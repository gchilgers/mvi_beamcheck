import numpy as np

from pathlib import Path
import tomllib
from pydicom import dcmread

from mvi_beamcheck import MVIBeamCheck
from mvi_beamcheck.beamcheck import FLATNESS_ROIS

def test_flatness_rois_are_correctly_positioned():
    # --- locate project root ---
    root = Path(__file__).resolve().parents[1]


    # --- load config  ---
    with open(root / 'config' / 'example.toml', 'rb') as f:
        config = tomllib.load(f)

    # --- load RTImage ---
    ds = dcmread(root / 'tests' / 'data' / 'rtimg_example_anon.dcm')

    # --- run beam check ---
    check = MVIBeamCheck(ds, config)

    # --- create synthetic image ---
    response = check.response.copy()
    synthetic = np.full_like(response, np.nan)

    # --- isocenter pixel vendor (x, y, 1-based) → internal (i, j, 0-based) ---
    iso_x_vendor_px, iso_y_vendor_px = check.config.imager.mean_isocenter_pixel
    iso_i_px = int(iso_y_vendor_px - 1)
    iso_j_px = int(iso_x_vendor_px - 1)

    # --- adjust synthetic image ---
    n_rows, n_cols = synthetic.shape
    synthetic[0:iso_i_px, iso_j_px:n_cols] = 1000       # D1 quadrant (upper right)
    synthetic[0:iso_i_px, 0:iso_j_px] = 2000            # D2 quadrant (upper left)
    synthetic[iso_i_px:n_rows, 0:iso_j_px] = 3000       # D3 quadrant (lower left)
    synthetic[iso_i_px:n_rows, iso_j_px:n_cols] = 4000  # D4 quadrant (lower right)
    synthetic[iso_i_px, :] = np.nan                     # isocenter row
    synthetic[:, iso_j_px] = np.nan                     # isocenter col
    synthetic[np.isnan(response)] = np.nan              # restore original vendor mask

    # --- overwrite response with synthetic image ---
    check.response = synthetic

    # --- test ---
    assert check._measure_roi_response(
        FLATNESS_ROIS['D1']['offset_mm'],
        FLATNESS_ROIS['D1']['size_px']
    ) == 1000

    assert check._measure_roi_response(
        FLATNESS_ROIS['D2']['offset_mm'],
        FLATNESS_ROIS['D2']['size_px']
    ) == 2000

    assert check._measure_roi_response(
        FLATNESS_ROIS['D3']['offset_mm'],
        FLATNESS_ROIS['D3']['size_px']
    ) == 3000

    assert check._measure_roi_response(
        FLATNESS_ROIS['D4']['offset_mm'],
        FLATNESS_ROIS['D4']['size_px']
    ) == 4000