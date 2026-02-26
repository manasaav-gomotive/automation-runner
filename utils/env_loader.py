import json
import os
from pathlib import Path

def load_env(env_name):
    config_path = Path(__file__).parent.parent / "config" / "environments" / f"{env_name}.json"
    with open(config_path) as f:
        config = json.load(f)

    env = os.environ.copy()

    for k,v in config.items():
        env[k] = str(v)

    return env