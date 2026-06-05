"""
Contains the main computational class MVIBeamCheck. This class reads the DICOM 
image (via from_dicom), calls the image processing helpers, computes output and 
beam quality deviations, and returns a BeamCheckResult.
"""
from pathlib import Path
import numpy as np
from datetime import datetime
from pydicom import Dataset, dcmread

from .results import BeamCheckResult

# --- ROI definitions (fixed method specification) ---
ROIS = {
    'output': {'offset_mm': (0, 0), 'size_px': (101, 101)},   
}

class MVIBeamCheck():
    
    # --- construction / interface --- 
    def __init__(self, rtimage: Dataset, config: dict):
        self.rtimage = rtimage
        self.config = config
        
        self.timestamp = self._get_timestamp()
        self.response = self._compute_response()
        
        self.output_response = self._measure_roi_response(ROIS['output']['offset_mm'], ROIS['output']['size_px'])
        self.output_deviation = self._compute_output_deviation()
                
    @classmethod
    def from_dcm(cls, path: Path, config: dict):
        return cls(dcmread(path), config)

    # --- metadata / preprocessing ---
    def _get_timestamp(self):
        date_as_str = self.rtimage.AcquisitionDate
        time_as_str = self.rtimage.AcquisitionTime
        timestamp_as_str = (date_as_str + time_as_str).replace('.', '')
        return datetime.strptime(timestamp_as_str, '%Y%m%d%H%M%S%f')

    def _compute_response(self):
        pixel_array = self.rtimage.pixel_array
        pixel_factor = float(self.rtimage[0x0021, 0x1002].value)

        response = (2**16 - 1 - pixel_array) / pixel_factor


        # exclude saturated pixels (vendor-applied mask)
        response[pixel_array == (2**16 - 1)] = np.nan

        return response

    # --- ROI definition ---
    def _roi_offset_to_px(self, roi_offset_mm: tuple[float, float]):
        # --- isocenter pixel vendor (x, y, 1-based) → internal (i, j, 0-based) ---
        iso_x_vendor_px, iso_y_vendor_px = self.config['system']['imager']['mean_isocenter_pixel']
    
        iso_i_px = int(iso_y_vendor_px - 1)
        iso_j_px = int(iso_x_vendor_px - 1)
    
        # --- pixel spacing (mm per pixel) ---
        spacing_i_mm_per_px, spacing_j_mm_per_px = self.rtimage.ImagePlanePixelSpacing
    
        # --- geometry ---
        SID_mm = float(self.rtimage.RTImageSID)  # source-to-imager distance
        SAD_mm = float(self.rtimage.RadiationMachineSAD)  # source-to-axis distance
    
        # --- offsets (mm) ---
        offset_i_mm, offset_j_mm = roi_offset_mm
    
        # --- convert mm → pixels  ---
        offset_i_px = int((offset_i_mm * (SID_mm / SAD_mm)) / spacing_i_mm_per_px)
        offset_j_px = int((offset_j_mm * (SID_mm / SAD_mm)) / spacing_j_mm_per_px)
    
        # --- ROI center in px ---
        roi_center_i_px = iso_i_px + offset_i_px
        roi_center_j_px = iso_j_px + offset_j_px
    
        return (roi_center_i_px, roi_center_j_px)
    
    def _create_roi(self, roi_offset_mm: tuple[float, float], roi_size_px: tuple[int, int]):
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
    def _extract_roi(self, roi):
        return self.response[roi]
      
    def _measure_roi_response(self, roi_offset_mm: tuple[float, float], roi_size_px: tuple[int, int]):
        roi = self._create_roi(roi_offset_mm, roi_size_px)
        return np.mean(self._extract_roi(roi))
    
    def _compute_output_deviation(self):
        crosscal_response = self.config['output']['crosscal_response']
        crosscal_output = self.config['output']['crosscal_output']
        output = self.output_response / crosscal_response * crosscal_output
        target_output = self.config['output']['target_output']
        return (output - target_output) / target_output * 100
    
    # --- results / API ---
    def result(self) -> BeamCheckResult:
        return BeamCheckResult(
            output_response = float(self.output_response),
            output_deviation = float(self.output_deviation)
    )

    def __repr__(self):
        return (
            f"MVIBeamCheck("
            f"output_response={self.output_response:.3f}, "
            f"output_deviation={self.output_deviation:.2f}%)"
    )
