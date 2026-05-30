from pathlib import Path
from pydicom import dcmread

def test_dicom_can_be_loaded():
    dcm_path = Path(__file__).parent / 'data' / 'rtimg_example_anon.dcm'
    
    ds = dcmread(dcm_path)

    assert ds is not None
