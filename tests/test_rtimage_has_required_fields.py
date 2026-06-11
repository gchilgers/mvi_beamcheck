from pathlib import Path
from pydicom import dcmread

def test_example_rtimage_has_required_fields():
    root = Path(__file__).resolve().parents[1]
    path = root / 'tests' / 'data' / 'rtimg_example_anon.dcm'
    
    ds = dcmread(path)

    # --- response ---
    assert hasattr(ds, 'pixel_array'), 'Missing pixel_array'
    assert ds.get((0x0021, 0x1002)) is not None, 'Missing pixel factor (0021,1002)'

    # --- timestamp ---
    assert hasattr(ds, 'AcquisitionDate'), 'Missing AcquisitionDate'
    assert hasattr(ds, 'AcquisitionTime'), 'Missing AcquisitionTime'

    # --- spacing ---
    assert hasattr(ds, 'ImagePlanePixelSpacing'), 'Missing ImagePlanePixelSpacing'

    # --- geometry ---
    assert hasattr(ds, 'RTImageSID'), 'Missing RTImageSID'
    assert hasattr(ds, 'RadiationMachineSAD'), 'Missing RadiationMachineSAD'


