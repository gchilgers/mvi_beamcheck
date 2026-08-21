"""
Tests for the end-to-end beam-check pipeline.

These tests verify that:
- The example RTIMAGE and configuration can be processed successfully.
- The computed output response and output deviation match reference values.
- The computed flatness responses, flatness, and beam-quality deviation match
  reference values.
"""

import pytest

from pathlib import Path
from pydicom import dcmread
import tomllib

from mvi_beamcheck import MVIBeamCheck

ROOT = Path(__file__).resolve().parents[1]

# --- expected output metrics ---
EXPECTED_OUTPUT_RESPONSE = 2274423.162674
EXPECTED_OUTPUT_DEVIATION = 0.34

# --- expected flatness metrics ---
EXPECTED_FLATNESS_RESPONSE_CAX = 2279190.438805
EXPECTED_FLATNESS_RESPONSE_D1 = 2139674.321530
EXPECTED_FLATNESS_RESPONSE_D2 = 2161641.444203
EXPECTED_FLATNESS_RESPONSE_D3 = 2154864.816918 
EXPECTED_FLATNESS_RESPONSE_D4 = 2135946.821430
EXPECTED_FLATNESS = 0.942454

# --- expected beam quality metric ---
EXPECTED_BEAM_QUALITY_DEVIATION = 0.45

def load_example_rtimage():
    path = ROOT / 'tests' / 'data' / 'rtimg_example_anon.dcm'
    return dcmread(path)


def load_example_config_dict():
    path = ROOT / 'config' / 'example.toml'
    with open(path, 'rb') as f:
        return tomllib.load(f)


def test_example_input_is_valid():
    ds = load_example_rtimage()
    config_dict = load_example_config_dict()
    MVIBeamCheck(ds, config_dict)


def test_output_deviation_example_image():
    ds = load_example_rtimage()
    config_dict = load_example_config_dict()

    check = MVIBeamCheck(ds, config_dict)
    result = check.result()

    assert result.output_response == pytest.approx(EXPECTED_OUTPUT_RESPONSE, abs=1e-6)
    assert result.output_deviation == pytest.approx(EXPECTED_OUTPUT_DEVIATION, abs=1e-2)


def test_beam_quality_deviation_example_image():
    ds = load_example_rtimage()
    config_dict = load_example_config_dict()

    check = MVIBeamCheck(ds, config_dict)
    result = check.result()

    assert result.flatness_responses['CAX'] == pytest.approx(EXPECTED_FLATNESS_RESPONSE_CAX, abs=1e-6)
    assert result.flatness_responses['D1'] == pytest.approx(EXPECTED_FLATNESS_RESPONSE_D1, abs=1e-6)
    assert result.flatness_responses['D2'] == pytest.approx(EXPECTED_FLATNESS_RESPONSE_D2, abs=1e-6)
    assert result.flatness_responses['D3'] == pytest.approx(EXPECTED_FLATNESS_RESPONSE_D3, abs=1e-6)
    assert result.flatness_responses['D4'] == pytest.approx(EXPECTED_FLATNESS_RESPONSE_D4, abs=1e-6)

    assert result.flatness == pytest.approx(EXPECTED_FLATNESS, abs=1e-6)
    assert result.beam_quality_deviation == pytest.approx(EXPECTED_BEAM_QUALITY_DEVIATION, abs=1e-2)
        
        
