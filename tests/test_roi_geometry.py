"""
Tests for flatness ROI geometry.

The synthetic RTIMAGE test pattern is constructed such that:
- The CAX region consists entirely of saturated pixels (65535), which are
  converted to NaN in the response matrix.
- The off-axis regions D1-D4 are encoded to yield exact response values of
  10000, 20000, 30000, and 40000, respectively.
- The pixel factor (0021,1002) is set to 1.0 to avoid scaling and potential
  floating-point rounding effects, allowing exact equality assertions.

These tests verify:
- Correct assignment of the off-axis ROIs (D1-D4) to the intended quadrants.
- Complete overlap of the CAX ROI with a central masked region of identical
  dimensions.
- Identical ROI dimensions for the CAX and off-axis flatness ROIs.

These tests do not verify:
- The exact pixel coordinates of the off-axis ROI centres.
"""

import numpy as np

from pathlib import Path
import tomllib
from pydicom import dcmread

from mvi_beamcheck import MVIBeamCheck
from mvi_beamcheck.beamcheck import FLATNESS_ROIS

import pytest


@pytest.fixture
def check():
    # --- locate project root ---
    root = Path(__file__).resolve().parents[1]


    # --- load config  ---
    with open(root / 'config' / 'example.toml', 'rb') as f:
        config = tomllib.load(f)

    # --- load RTImage ---
    ds = dcmread(root / 'tests' / 'data' / 'rtimg_test_pattern.dcm')

    # --- run beam check ---
    return MVIBeamCheck(ds, config)


def test_flatness_cax_roi_is_correctly_positioned(check):
    # The CAX region of the synthetic RTIMAGE is filled with saturated pixels,
    # which are masked to NaN during response computation.
    response = check._measure_roi_response(
        FLATNESS_ROIS['CAX']['offset_mm'],
        FLATNESS_ROIS['CAX']['size_px']
    )

    assert np.isnan(response), f'Expected NaN, got {response}' 


def test_flatness_off_axis_rois_are_correctly_positioned(check):
    # The synthetic RTIMAGE contains uniform regions with predefined response
    # values. If each ROI is positioned correctly, the ROI mean equals the
    # corresponding encoded value exactly.
    for roi_name, expected in [
        ('D1', 10000),
        ('D2', 20000),
        ('D3', 30000),
        ('D4', 40000)
    ]:       
        response = check._measure_roi_response(
            FLATNESS_ROIS[roi_name]['offset_mm'],
            FLATNESS_ROIS[roi_name]['size_px']
        )

        assert response == expected, f'Expected {expected} for ROI {roi_name}, got {response}'


def test_flatness_rois_have_same_shape(check):
    cax_roi = check._extract_roi(
        check._create_roi(
            FLATNESS_ROIS['CAX']['offset_mm'],
            FLATNESS_ROIS['CAX']['size_px']
        )
    )

    # The synthetic test pattern is constructed such that the CAX ROI
    # is completely filled with NaN values.
    assert np.all(np.isnan(cax_roi))

    cax_shape = cax_roi.shape

    for roi_name in ['D1', 'D2', 'D3', 'D4']:
        shape = check._extract_roi(
            check._create_roi(
                FLATNESS_ROIS[roi_name]['offset_mm'],
                FLATNESS_ROIS[roi_name]['size_px']
            )
        ).shape

        assert shape == cax_shape, (
            f'Expected shape {cax_shape} for ROI {roi_name}, got {shape}'
        )