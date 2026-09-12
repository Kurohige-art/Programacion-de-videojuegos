"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the bow and arrow projectile classes.
"""

from typing import Any

import pygame

import settings
from src.Projectile import Projectile


class ArrowProjectile:
    """Projectile wrapper for the direction-specific arrow texture."""
    def __init__(self, x: float, y: float, direction: str):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.direction = direction
        
        base_texture = settings.TEXTURES["arrow"]
        if direction == "down":
            self.texture = pygame.transform.rotate(base_texture, 180)
        elif direction == "left":
            self.texture = pygame.transform.rotate(base_texture, 90)
        elif direction == "right":
            self.texture = pygame.transform.rotate(base_texture, -90)
        else:
            self.texture = base_texture

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def render(
        self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0
    ) -> None:
        surface.blit(self.texture, (self.x + offset_x, self.y + offset_y))


class Bow:
    """Factory for player arrow projectiles."""
    @staticmethod
    def fire(player_entity: Any, direction: str) -> Projectile:
        spawn_x = player_entity.x + (player_entity.width / 2) - 2
        spawn_y = player_entity.y + (player_entity.height / 2) + 1
        
        arrow_graphic = ArrowProjectile(spawn_x, spawn_y, direction)
        return Projectile(arrow_graphic, direction)
