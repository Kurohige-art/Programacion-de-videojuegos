"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayerShootBowState.
"""

from typing import TypeVar

import pygame

from gale.state import StateMachine

import settings
from src.states.entity.BaseEntityState import BaseEntityState
from src.world.Bow import Bow


class PlayerShootBowState(BaseEntityState):
    def __init__(
        self,
        player: TypeVar("Player"),
        state_machine: StateMachine,
        dungeon: TypeVar("Dungeon"),
    ) -> None:
        super().__init__(player, state_machine)
        self.dungeon = dungeon
        self.timer = 0.0
        self.duration = 0.2

    def enter(self) -> None:
        self.timer = 0.0
        direction = self.entity.direction

        if direction == "down":
            self.frame_index = 1
        elif direction == "up":
            self.frame_index = 2
        elif direction == "right":
            self.frame_index = 3
        elif direction == "left":
            self.frame_index = 4

        projectile = Bow.fire(self.entity, direction)
        self.dungeon.current_room.projectiles.append(projectile)

        if "sword" in settings.SOUNDS:
            settings.SOUNDS["sword"].stop()
            settings.SOUNDS["sword"].play()

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.timer >= self.duration:
            self.entity.change_state("idle")

    def render(self, surface: pygame.Surface) -> None:
        texture = settings.TEXTURES["character_arrow"]
        frame = settings.frame("character_arrow", self.frame_index)

        sprite_x = round(self.entity.x)
        sprite_y = round(self.entity.y)
        surface.blit(texture, (sprite_x, sprite_y), frame)