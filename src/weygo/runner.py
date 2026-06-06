from __future__ import annotations

from pathlib import Path
from typing import Any

from .input_controller import InputController
from .logger import setup_logger
from .safety import SafetyGuard
from .screen import Screen
from .tasks import NpcAutoDuelTask


def run_task(config: dict[str, Any], task: str, execute: bool) -> int:
    logger, run_dir = setup_logger()

    if not execute:
        logger.info("dry-run mode: no mouse input will be sent")

    try:
        screen = Screen(config, logger, run_dir, execute)
        safety = SafetyGuard(config, logger)
        safety.clear_stop()
        safety.describe()
        input_controller = InputController(config, screen, logger, execute)

        if task == "npc-auto-duel":
            NpcAutoDuelTask(config, screen, input_controller, safety, logger).run()
            return 0

        logger.error("unknown task: %s", task)
        return 2
    except KeyboardInterrupt:
        logger.warning("stopped by Ctrl+C")
        return 130
    except Exception as exc:
        logger.error("task failed: %s", exc)
        return 1


def request_stop(config: dict[str, Any]) -> Path:
    class _NullLogger:
        def info(self, *_args: Any, **_kwargs: Any) -> None:
            pass

        def warning(self, *_args: Any, **_kwargs: Any) -> None:
            pass

    safety = SafetyGuard(config, _NullLogger())
    return safety.request_stop()
