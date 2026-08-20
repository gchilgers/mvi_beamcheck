import numpy as np

from pathlib import Path
import tomllib
from pydicom import dcmread

import pytest

from mvi_beamcheck import MVIBeamCheck
from mvi_beamcheck.beamcheck import FLATNESS_ROIS

def test_flatness_off_axis_rois_are_correctly_positioned():
    # --- locate project root ---
    root = Path(__file__).resolve().parents[1]


    # --- load config  ---
    with open(root / 'config' / 'example.toml', 'rb') as f:
        config = tomllib.load(f)

    # --- load RTImage ---
    ds = dcmread(root / 'tests' / 'data' / 'rtimg_test_pattern.dcm')

    # --- run beam check ---
    check = MVIBeamCheck(ds, config)

    # --- test ---
    assert check._measure_roi_response(
        FLATNESS_ROIS['D1']['offset_mm'],
        FLATNESS_ROIS['D1']['size_px']
    ) == pytest.approx(15000, abs=100)  # for taking rounding effect into account

    assert check._measure_roi_response(
        FLATNESS_ROIS['D2']['offset_mm'],
        FLATNESS_ROIS['D2']['size_px']
    ) == pytest.approx(30000, abs=100)  # for taking rounding effect into account

    assert check._measure_roi_response(
        FLATNESS_ROIS['D3']['offset_mm'],
        FLATNESS_ROIS['D3']['size_px']
    ) == pytest.approx(45000, abs=100)  # for taking rounding effect into account

    assert check._measure_roi_response(
        FLATNESS_ROIS['D4']['offset_mm'],
        FLATNESS_ROIS['D4']['size_px']
    ) == pytest.approx(60000, abs=100)  # for taking rounding effect into account

