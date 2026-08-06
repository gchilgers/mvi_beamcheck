"""
Contains the main computational class MVIBeamCheck. This class reads the DICOM 
image (via from_rtimage), calls the image processing helpers, computes output and 
beam quality deviations, and returns a BeamCheckResult.
"""
from pathlib import Path
import numpy as np
from datetime import datetime
from pydicom import Dataset, dcmread

from .config import BeamCheckConfig
from .result import BeamCheckResult
from .formulas import compute_output_deviation, compute_flatness, compute_beam_quality_deviation

# --- ROI definitions (fixed method specification) ---
ROIS = {
    'output': {'offset_mm': (0, 0), 'size_px': (101, 101)},
    'flatness_cax': {'offset_mm': (0, 0), 'size_px': (47, 21)},
    'flatness_D1': {'offset_mm': (0.6*90, 0.6*40), 'size_px': (47, 21)},
    'flatness_D2': {'offset_mm': (-0.6*90, 0.6*40), 'size_px': (47, 21)},
    'flatness_D3': {'offset_mm': (-0.6*90, -0.6*40), 'size_px': (47, 21)},
    'flatness_D4': {'offset_mm': (0.6*90, -0.6*40), 'size_px': (47, 21)},
}

class MVIBeamCheck():
    
    # --- construction / interface --- 
    def __init__(self, rtimage: Dataset, config: dict) -> None:
        self.rtimage = rtimage
        self.config = BeamCheckConfig.from_dict(config)
        
        self.timestamp = self._get_timestamp()
        self.response = self._compute_response()
        
        self.output_response = self._measure_roi_response(ROIS['output']['offset_mm'], ROIS['output']['size_px'])
        self.output_deviation = self._compute_output_deviation()

        self.flatness = self._compute_flatness()
        self.beam_quality_deviation = self._compute_beam_quality_deviation()
                
    @classmethod
    def from_rtimage(cls, path: Path, config: dict) -> 'MVIBeamCheck':
        return cls(dcmread(path), config)

    # --- metadata / preprocessing ---
    def _get_timestamp(self) -> datetime:
        acquisition_date = getattr(self.rtimage, 'AcquisitionDate', None)
        if acquisition_date is None:
            raise ValueError('Missing AcquisitionDate (required for timestamp)')
        acquisition_date = str(acquisition_date)

        acquisition_time = getattr(self.rtimage, 'AcquisitionTime', None)
        if acquisition_time is None:
            raise ValueError('Missing AcquisitionTime (required for timestamp)')
        acquisition_time = str(acquisition_time)

        timestamp_as_str = (acquisition_date + acquisition_time).replace('.', '')

        return datetime.strptime(timestamp_as_str, '%Y%m%d%H%M%S%f')

    def _compute_response(self) -> np.ndarray:
        pixel_array = self.rtimage.pixel_array

        tag = self.rtimage.get((0x0021, 0x1002))
        if tag is None:
            raise ValueError('Missing pixel factor (required for response computation)')
        pixel_factor = float(tag.value)

        response = (2**16 - 1 - pixel_array) / pixel_factor

        # exclude saturated pixels (vendor-applied mask)
        response[pixel_array == (2**16 - 1)] = np.nan

        return response
          

    # --- ROI definition ---
    def _roi_offset_to_px(self, roi_offset_mm: tuple[float, float]) -> tuple[int, int]:
        # --- isocenter pixel vendor (x, y, 1-based) → internal (i, j, 0-based) ---
        iso_x_vendor_px, iso_y_vendor_px = self.config.imager.mean_isocenter_pixel
        iso_i_px = int(iso_y_vendor_px - 1)
        iso_j_px = int(iso_x_vendor_px - 1)
    
        # --- pixel spacing (mm per pixel) ---
        pixel_spacing = getattr(self.rtimage, 'ImagePlanePixelSpacing', None)
        if pixel_spacing is None:
            raise ValueError('Missing ImagePlanePixelSpacing (required for ROI computation)')
        pixel_spacing_i = float(pixel_spacing[0])
        pixel_spacing_j = float(pixel_spacing[1])

        # --- geometry ---
        SID_mm = getattr(self.rtimage, 'RTImageSID', None)  # source-to-imager distance
        if SID_mm is None:
            raise ValueError('Missing RTImageSID (required for ROI computation)')
        SID_mm = float(SID_mm)

        SAD_mm = getattr(self.rtimage, 'RadiationMachineSAD', None)  # source-to-axis distance
        if SAD_mm is None:
            raise ValueError('Missing RadiationMachineSAD (required for ROI computation)')
        SAD_mm = float(SAD_mm)
    
        # --- offsets (mm) ---
        offset_i_mm, offset_j_mm = roi_offset_mm
    
        # --- convert mm → pixels  ---
        offset_i_px = int((offset_i_mm * (SID_mm / SAD_mm)) / pixel_spacing_i)
        offset_j_px = int((offset_j_mm * (SID_mm / SAD_mm)) / pixel_spacing_j)
    
        # --- ROI center in px ---
        roi_center_i_px = iso_i_px + offset_i_px
        roi_center_j_px = iso_j_px + offset_j_px
    
        return (roi_center_i_px, roi_center_j_px)
    
    def _create_roi(self, roi_offset_mm: tuple[float, float], roi_size_px: tuple[int, int]) -> tuple[slice, slice]:
        # --- center position in pixels ---
        center_i, center_j = self._roi_offset_to_px(roi_offset_mm)
    
        # --- ROI size ---
        size_i, size_j = roi_size_px
        half_i = size_i // 2
        half_j = size_j // 2
    
        # --- construct slices ---
        slice_i = slice(center_i - half_i, center_i + half_i + 1)
        slice_j = slice(center_j - half_j, center_j + half_j + 1)
    
        return (slice_i, slice_j)  
    
    # --- extraction / measurement ---
    def _extract_roi(self, roi: tuple[slice, slice]) -> np.ndarray:
        return self.response[roi]
      
    def _measure_roi_response(self, roi_offset_mm: tuple[float, float], roi_size_px: tuple[int, int]) -> float:
        roi = self._create_roi(roi_offset_mm, roi_size_px)
        return np.mean(self._extract_roi(roi))
    
    def _compute_output_deviation(self) -> float:
        crosscal_response = self.config.output.crosscal_response
        crosscal_output = self.config.output.crosscal_output
        target_output = self.config.output.target_output
        return compute_output_deviation(self.output_response, crosscal_response, crosscal_output, target_output)

    def _compute_flatness(self) -> float:
        flatness_responses = {
            name: self._measure_roi_response(roi['offset_mm'], roi['size_px'])
            for name, roi in ROIS.items()
            if name.startswith('flatness_')
        }
        return compute_flatness(flatness_responses)

    def _compute_beam_quality_deviation(self) -> float:
        reference_flatness = self.config.beam_quality.reference_flatness
        beta = self.config.beam_quality.beta
        return compute_beam_quality_deviation(self.flatness, reference_flatness, beta)

    # --- results / API ---
    def result(self) -> BeamCheckResult:
        return BeamCheckResult(
            timestamp = self.timestamp,
            output_response = float(self.output_response),
            output_deviation = float(self.output_deviation),
            flatness = float(self.flatness),
            beam_quality_deviation = float(self.beam_quality_deviation)
    )

    def __repr__(self):
        result = self.result()
        return (
            f'MVIBeamCheck('
            f'timestamp={result.timestamp.isoformat()}, '
            f'output_response={result.output_response:.3f}, '
            f'output_deviation={result.output_deviation:.2f}%) ',
            f'flatness={result.flatness:.3f}, '
            f'beam_quality_deviation={result.beam_quality_deviation:.2f}%)'
    )
