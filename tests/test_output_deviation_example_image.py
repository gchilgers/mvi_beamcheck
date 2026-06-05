from pathlib import Path
import tomllib
from pydicom import dcmread
import pytest

from mvi_beamcheck import MVIBeamCheck

EXPECTED_OUTPUT_RESPONSE = 2274423.163
EXPECTED_OUTPUT_DEVIATION = 0.34

def test_output_deviation_example_image():
    # --- load config and dcm ---
    root = Path(__file__).resolve().parents[1]

    config_path = root / 'config' / 'example.toml'
    with open(config_path, 'rb') as f:
        config = tomllib.load(f)
  
    dcm_path = root / 'tests' / 'data' / 'rtimg_example_anon.dcm'
    ds = dcmread(dcm_path)

    # --- perform check ---
    check = MVIBeamCheck(ds, config)
    assert check.output_response == pytest.approx(EXPECTED_OUTPUT_RESPONSE, abs=0.1), \
        f'Output rsponse mismatch: got {check.output_response: .1f}, expected {EXPECTED_OUTPUT_RESPONSE:.1f}'
    assert check.output_deviation == pytest.approx(EXPECTED_OUTPUT_DEVIATION, abs=0.01), \
        f'Output deviation mismatch: got {check.output_deviation:.2f} %, expected {EXPECTED_OUTPUT_DEVIATION:.2f} %'
