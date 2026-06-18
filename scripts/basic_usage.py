from pathlib import Path
import tomllib
from pydicom import dcmread

from mvi_beamcheck import MVIBeamCheck

# --- locate project root ---
root = Path(__file__).resolve().parents[1]

# --- load config ---
with open(root / 'config' / 'example.toml', 'rb') as f:
    config = tomllib.load(f)

# --- load RTImage ---
ds = dcmread(root / 'tests' / 'data' / 'rtimg_example_anon.dcm')

# --- run beam check ---
check = MVIBeamCheck(ds, config)

# --- retrieve results ---
result = check.result()

# --- print key outputs ---
print('\nBeam check results:')
print(f'Output response: {result.output_response:.1f}')
print(f'Output deviation: {result.output_deviation:.2f} %')