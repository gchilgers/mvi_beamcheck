from pathlib import Path
import tomllib
from pydicom import dcmread
import pytest
from mvi_beamcheck import MVIBeamCheck


def test_missing_acquisition_date_raises():
    root = Path(__file__).resolve().parents[1]

    # --- load config ---
    with open (root / 'config' / 'example.toml', 'rb') as f:
        config = tomllib.load(f)

    # --- load RTIMAGE ---
    ds = dcmread(root / 'tests' / 'data' / 'rtimg_example_anon.dcm')

    # --- remove field ---
    del ds.AcquisitionDate

    # --- check error ---
    with pytest.raises(ValueError, match='AcquisitionDate'):
        MVIBeamCheck(ds, config)


def test_missing_acquisition_time_raises():
    root = Path(__file__).resolve().parents[1]

    # --- load config ---
    with open (root / 'config' / 'example.toml', 'rb') as f:
        config = tomllib.load(f)

    # --- load RTIMAGE ---
    ds = dcmread(root / 'tests' / 'data' / 'rtimg_example_anon.dcm')

    # --- remove field ---
    del ds.AcquisitionTime

    # --- check error ---
    with pytest.raises(ValueError, match='AcquisitionTime'):
        MVIBeamCheck(ds, config)


def test_missing_pixel_factor_raises():
    root = Path(__file__).resolve().parents[1]

    # --- load config ---
    with open(root / 'config' / 'example.toml', 'rb') as f:
        config = tomllib.load(f)

    # --- load DICOM ---
    ds = dcmread(root / 'tests' / 'data' / 'rtimg_example_anon.dcm')

    # --- remove private tag ---
    ds.pop((0x0021, 0x1002), None)

    # --- check error ---
    with pytest.raises(ValueError, match='pixel factor'):
        MVIBeamCheck(ds, config)


def test_missing_pixel_spacing_raises():
    root = Path(__file__).resolve().parents[1]

    # --- load config ---
    with open(root / 'config' / 'example.toml', 'rb') as f:
        config = tomllib.load(f)

    # --- load DICOM ---
    ds = dcmread(root / 'tests' / 'data' / 'rtimg_example_anon.dcm')

    # --- remove field ---
    del ds.ImagePlanePixelSpacing

    # --- check error ---
    with pytest.raises(ValueError, match='ImagePlanePixelSpacing'):
        MVIBeamCheck(ds, config)


def test_missing_rtimagesid_raises():
    root = Path(__file__).resolve().parents[1]

    # --- load config ---
    with open(root / 'config' / 'example.toml', 'rb') as f:
        config = tomllib.load(f)

    # --- load DICOM ---
    ds = dcmread(root / 'tests' / 'data' / 'rtimg_example_anon.dcm')

    # --- remove field ---
    del ds.RTImageSID

    # --- check error ---
    with pytest.raises(ValueError, match='RTImageSID'):
        MVIBeamCheck(ds, config)


def test_missing_radiationmachinesad_raises():
    root = Path(__file__).resolve().parents[1]

    # --- load config ---
    with open(root / 'config' / 'example.toml', 'rb') as f:
        config = tomllib.load(f)

    # --- load DICOM ---
    ds = dcmread(root / 'tests' / 'data' / 'rtimg_example_anon.dcm')

    # --- remove field ---
    del ds.RadiationMachineSAD

    # --- check error ---
    with pytest.raises(ValueError, match='RadiationMachineSAD'):
        MVIBeamCheck(ds, config)







