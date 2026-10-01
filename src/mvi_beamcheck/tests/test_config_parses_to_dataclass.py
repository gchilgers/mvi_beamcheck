"""
Test for configuration parsing.

This test verifies that the example TOML configuration can be parsed into a
BeamCheckConfig dataclass and serves as a guard against schema changes that
would make the distributed example configuration invalid.
"""

from pathlib import Path
import tomllib

from mvi_beamcheck.config import BeamCheckConfig

def test_example_config_parses_to_beamcheck_config():
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