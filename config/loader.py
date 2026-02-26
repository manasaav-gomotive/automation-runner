import json
import os
from types import SimpleNamespace

def load_env_config(env: str):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(base_dir, "config", "environments", f"{env}.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        data = json.load(f)

    return SimpleNamespace(**data)