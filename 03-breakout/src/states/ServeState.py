"""
ISPPV1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class to define the Serve state.
"""

import pygame

from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text

import settings
from src.Ball import Ball
from src.utilities.level_maker import create_level


class ServeState(BaseState):
    def enter(self, **params: dict) -> None:
        self.level = params["level"]
        self.paddle = params["paddle"]
        self.captured = params.get("captured", False)
        self.ball_offset_x = params.get("ball_offset_x", self.paddle.width // 2 - 4)
        if not self.captured:
            self.paddle.x = settings.VIRTUAL_WIDTH // 2 - 32
        self.paddle.y = settings.VIRTUAL_HEIGHT - 32
        self.ball = params.get(
            "ball", Ball(self.paddle.x + self.ball_offset_x, self.paddle.y - 8)
        )
        self.ball.vx = 0
        self.ball.vy = 0
        self.brickset = params.get("brickset", create_level(self.level))
        self.score = params.get("score", 0)
        self.lives = params.get("lives", 3)
        self.live_factor = params.get("live_factor", 1)
        self.points_to_next_live = params.get(
            "points_to_next_live", settings.LIVE_POINTS_BASE
        )
        self.powerups = params.get("powerups", [])
        self.catch_ball_timer = params.get("catch_ball_timer", 0.0)
        self.cannons_active = params.get("cannons_active", False)
        self.projectiles = params.get("projectiles", [])

    def update(self, dt: float) -> None:
        self.paddle.update(dt)
        self.ball.x = self.paddle.x + self.ball_offset_x
        self.ball.y = self.paddle.y - self.ball.height

        if self.captured:
            self.catch_ball_timer -= dt
            if self.catch_ball_timer <= 0:
                self._launch_ball()

    def _launch_ball(self) -> None:
        self.state_machine.change(
            "play",
            level=self.level,
            score=self.score,
            lives=self.lives,
            paddle=self.paddle,
            balls=[self.ball],
            brickset=self.brickset,
            points_to_next_live=self.points_to_next_live,
            live_factor=self.live_factor,
            powerups=self.powerups,
            catch_ball_timer=0.0,
            catch_ball_ready=False,
            cannons_active=self.cannons_active,
            projectiles=self.projectiles,
        )

    def render(self, surface: pygame.Surface) -> None:
        heart_x = settings.VIRTUAL_WIDTH - 120

        i = 0
        # Draw filled hearts
        while i < self.lives:
            surface.blit(
                settings.TEXTURES["hearts"], (heart_x, 5), settings.FRAMES["hearts"][0]
            )
            heart_x += 11
            i += 1

        # Draw empty hearts
        while i < 3:
            surface.blit(
                settings.TEXTURES["hearts"], (heart_x, 5), settings.FRAMES["hearts"][1]
            )
            heart_x += 11
            i += 1

        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["tiny"],
            settings.VIRTUAL_WIDTH - 80,
            5,
            (255, 255, 255),
        )

        self.brickset.render(surface)

        self.paddle.render(surface)
        self.ball.render(surface)

        render_text(
            surface,
            f"Level {self.level}",
            settings.FONTS["large"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 2 - 30,
            (255, 255, 255),
            center=True,
        )
        render_text(
            surface,
            "Press Space to serve!" if self.captured else "Press Enter to serve!",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 2,
            (255, 255, 255),
            center=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_data.pressed and (
            (not self.captured and input_id == "enter")
            or (self.captured and input_id == "pause")
        ):
            self._launch_ball()

        if input_id == "move_left":
            if input_data.pressed:
                self.paddle.vx = -settings.PADDLE_SPEED
            elif input_data.released and self.paddle.vx < 0:
                self.paddle.vx = 0
        elif input_id == "move_right":
            if input_data.pressed:
                self.paddle.vx = settings.PADDLE_SPEED
            elif input_data.released and self.paddle.vx > 0:
                self.paddle.vx = 0
