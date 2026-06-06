from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT


class SafetyGuard:
    def __init__(self, config: dict[str, Any], logger: Any) -> None:
        self.config = config
        self.logger = logger
        self.stop_file = PROJECT_ROOT / str(config["safety"]["stop_file"])

    def check(self) -> None:
        if self.stop_file.exists():
            raise RuntimeError(f"Stop file detected: {self.stop_file}")

    def describe(self) -> None:
        self.logger.info("move mouse to a screen corner to trigger pyautogui failsafe")
        self.logger.info("create %s to stop before the next step", self.stop_file)
