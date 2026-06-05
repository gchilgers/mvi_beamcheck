from pathlib import Path
import tomllib
from pydicom import dcmread

from mvi_beamcheck import MVIBeamCheck

root = Path(__file__).resolve().parents[1]

# --- load config ---
with open(root / 'config' / 'example.toml', 'rb') as f:
    config = tomllib.load(f)

# --- load DICOM ---
ds = dcmread(root / 'tests' / 'data' / 'rtimg_example_anon.dcm')

# --- run analysis ---
check = MVIBeamCheck(ds, config)
print(check)

# --- direct access ---
# print(f'Output response: {result.output_response:.3f}')
# print(f'Output deviation (%): {result.output_deviation:.1f}')

# --- result interface ---
result = check.result()
print(result)



