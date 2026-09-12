"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class FireBallProjectile.
"""

import math
from typing import Any

import pygame

import settings


class FireBallProjectile:
    def __init__(self, x: float, y: float, target_x: float, target_y: float, direction: str):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.speed = 50
        self.dead = False
        
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        self.vx = (dx / dist) * self.speed
        self.vy = (dy / dist) * self.speed
        
        base_texture = settings.TEXTURES["fire_ball"]
        if direction == "left":
            self.texture = pygame.transform.rotate(base_texture, 180)
        elif direction == "up":
            self.texture = pygame.transform.rotate(base_texture, 90)
        elif direction == "down":
            self.texture = pygame.transform.rotate(base_texture, -90)
        else:
            self.texture = base_texture

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def update(self, dt: float) -> None:
        if self.dead:
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Destruir si sale de la pantalla
        if (self.x < 0 or self.x > settings.VIRTUAL_WIDTH or 
            self.y < 0 or self.y > settings.VIRTUAL_HEIGHT):
            self.dead = True

    def render(
        self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0
    ) -> None:
        surface.blit(self.texture, (self.x + offset_x, self.y + offset_y))

    def collides(self, target: Any) -> bool:
        return self.get_collision_rect().colliderect(target.get_collision_rect())
