"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Boss.
"""

from typing import Any

import pygame

import settings
from src.world.FireBallProjectile import FireBallProjectile


class Boss:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 36
        self.health = 8
        self.dead = False
        self.direction = "down"
        
        self.vulnerable = False
        self.vulnerable_timer = 0.0
        self.hurt_timer = 0.0
        
        self.attack_timer = 0.0
        self.is_attacking = False
        self.attack_duration = 0.0

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def collides(self, target: Any) -> bool:
        if isinstance(target, pygame.Rect):
            target_rect = target
        else:
            target_rect = target.get_collision_rect()
        return self.get_collision_rect().colliderect(target_rect)

    def hit_by_arrow(self, damage: int = 0) -> None:
        self.vulnerable = True
        self.vulnerable_timer = 2.0
        self.hurt_timer = 2.0
        self.is_attacking = False

    def hit_by_sword(self, damage: int = 1) -> bool:
        if self.vulnerable:
            self.health -= damage
            self.vulnerable = False
            self.vulnerable_timer = 0.0
            self.hurt_timer = 0.0

            if self.health <= 0:
                self.dead = True
            return True
        return False

    def update(self, dt: float, room: Any) -> None:
        if self.dead:
            return

        if self.vulnerable:
            self.vulnerable_timer -= dt
            if self.vulnerable_timer <= 0:
                self.vulnerable = False

        if self.hurt_timer > 0:
            self.hurt_timer -= dt
            return

        player = room.player
        dx = (player.x + player.width / 2) - (self.x + self.width / 2)
        dy = (player.y + player.height / 2) - (self.y + self.height / 2)

        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "down" if dy > 0 else "up"

        self.attack_timer += dt
        if self.attack_timer >= 2.5:
            self.attack_timer = 0.0
            self.is_attacking = True
            self.attack_duration = 0.4
            
            fireball = FireBallProjectile(
                self.x + self.width / 2 - 8,
                self.y + self.height / 2 - 8,
                player.x + player.width / 2,
                player.y + player.height / 2,
                self.direction,
            )
            room.projectiles.append(fireball)

        if self.is_attacking:
            self.attack_duration -= dt
            if self.attack_duration <= 0:
                self.is_attacking = False

    def render(
        self,
        surface: pygame.Surface,
        offset_x: float = 0,
        offset_y: float = 0,
    ) -> None:
        if self.hurt_timer > 0:
            if self.direction == "left":
                frame_idx = 7
            elif self.direction == "right":
                frame_idx = 10
            elif self.direction == "up":
                frame_idx = 3
            else:
                frame_idx = 1
        elif self.is_attacking:
            if self.direction == "down":
                frame_idx = 2
            elif self.direction == "up":
                frame_idx = 4
            elif self.direction == "left":
                frame_idx = 6
            else:
                frame_idx = 9
        else:
            if self.direction == "down":
                frame_idx = 1
            elif self.direction == "up":
                frame_idx = 3
            elif self.direction == "left":
                frame_idx = 5
            else:
                frame_idx = 8

        texture = settings.TEXTURES["boss"]
        frame = settings.frame("boss", frame_idx)
        surface.blit(texture, (round(self.x) + offset_x, round(self.y) + offset_y), frame)