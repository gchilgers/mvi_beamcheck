from pathlib import Path
from pydicom import dcmread

def test_example_rtimage_can_be_loaded():
    root = Path(__file__).resolve().parents[1]
    path = root / 'tests' / 'data' / 'rtimg_example_anon.dcm'
    
    ds = dcmread(path)

    assert ds is not None
