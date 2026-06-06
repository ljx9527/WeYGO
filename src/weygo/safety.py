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

    def request_stop(self) -> Path:
        self.stop_file.write_text("stop\n", encoding="utf-8")
        self.logger.info("stop requested: %s", self.stop_file)
        return self.stop_file

    def clear_stop(self) -> None:
        if self.stop_file.exists():
            self.stop_file.unlink()
            self.logger.info("cleared stale stop file: %s", self.stop_file)

    def describe(self) -> None:
        self.logger.info("move mouse to a screen corner to trigger pyautogui failsafe")
        self.logger.info("create %s to stop before the next step", self.stop_file)
