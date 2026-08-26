"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class Bird.
"""

import pygame

import settings


class Bird:
    def __init__(self, x: float, y: float, width: float, height: float) -> None:
        self.x: float = x
        self.y: float = y
        self.width: float = width
        self.height: float = height
        self.vy: float = 0.0
        self.jumping: bool = False
        self.vx = 0.0
        self.ghost_mode = False
        self.ghost_timer = 0.0
        self.ghost_blink_timer = 0.0

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def jump(self) -> None:
        self.jumping = True

    def update(self, dt: float) -> None:
        self.vy += settings.GRAVITY * dt

        if self.jumping:
            settings.SOUNDS["jump"].play()
            self.vy = -settings.JUMP_TAKEOFF_SPEED
            self.jumping = False

        self.y += self.vy * dt
        self.x += self.vx * dt
        self.x = max(0, min(self.x, settings.VIRTUAL_WIDTH - self.width))

        if self.ghost_mode:
            self.ghost_timer -= dt
            if self.ghost_timer <= 2.0:
                self.ghost_blink_timer = (self.ghost_blink_timer + dt) % 0.24
            else:
                self.ghost_blink_timer = 0.0
            if self.ghost_timer <= 0:
                self.ghost_mode = False
                self.ghost_blink_timer = 0.0
                pygame.mixer.music.load(
                    settings.BASE_DIR / "assets" / "sounds" / "marios_way.ogg"
                )
                pygame.mixer.music.play(loops=-1)

    def render(self, surface: pygame.Surface) -> None:
        is_blinking = self.ghost_mode and self.ghost_timer <= 2.0
        is_visible = self.ghost_blink_timer < 0.12
        if self.ghost_mode and (not is_blinking or is_visible):
            surface.blit(settings.TEXTURES["ghost"], self.get_rect())
        else:
            surface.blit(settings.TEXTURES["bird"], self.get_rect())