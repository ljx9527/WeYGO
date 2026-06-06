from __future__ import annotations

import time
from typing import Any

from .screen import Screen


class InputController:
    def __init__(self, config: dict[str, Any], screen: Screen, logger: Any, execute: bool) -> None:
        self.config = config
        self.screen = screen
        self.logger = logger
        self.execute = execute
        self.delay = float(config["app"]["action_delay_seconds"])

        if execute:
            import pyautogui

            pyautogui.FAILSAFE = bool(config["safety"]["enable_pyautogui_failsafe"])

    def click(self, point_name: str, reason: str) -> None:
        x, y = self.screen.point(point_name)
        if self.execute:
            import pyautogui

            self.logger.info("click %s at (%s, %s): %s", point_name, x, y, reason)
            pyautogui.click(x=x, y=y)
        else:
            self.logger.info("[dry-run] click %s at (%s, %s): %s", point_name, x, y, reason)
        time.sleep(self.delay)

    def wait(self, seconds: float, reason: str) -> None:
        self.logger.info("wait %.1fs: %s", seconds, reason)
        time.sleep(seconds)
