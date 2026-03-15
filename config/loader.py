import json
import os
from types import SimpleNamespace

from config.suite_map import SUITE_MAP

def load_env_config(env: str):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(base_dir, "config", "environments", f"{env}.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        data = json.load(f)

    config = SimpleNamespace(**data)
    if not hasattr(config, "suite_map") or not config.suite_map:
        config.suite_map = SUITE_MAP
    return config
