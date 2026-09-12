"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Tile.
"""

import pygame

import settings


class Tile:
    POWERUP_LINE = "line"  # In-game name: Line Clear
    POWERUP_COLOR_BOMB = "color_bomb"  # In-game name: Color Bomb

    def __init__(self, i: int, j: int, color: int, variety: int) -> None:
        self.i = i
        self.j = j
        self.x = self.j * settings.TILE_SIZE
        self.y = self.i * settings.TILE_SIZE
        self.color = color
        self.variety = variety
        self.powerup_type = None
        self.alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )

    def set_powerup(self, powerup_type: str) -> None:
        self.powerup_type = powerup_type

    def clear_powerup(self) -> None:
        self.powerup_type = None

    def render(self, surface: pygame.Surface, offset_x: int, offset_y: int) -> None:
        self.alpha_surface.fill((0, 0, 0, 0))
        self.alpha_surface.blit(
            settings.TEXTURES["tiles"],
            (0, 0),
            settings.FRAMES["tiles"][self.color][self.variety],
        )
        pygame.draw.rect(
            self.alpha_surface,
            (34, 32, 52, 200),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )

        base_x = self.x + offset_x
        base_y = self.y + offset_y

        surface.blit(self.alpha_surface, (base_x + 2, base_y + 2))
        surface.blit(
            settings.TEXTURES["tiles"],
            (base_x, base_y),
            settings.FRAMES["tiles"][self.color][self.variety],
        )

        if self.powerup_type == Tile.POWERUP_LINE:
            icon = settings.TEXTURES["lightning"]
            icon_x = base_x + (settings.TILE_SIZE - icon.get_width()) // 2
            icon_y = base_y + (settings.TILE_SIZE - icon.get_height()) // 2
            surface.blit(icon, (icon_x, icon_y))
        elif self.powerup_type == Tile.POWERUP_COLOR_BOMB:
            icon = settings.TEXTURES["bomb"]
            icon_x = base_x + (settings.TILE_SIZE - icon.get_width()) // 2
            icon_y = base_y + (settings.TILE_SIZE - icon.get_height()) // 2
            surface.blit(icon, (icon_x, icon_y))
