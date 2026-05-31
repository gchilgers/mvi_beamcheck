from pathlib import Path
import tomllib

def test_configuration_can_be_loaded():
    config_path = Path(__file__).parents[1] / 'config' / 'example.toml'

    with open(config_path, 'rb') as f:
        config = tomllib.load(f)

    assert config is not None
