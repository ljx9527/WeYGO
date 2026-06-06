from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "default.json"
LOCAL_CONFIG = PROJECT_ROOT / "config" / "local.json"


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def load_config(path: str | None = None) -> Dict[str, Any]:
    with DEFAULT_CONFIG.open("r", encoding="utf-8") as f:
        config = json.load(f)

    local_path = Path(path) if path else LOCAL_CONFIG
    if local_path.exists():
        with local_path.open("r", encoding="utf-8") as f:
            config = deep_merge(config, json.load(f))

    return config
