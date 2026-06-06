from __future__ import annotations

from typing import Any

from .input_controller import InputController
from .safety import SafetyGuard
from .screen import Screen


class NpcAutoDuelTask:
    """Starts a built-in NPC auto duel from the visible home/NPC flow."""

    def __init__(
        self,
        config: dict[str, Any],
        screen: Screen,
        input_controller: InputController,
        safety: SafetyGuard,
        logger: Any,
    ) -> None:
        self.config = config
        self.task_config = config["tasks"]["npc_auto_duel"]
        self.screen = screen
        self.input = input_controller
        self.safety = safety
        self.logger = logger

    def run(self) -> None:
        npc_point = str(self.task_config["npc_point"])
        dialog_taps = int(self.task_config["dialog_taps"])
        post_start_wait = float(self.task_config["post_start_wait_seconds"])

        self.logger.info("task start: npc_auto_duel")
        self.screen.screenshot("before_npc_auto_duel")

        self._step_click(npc_point, "select npc from home screen")

        for index in range(dialog_taps):
            self._step_click("dialog_next", f"advance npc dialog {index + 1}/{dialog_taps}")

        if bool(self.task_config["confirm_before_start"]):
            self.logger.info("confirmation point: next step starts the built-in auto duel")

        target = "auto_duel" if bool(self.task_config["prefer_auto_duel"]) else "manual_duel"
        self._step_click(target, "start built-in npc auto duel")

        self.input.wait(float(self.config["app"]["state_delay_seconds"]), "wait for possible prompt")
        self.screen.screenshot("after_start_auto_duel")

        self._step_click("confirm", "confirm common prompt if present")
        self.input.wait(post_start_wait, "let game load or run the duel")
        self.screen.screenshot("npc_auto_duel_started")

        self.logger.info("task complete: npc_auto_duel")

    def _step_click(self, point_name: str, reason: str) -> None:
        self.safety.check()
        self.input.click(point_name, reason)
