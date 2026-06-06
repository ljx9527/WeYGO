from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .screen import Region


def get_active_window_region() -> Region:
    import pyautogui

    window = pyautogui.getActiveWindow()
    if window is None:
        raise RuntimeError("No active window detected.")
    if getattr(window, "isMinimized", False):
        raise RuntimeError("Active window is minimized.")

    return Region(
        int(window.left),
        int(window.top),
        int(window.width),
        int(window.height),
        f"manual selected window '{window.title}'",
    )


def apply_region_to_config(config: dict[str, Any], region: Region) -> dict[str, Any]:
    config["app"]["window_title"] = ""
    config["app"]["viewport"] = {
        key: value
        for key, value in asdict(region).items()
        if key in {"x", "y", "width", "height"}
    }
    return config
