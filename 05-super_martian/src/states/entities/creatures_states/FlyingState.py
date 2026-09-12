"""
ISPPV1 2024
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class FlyingState.
"""

from src.states.entities.BaseEntityState import BaseEntityState


class FlyingState(BaseEntityState):
    def enter(self, flipped: bool) -> None:
        self.entity.change_animation("walk")
        self.entity.flipped = flipped
        self.entity.vx = -self.entity.walk_speed
        if self.entity.flipped:
            self.entity.vx *= -1

    def update(self, dt: float) -> None:
        if self.entity.x <= 0 or self.entity.x + self.entity.width >= self.entity.tilemap.pixel_width:
            self.entity.vx *= -1
            self.entity.flipped = not self.entity.flipped
