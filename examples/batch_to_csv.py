"""
Example script: batch processing of RTImage DICOM files.

Processes multiple RTImage datasets and exports results to CSV.

Usage:
    python batch_to_csv.py <data_dir>

Notes:
- The config file in /config is provided as an example.
- Replace it with a system-specific configuration if needed.
"""

from pathlib import Path
import sys
import csv
import tomllib
from pydicom import dcmread

from mvi_beamcheck import MVIBeamCheck


# --- locate project root ---
root = Path(__file__).resolve().parents[1]


# --- parse CLI arguments ---
if len(sys.argv) != 2:
    print('Usage: python batch_to_csv.py <data_dir>')
    sys.exit(1)

data_dir = Path(sys.argv[1])

if not data_dir.exists():
    raise ValueError(f'Data directory does not exist {data_dir}')

# --- load config (replace with your own) ---
with open(root / 'config' / 'example.toml', 'rb') as f:
    config = tomllib.load(f)


# --- output CSV file ---
output_csv = data_dir / 'output.csv'


# --- process and write results ---
with open(output_csv, 'w', newline='') as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            'filename',
            'timestamp',
            'output_response',
            'output_deviation_percent',
        ],
    )

    writer.writeheader()

    for path in sorted(data_dir.glob('*.dcm')):
        ds = dcmread(path)

        check = MVIBeamCheck(ds, config)
        result = check.result()

        row = {'filename': path.name, **result.to_dict()}

        writer.writerow(row)


print(f'\nBatch processing complete. Results written to: {output_csv}')