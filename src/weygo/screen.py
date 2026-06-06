from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Tuple


@dataclass
class ScreenSize:
    width: int
    height: int


@dataclass
class Region:
    x: int
    y: int
    width: int
    height: int
    source: str


class Screen:
    def __init__(self, config: dict[str, Any], logger: Any, run_dir: Path, execute: bool) -> None:
        self.config = config
        self.logger = logger
        self.run_dir = run_dir
        self.execute = execute
        self.base = ScreenSize(
            int(config["app"]["base_width"]),
            int(config["app"]["base_height"]),
        )
        self.region = self.resolve_region()

    def current_size(self) -> ScreenSize:
        return ScreenSize(self.region.width, self.region.height)

    def resolve_region(self) -> Region:
        viewport = self.config["app"].get("viewport")
        if viewport:
            region = Region(
                int(viewport["x"]),
                int(viewport["y"]),
                int(viewport["width"]),
                int(viewport["height"]),
                "config viewport",
            )
            self.logger.info("target region: %s", region)
            return region

        title = str(self.config["app"].get("window_title") or "").strip()
        if title:
            region = self._find_window_region(title)
            if region:
                self.logger.info("target region: %s", region)
                return region

        if self.execute and bool(self.config["app"]["require_target_region_for_execute"]):
            raise RuntimeError(
                "Execution requires app.window_title or app.viewport in config/local.json."
            )

        self.logger.info("target region: base screenshot size for dry-run")
        return Region(0, 0, self.base.width, self.base.height, "base dry-run")

    def _find_window_region(self, title: str) -> Region | None:
        try:
            import pyautogui

            for window in pyautogui.getWindowsWithTitle(title):
                if getattr(window, "isMinimized", False):
                    continue
                return Region(
                    int(window.left),
                    int(window.top),
                    int(window.width),
                    int(window.height),
                    f"window title '{title}'",
                )
        except Exception as exc:
            self.logger.warning("window lookup failed: %s", exc)
        return None

    def point(self, name: str) -> Tuple[int, int]:
        ratio_x, ratio_y = self.config["points"][name]
        return (
            self.region.x + int(self.region.width * ratio_x),
            self.region.y + int(self.region.height * ratio_y),
        )

    def screenshot(self, label: str) -> Path | None:
        try:
            import pyautogui

            target = self.run_dir / f"{label}.png"
            image = pyautogui.screenshot(
                region=(self.region.x, self.region.y, self.region.width, self.region.height)
            )
            image.save(target)
            self.logger.info("saved screenshot: %s", target)
            return target
        except Exception as exc:
            self.logger.warning("screenshot failed: %s", exc)
            return None
