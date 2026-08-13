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

# --- Output ROI: Hilgers et al. 2023 (DOI: 10.1016/j.phro.2023.100411) ---
OUTPUT_ROI = {'offset_mm': (0, 0),             
              'size_px': (101, 101),
}

# --- Flatness ROIs: Hilgers et al. 2026 (DOI: 10.1016/j.phro.2026.100930) ---
FLATNESS_ROIS = {
    'CAX': {'offset_mm': (0, 0), 
            'size_px': (47, 21)
    }, 
    'D1': {'offset_mm': (0.6*90, 0.6*40), 
           'size_px': (47, 21)
    },
    'D2': {'offset_mm': (-0.6*90, 0.6*40), 
           'size_px': (47, 21)
    },
    'D3': {'offset_mm': (-0.6*90, -0.6*40), 
           'size_px': (47, 21)
    },
    'D4': {'offset_mm': (0.6*90, -0.6*40),
           'size_px': (47, 21)
    },
}

class MVIBeamCheck():
    
    # --- construction / interface --- 
    def __init__(self, rtimage: Dataset, config: dict) -> None:
        self.rtimage = rtimage
        self.config = BeamCheckConfig.from_dict(config)
        
        self.timestamp = self._get_timestamp()
        self.response = self._compute_response()
        
        self.output_response = self._measure_roi_response(OUTPUT_ROI['offset_mm'], OUTPUT_ROI['size_px'])
        self.output_deviation = self._compute_output_deviation()
        self.flatness_responses = {
            name: self._measure_roi_response(roi['offset_mm'], roi['size_px'])
            for name, roi in FLATNESS_ROIS.items()
        }

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
        """
        Convert an ROI offset in imager coordinates to image-array indices.

        Coordinate systems:
        - (u, v): imager coordinates in the detector plane, expressed either
        in millimetres relative to isocenter or in image pixels.
        - (i, j): NumPy array indices, where i is the row index and j is the
        column index (0-based).

        Pixels are treated as discrete detector elements rather than sub-pixel
        locations. Vendor mean isocenter pixel is provided as 1-based (u, v)
        pixel coordinates and are converted to internal 0-based (i, j) indices.
        """
        # --- isocenter pixel vendor (u, v, 1-based) → internal (i, j, 0-based) ---
        iso_u_vendor_px, iso_v_vendor_px = self.config.imager.mean_isocenter_pixel
        iso_i_px = int(iso_v_vendor_px - 1)
        iso_j_px = int(iso_u_vendor_px - 1)
    
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
        offset_u_mm, offset_v_mm = roi_offset_mm
    
        # --- convert mm → pixels  ---
        offset_i_px = int((offset_v_mm * (SID_mm / SAD_mm)) / pixel_spacing_i)
        offset_j_px = int((offset_u_mm * (SID_mm / SAD_mm)) / pixel_spacing_j)
    
        # --- ROI center in px ---
        roi_center_i_px = iso_i_px - offset_i_px
        roi_center_j_px = iso_j_px + offset_j_px
    
        return (roi_center_i_px, roi_center_j_px)
    
    def _create_roi(self, roi_offset_mm: tuple[float, float], roi_size_px: tuple[int, int]) -> tuple[slice, slice]:
        # --- center position in pixels ---
        center_i, center_j = self._roi_offset_to_px(roi_offset_mm)
    
        # --- ROI size ---
        size_j, size_i = roi_size_px

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
        return compute_flatness(
            cax_response = self.flatness_responses['CAX'],
            off_axis_responses = [
                self.flatness_responses['D1'], 
                self.flatness_responses['D2'], 
                self.flatness_responses['D3'], 
                self.flatness_responses['D4'],
            ]
        )
        
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
            flatness_responses = self.flatness_responses,
            flatness = float(self.flatness),
            beam_quality_deviation = float(self.beam_quality_deviation)
    )
