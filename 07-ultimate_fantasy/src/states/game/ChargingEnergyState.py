"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

This file contains the class ChargingEnergyState: displays an entity's
recovery period after its action and advances the battle turn automatically.
"""

from typing import Any, Callable

import pygame

from gale.state import BaseState
from gale.ui.text_box import TextBox

import settings


class ChargingEnergyState(BaseState):
    def enter(
        self,
        battle_state: Any,
        entity: Any,
        on_complete: Callable[[Any], None],
    ) -> None:
        self.battle_state = battle_state
        self.entity = entity
        self.on_complete = on_complete
        self.elapsed = 0.0
        self.duration = entity.rest_time
        self.textbox = TextBox(
            0,
            settings.VIRTUAL_HEIGHT - 64,
            settings.VIRTUAL_WIDTH,
            64,
            "charging energy...",
            font=settings.FONTS["medium"],
            lines_per_page=3,
        )

    def update(self, dt: float) -> None:
        self.battle_state.update_timers(dt)
        for enemy in self.battle_state.enemies:
            if not enemy.dead:
                enemy.update(dt)

        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.state_machine.pop()
            self.on_complete(self.entity)

    def on_input(self, input_id: str, input_data: Any) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        self.textbox.render(surface)