import pytest
from pathlib import Path
import tomllib
from pydicom import dcmread
import copy
from mvi_beamcheck import MVIBeamCheck

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture
def config():
    with open(ROOT / 'config' / 'example.toml', 'rb') as f:
        return tomllib.load(f)

@pytest.fixture
def rtimage():
    return dcmread(ROOT / 'tests' / 'data' / 'rtimg_example_anon.dcm')

def test_missing_acquisition_date_raises(rtimage, config):
    ds = copy.deepcopy(rtimage)
    del ds.AcquisitionDate
    with pytest.raises(ValueError, match='AcquisitionDate'):
        MVIBeamCheck(ds, config)

def test_missing_acquisition_time_raises(rtimage, config):
    ds = copy.deepcopy(rtimage)
    del ds.AcquisitionTime
    with pytest.raises(ValueError, match='AcquisitionTime'):
        MVIBeamCheck(ds, config)

def test_missing_pixel_factor_raises(rtimage, config):
    ds = copy.deepcopy(rtimage)
    ds.pop((0x0021, 0x1002), None)
    with pytest.raises(ValueError, match='pixel factor'):
        MVIBeamCheck(ds, config)

def test_missing_pixel_spacing_raises(rtimage, config):
    ds = copy.deepcopy(rtimage)
    del ds.ImagePlanePixelSpacing
    with pytest.raises(ValueError, match='ImagePlanePixelSpacing'):
        MVIBeamCheck(ds, config)

def test_missing_rtimagesid_raises(rtimage, config):
    ds = copy.deepcopy(rtimage)
    del ds.RTImageSID
    with pytest.raises(ValueError, match='RTImageSID'):
        MVIBeamCheck(ds, config)

def test_missing_radiationmachinesad_raises(rtimage, config):
    ds = copy.deepcopy(rtimage)
    del ds.RadiationMachineSAD
    with pytest.raises(ValueError, match='RadiationMachineSAD'):
        MVIBeamCheck(ds, config)