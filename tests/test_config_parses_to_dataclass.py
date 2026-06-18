from pathlib import Path
import tomllib

from mvi_beamcheck.config import BeamCheckConfig

def test_example_config_can_be_loaded():
    # --- locate file ---
    root = Path(__file__).resolve().parents[1]
    path = root / 'config' / 'example.toml'
    
    # --- read TOML ---
    with open(path, 'rb') as f:
        config_dict = tomllib.load(f)

    
    # --- convert to dataclass ---
    config = BeamCheckConfig.from_dict(config_dict)

    # --- verify config is usable --  
    assert isinstance(config, BeamCheckConfig)