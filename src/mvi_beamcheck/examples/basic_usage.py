"""
Example script: basic usage of MVIBeamCheck for a single RTImage.

Processes a single RTImage dataset and prints result to the console.

Notes:
- The config file in /config is provided as an example.
- Replace it with a system-specific configuration if needed.
"""

from pathlib import Path
import tomllib
from pydicom import dcmread

from mvi_beamcheck import MVIBeamCheck


# --- locate project root ---
root = Path(__file__).resolve().parents[1]


# --- load config (replace with your own) ---
with open(root / 'config' / 'example.toml', 'rb') as f:
    config = tomllib.load(f)


# --- load RTImage ---
ds = dcmread(root / 'tests' / 'data' / 'rtimg_example_anon.dcm')


# --- run beam check ---
check = MVIBeamCheck(ds, config)
result = check.result()


# --- print result ---
print(result)
