"""
Contains the main computational class MVIBeamCheck. 

MVIBeamCheck reads an RTIMAGE converts pixel values to response values,
measures predefined output and flatness ROIs, computes output and beam
quality deviations, and exposes the results through BeamCheckResult.
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
    """
    Perform output and beam-quality analysis on an RTIMAGE.

    The analysis follows the ROI definitions described in the referenced
    publications and uses machine-specific parameters supplied
    through BeamCheckConfig.
    """    
    # --- construction / interface --- 
    def __init__(self, rtimage: Dataset, config: dict) -> None:
        self.rtimage = rtimage
        self.config = BeamCheckConfig.from_dict(config)
        
        self.timestamp = self._get_timestamp()
        self.response_matrix = self._compute_response_matrix()
        
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
        """
        Create an MVIBeamCheck instance from an RTIMAGE DICOM file.
        """
        return cls(dcmread(path), config)


    # --- metadata / preprocessing ---
    def _get_timestamp(self) -> datetime:
        """
        Construct an acquisition timestamp from AcquisitionDate and
        AcquisitionTime.

        Raises
        ------
        ValueError
            If either DICOM attribute is missing.
        """
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


    def _compute_response_matrix(self) -> np.ndarray:
        """
        Convert pixel values to detector response.
        
        Response is computed using the vendor pixel factor stored in DICOM
        tag (0021,1002). Vendor-masked saturated pixels are converted to NaN.
        """
        pixel_array = self.rtimage.pixel_array

        tag = self.rtimage.get((0x0021, 0x1002))
        if tag is None:
            raise ValueError('Missing pixel factor (required for response computation)')
        pixel_factor = float(tag.value)

        response_matrix = (2**16 - 1 - pixel_array) / pixel_factor

        # exclude saturated pixels (vendor-applied mask)
        response_matrix[pixel_array == (2**16 - 1)] = np.nan

        return response_matrix
          

    # --- ROI definition ---
    def _roi_offset_to_px(self, roi_offset_mm: tuple[float, float]) -> tuple[int, int]:
        """
        Convert an ROI offset in isocenter-plane millimetres to a pixel
        location in the response matrix.
    
        Offsets are projected from isocenter to the imager plane using the
        SAD and SID recorded in the RTIMAGE. The vendor-reported isocenter
        pixel coordinates are converted from the vendor's (u,v) 1-based
        convention to the internal (j,i) 0-based image convention.
        """

        # --- isocenter pixel vendor (u, v, 1-based) → internal (j, i, 0-based) ---
        iso_u_vendor_px, iso_v_vendor_px = self.config.imager.mean_isocenter_pixel
        iso_i_px = round(iso_v_vendor_px - 1)
        iso_j_px = round(iso_u_vendor_px - 1)
    
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
        offset_i_px = round((offset_v_mm * (SID_mm / SAD_mm)) / pixel_spacing_i)
        offset_j_px = round((offset_u_mm * (SID_mm / SAD_mm)) / pixel_spacing_j)
    
        # --- ROI center in px ---
        roi_center_i_px = iso_i_px - offset_i_px
        roi_center_j_px = iso_j_px + offset_j_px
    
        return (roi_center_i_px, roi_center_j_px)

    
    def _create_roi(self, roi_offset_mm: tuple[float, float], roi_size_px: tuple[int, int]) -> tuple[slice, slice]:
        # --- center position of the ROI in the response matrix ---
        center_i, center_j = self._roi_offset_to_px(roi_offset_mm)
    
        # --- ROI size in pixels: (u, v) -> (j, i) ---
        size_j, size_i = roi_size_px

        half_i = size_i // 2
        half_j = size_j // 2
      
        # --- construct slices ---
        slice_i = slice(center_i - half_i, center_i + half_i + 1)
        slice_j = slice(center_j - half_j, center_j + half_j + 1)
    
        return (slice_i, slice_j)  

    
    # --- extraction / measurement ---
    def _extract_roi(self, roi: tuple[slice, slice]) -> np.ndarray:
          return self.response_matrix[roi]

      
    def _measure_roi_response(self, roi_offset_mm: tuple[float, float], roi_size_px: tuple[int, int]) -> float:
        """
        Measure the mean response within an ROI.

        ROI responses are computed using np.mean(). Consequently, the presence
        of a NaN pixel within an ROI causes the ROI response to become NaN. While
        this is expected for intentionally vendor-masked regions, an unexpected
        NaN response may indicate a detector defect (e.g. a dead pixel) or another
        pixel-data integrity issue within the ROI.
        """
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
        """
        Return the analysis results as a BeamCheckResult instance.
        """
        return BeamCheckResult(
            timestamp = self.timestamp,
            output_response = float(self.output_response),
            output_deviation = float(self.output_deviation),
            flatness_responses = self.flatness_responses,
            flatness = float(self.flatness),
            beam_quality_deviation = float(self.beam_quality_deviation)
    )
