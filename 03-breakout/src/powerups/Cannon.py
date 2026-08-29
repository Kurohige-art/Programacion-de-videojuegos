from typing import TypeVar

import pygame

import settings
from src.powerups.PowerUp import PowerUp
from src.powerups.CannonProjectile import CannonProjectile


class Cannon(PowerUp):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 0)
        self.collected = False
        self.shots = 0
        self.cannon_frame = 0
        self.paddle_width = 0

    def take(self, play_state: TypeVar("PlayState")) -> None:
        self.collected = True
        max_pair = len(settings.FRAMES["cannon"]["cannons"]) // 2 - 1
        self.cannon_frame = min(play_state.paddle.skin, max_pair)
        self.paddle_width = play_state.paddle.width
        self.x = play_state.paddle.x
        self.y = play_state.paddle.y

    def update(self, dt: float) -> None:
        if not self.collected:
            super().update(dt)

    def can_fire(self, projectiles) -> bool:
        return self.collected and self.shots < 3 and not projectiles

    def fire(self, play_state: TypeVar("PlayState")) -> None:
        if not self.can_fire(play_state.cannon_projectiles):
            return

        paddle = play_state.paddle
        self.x = paddle.x
        self.y = paddle.y
        self.paddle_width = paddle.width
        play_state.cannon_projectiles = [
            CannonProjectile(self.x, self.y, -1),
            CannonProjectile(self.x + paddle.width - 14, self.y, 1),
        ]
        self.shots += 1
        if self.shots == 3:
            self.active = False

    def render(self, surface: pygame.Surface) -> None:
        if not self.collected:
            super().render(surface)
            return

        pair_index = self.cannon_frame
        right_frame = settings.FRAMES["cannon"]["cannons"][pair_index * 2]
        left_frame = settings.FRAMES["cannon"]["cannons"][pair_index * 2 + 1]

        right_x = self.x + self.paddle_width - 14
        left_x = self.x
        top_y = self.y - 16

        surface.blit(settings.TEXTURES["spritesheet_canon"], (right_x, top_y), right_frame)
        surface.blit(settings.TEXTURES["spritesheet_canon"], (left_x, top_y), left_frame)