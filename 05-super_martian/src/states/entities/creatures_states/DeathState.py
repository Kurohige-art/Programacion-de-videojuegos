"""
ISPPV1 2024
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class DeathState.
"""

from src.states.entities.BaseEntityState import BaseEntityState


class DeathState(BaseEntityState):
    def enter(self) -> None:
        self.entity.vx = 0
        self.entity.change_animation("death")

    def update(self, dt: float) -> None:
        animation = self.entity.current_animation
        if animation.loops is not None and animation.times_played >= animation.loops:
            self.entity.is_dead = True
