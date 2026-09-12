"""
ISPPV1 2024
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class LevelTransitionState.
"""

from typing import Any, Dict

import pygame

from gale.state import BaseState
from gale.timer import Timer

import settings


class LevelTransitionState(BaseState):
    CLOSE_SPEED = 520

    def enter(self, **enter_params: Dict[str, Any]) -> None:
        settings.SOUNDS["victory"].stop()
        self.level = enter_params["level"]
        self.game_level = enter_params["game_level"]
        self.player = enter_params["player"]
        self.camera = enter_params["camera"]
        self.clock = enter_params["clock"]
        self.next_level = self.level + 1
        self.center = (settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2)
        self.radius = (settings.VIRTUAL_WIDTH**2 + settings.VIRTUAL_HEIGHT**2) ** 0.5

    def update(self, dt: float) -> None:
        self.radius -= self.CLOSE_SPEED * dt
        if self.radius <= 0:
            Timer.clear()
            if self.level >= settings.NUM_LEVELS:
                self.state_machine.change("start")
            else:
                self.state_machine.change(
                    "play",
                    level=self.next_level,
                    transition_open=True,
                )

    def render(self, surface: pygame.Surface) -> None:
        self.game_level.render(surface, self.camera)
        self.player.render(surface, self.camera)
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 255))
        pygame.draw.circle(overlay, (0, 0, 0, 0), self.center, max(0, int(self.radius)))
        surface.blit(overlay, (0, 0))
