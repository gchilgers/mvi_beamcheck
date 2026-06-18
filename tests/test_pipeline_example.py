import pytest

from pathlib import Path
from pydicom import dcmread
import tomllib

from mvi_beamcheck import MVIBeamCheck

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_OUTPUT_RESPONSE = 2274423.163
EXPECTED_OUTPUT_DEVIATION = 0.34

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

    assert check.output_response == pytest.approx(EXPECTED_OUTPUT_RESPONSE, abs=0.1)
    assert check.output_deviation == pytest.approx(EXPECTED_OUTPUT_DEVIATION, abs=0.01)

