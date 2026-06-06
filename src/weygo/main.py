from __future__ import annotations

import argparse
import sys

from .config import load_config
from .runner import run_task


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
    return run_task(config, args.task, bool(args.execute))


if __name__ == "__main__":
    sys.exit(main())
