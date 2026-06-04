from pathlib import Path
import tomllib

def test_example_config_can_be_loaded():
    root = Path(__file__).resolve().parents[1]
    path = root / 'config' / 'example.toml'
    
    with open(path, 'rb') as f:
        config = tomllib.load(f)

    assert 'output' in config
    assert 'crosscal_response' in config['output']
    assert 'crosscal_output' in config['output']
    assert 'target_output' in config['output']