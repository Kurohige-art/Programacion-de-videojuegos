"""
#
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class LogPair: a top log
(rendered flipped upside down) and a bottom log, LOGS_GAP pixels
apart, that scroll left together and score once the bird passes them.
"""

import pygame

import settings


class LogPair:
    def __init__(self, x: float, y: float, is_moving: bool = False, gap: float = settings.LOGS_GAP) -> None:
        self.x: float = x
        self.y: float = y
        self.scored: bool = False
        self.is_moving = is_moving
        self.gap = gap
        self.gap_dir = 1
        self.initial_gap = gap
        self.min_gap = 0
        maximum_gap = gap + 35
        center_margin = 20
        minimum_center_y = maximum_gap / 2 + center_margin
        maximum_center_y = settings.VIRTUAL_HEIGHT - maximum_gap / 2 - center_margin
        requested_center_y = y + settings.LOG_HEIGHT + gap / 2
        self.gap_center_y = max(
            minimum_center_y,
            min(requested_center_y, maximum_center_y),
        )
        self.y = self.gap_center_y - settings.LOG_HEIGHT - gap / 2

    def get_top_rect(self) -> pygame.Rect:
        return pygame.Rect(
            round(self.x), round(self.y), settings.LOG_WIDTH, settings.LOG_HEIGHT
        )

    def get_bottom_rect(self) -> pygame.Rect:
        return pygame.Rect(
            round(self.x),
            round(self.y + self.gap + settings.LOG_HEIGHT),
            settings.LOG_WIDTH,
            settings.LOG_HEIGHT,
        )

    def collides(self, rect: pygame.Rect) -> bool:
        return self.get_top_rect().colliderect(
            rect
        ) or self.get_bottom_rect().colliderect(rect)

    def update(self, dt: float) -> None:
        self.x += -settings.MAIN_SCROLL_SPEED * dt

        if self.is_moving:
            self.gap += 50 * self.gap_dir * dt

            if self.gap > self.initial_gap + 35:
                self.gap = self.initial_gap + 35
                self.gap_dir = -1
            elif self.gap <= self.min_gap:
                self.gap = self.min_gap
                self.gap_dir = 1
                settings.SOUNDS["crash"].play()

            self.y = self.gap_center_y - settings.LOG_HEIGHT - self.gap / 2

    def is_out_of_game(self) -> bool:
        return self.x < -settings.LOG_WIDTH

    def update_scored(self, rect: pygame.Rect) -> bool:
        if self.scored:
            return False
        if rect.left > self.x + settings.LOG_WIDTH:
            self.scored = True
            return True
        return False

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["log_inverted"], self.get_top_rect())
        surface.blit(settings.TEXTURES["log"], self.get_bottom_rect())