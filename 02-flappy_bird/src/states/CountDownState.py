"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class CountDownState.
"""

import pygame

from gale.state import BaseState
from gale.text import render_text

import settings
from src.World import World


class CountDownState(BaseState):
    def enter(self, **enter_params: dict) -> None:
        self.world = enter_params.get("world", World(generate_logs=False))
        self.bird = enter_params.get("bird", None)
        self.score = enter_params.get("score", 0)
        self.world.reset(False)
        self.counter = 3
        self.timer = 0.0

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.timer >= 1.0:
            self.timer = 0.0
            self.counter -= 1
            if self.counter == 0:
                self.state_machine.change(
                    "playing", 
                    world=self.world, 
                    bird=self.bird, 
                    score=self.score
                )
                return
        if self.bird is None:
            self.world.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        if self.bird:
            self.bird.render(surface)
        render_text(
            surface,
            str(self.counter),
            settings.FONTS["huge"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )
