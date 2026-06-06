from __future__ import annotations

import argparse
import sys

from .config import load_config
from .input_controller import InputController
from .logger import setup_logger
from .safety import SafetyGuard
from .screen import Screen
from .tasks import NpcAutoDuelTask


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WeYGO local automation runner")
    parser.add_argument(
        "task",
        choices=["npc-auto-duel"],
        help="Task to run.",
    )
    parser.add_argument(
        "--config",
        help="Optional local config path. Defaults to config/local.json when present.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually move/click the mouse. Without this flag, only logs planned actions.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    logger, run_dir = setup_logger()

    execute = bool(args.execute)
    if not execute:
        logger.info("dry-run mode: no mouse input will be sent")

    try:
        screen = Screen(config, logger, run_dir, execute)
        safety = SafetyGuard(config, logger)
        safety.describe()
        input_controller = InputController(config, screen, logger, execute)

        if args.task == "npc-auto-duel":
            NpcAutoDuelTask(config, screen, input_controller, safety, logger).run()
    except KeyboardInterrupt:
        logger.warning("stopped by Ctrl+C")
        return 130
    except Exception as exc:
        logger.error("task failed: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
