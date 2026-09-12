"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

from typing import Dict, Any

import pygame

from gale.camera import Camera
from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings
from src.Clock import Clock
from src.GameLevel import GameLevel
from src.Player import Player
from src.GameItem import GameItem


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params.get("level", 1)
        self.game_level = enter_params.get("game_level")
        if self.game_level is None:
            self.game_level = GameLevel(self.level)
            pygame.mixer.music.load(
                settings.BASE_DIR / "assets" / "sounds" / "music_grassland.ogg"
            )
            pygame.mixer.music.play(loops=-1)

        self.tilemap = self.game_level.tilemap
        self.player = enter_params.get("player")
        if self.player is None:
            # Resting exactly on the ground tile's surface (row 9, one tile
            # below the platform's top edge) rather than a few pixels into
            # it, so gale.tilemap's one-way platform collision (which
            # requires the entity to already be at/above the surface) picks
            # it up on the very first frame instead of falling through.
            spawn_y = 9 * self.tilemap.tile_height - 20
            self.player = Player(0, spawn_y, self.game_level)
            self.player.change_state("idle")

        self.camera = enter_params.get("camera")

        if self.camera is None:
            self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
            self.camera.follow(self.player, rate=settings.CAMERA_FOLLOW_RATE)
            self.camera.bounds = self.game_level.get_rect()
            self.camera.x, self.camera.y = self.player.x, self.player.y
            self.camera.update(0)

        self.clock = enter_params.get("clock")
        self.transition_radius = 0 if enter_params.get("transition_open") else None
        self.transition_center = (
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 2,
        )

        if self.clock is None:
            self.clock = Clock(100)

            def countdown_timer():
                self.clock.count_down()

                if 0 < self.clock.time <= 5:
                    settings.SOUNDS["timer"].play()

                if self.clock.time == 0:
                    self.player.change_state("dead")

            Timer.every(1, countdown_timer)
        else:
            Timer.resume()

    def update(self, dt: float) -> None:
        if self.transition_radius is not None:
            self.transition_radius += 520 * dt
            diagonal = (
                settings.VIRTUAL_WIDTH**2 + settings.VIRTUAL_HEIGHT**2
            ) ** 0.5
            if self.transition_radius >= diagonal:
                self.transition_radius = None

        if self.game_level.update_key_block(self.player.score):
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            settings.SOUNDS["victory"].play()
            Timer.clear()

        if self.player.is_dead:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            settings.SOUNDS["victory"].stop()
            Timer.clear()
            self.state_machine.change("game_over", self.player, self.level)

        previous_player_y = self.player.y
        previous_player_vy = self.player.vy
        self.player.update(dt)

        if self.player.y >= self.tilemap.pixel_height:
            self.player.change_state("dead")

        self.camera.update(dt)
        self.game_level.update(dt)

        if self.game_level.key is not None and self.player.collides(
            self.game_level.key
        ):
            self.game_level.key = None
            settings.SOUNDS["victory"].stop()
            self.state_machine.change(
                "level_transition",
                level=self.level,
                game_level=self.game_level,
                player=self.player,
                camera=self.camera,
                clock=self.clock,
            )
            return

        for creature in self.game_level.creatures:
            if self.player.collides(creature):
                falling_on_creature = (
                    previous_player_vy > 0
                    and previous_player_y + self.player.height <= creature.y + 4
                )
                if falling_on_creature:
                    creature.stomp()
                    self.player.vy = -settings.GRAVITY / 3
                else:
                    self.player.change_state("dead")

        for item in self.game_level.items:
            if not item.active or not item.collidable:
                continue

            if self.player.collides(item):
                item.on_collide(self.player)
                item.on_consume(self.player)

    def render(self, surface: pygame.Surface) -> None:
        self.game_level.render(surface, self.camera)
        self.player.render(surface, self.camera)

        render_text(
            surface,
            f"Score: {self.player.score}",
            settings.FONTS["small"],
            5,
            5,
            (255, 255, 255),
            shadowed=True,
        )

        render_text(
            surface,
            f"Time: {self.clock.time}",
            settings.FONTS["small"],
            settings.VIRTUAL_WIDTH - 60,
            5,
            (255, 255, 255),
            shadowed=True,
        )

        if self.transition_radius is not None:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 255))
            pygame.draw.circle(
                overlay,
                (0, 0, 0, 0),
                self.transition_center,
                max(0, int(self.transition_radius)),
            )
            surface.blit(overlay, (0, 0))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "pause" and input_data.pressed:
            Timer.pause()
            self.state_machine.change(
                "pause",
                level=self.level,
                camera=self.camera,
                game_level=self.game_level,
                player=self.player,
                clock=self.clock,
            )
        else:
            self.player.on_input(input_id, input_data)
