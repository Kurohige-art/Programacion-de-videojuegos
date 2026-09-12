"""
ISPPV1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class to define the Play state.
"""

import random

import pygame

from gale.factory import AbstractFactory
from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text

import settings
import src.powerups


class PlayState(BaseState):
    def enter(self, **params: dict):
        self.level = params["level"]
        self.score = params["score"]
        self.lives = params["lives"]
        self.paddle = params["paddle"]
        self.balls = params["balls"]
        self.brickset = params["brickset"]
        self.live_factor = params["live_factor"]
        self.points_to_next_live = params["points_to_next_live"]
        self.points_to_next_grow_up = (
            self.score
            + settings.PADDLE_GROW_UP_POINTS * (self.paddle.size + 1) * self.level
        )
        self.powerups = params.get("powerups", [])
        self.capture_available = params.get("capture_available", False)
        self.captured_ball = params.get("captured_ball")
        self.capture_timer = params.get("capture_timer", 0)
        self.capture_x_offset = params.get("capture_x_offset", 0)
        self.cannon_projectiles = params.get("cannon_projectiles", [])

        if not params.get("resume", False):
            self.balls[0].vx = random.randint(-80, 80)
            self.balls[0].vy = random.randint(-170, -100)
            settings.SOUNDS["paddle_hit"].play()

        self.powerups_abstract_factory = AbstractFactory("src.powerups")

    def update(self, dt: float) -> None:
        self.paddle.update(dt)

        for ball in self.balls:
            if ball is self.captured_ball:
                continue

            ball.update(dt)
            ball.solve_world_boundaries()

            # Check collision with the paddle
            if ball.collides(self.paddle):
                if (
                    self.capture_available
                    and self.captured_ball is None
                    and ball.vy > 0
                ):
                    self.capture_ball(ball)
                    continue

                self.rebound_from_paddle(ball)

            # Check collision with brickset
            if not ball.collides(self.brickset):
                continue

            brick = self.brickset.get_colliding_brick(ball.get_collision_rect())

            if brick is None:
                continue

            brick.hit()
            self.score += brick.score()
            ball.rebound(brick)

            # Check earn life
            if self.score >= self.points_to_next_live:
                settings.SOUNDS["life"].play()
                self.lives = min(3, self.lives + 1)
                self.live_factor += 0.5
                self.points_to_next_live += settings.LIVE_POINTS_BASE * self.live_factor

            # Check growing up of the paddle
            if self.score >= self.points_to_next_grow_up:
                settings.SOUNDS["grow_up"].play()
                self.points_to_next_grow_up += (
                    settings.PADDLE_GROW_UP_POINTS * (self.paddle.size + 1) * self.level
                )
                self.paddle.inc_size()

            # Chance to generate a power-up
            if random.random() < 0.1:
                r = brick.get_collision_rect()
                powerup_name = random.choice(
                    ("CaptureBall", "ExtraLife", "TwoMoreBall", "Cannon")
                )
                self.powerups.append(
                    self.powerups_abstract_factory.get_factory(powerup_name).create(
                        r.centerx - 8, r.centery - 8
                    )
                )

        if self.captured_ball is not None:
            self.capture_timer += dt
            self.update_captured_ball()
            if self.capture_timer >= 5:
                self.launch_captured_ball()

        # Removing all balls that are not in play
        self.balls = [ball for ball in self.balls if ball.active]

        self.brickset.update(dt)

        for projectile in self.cannon_projectiles:
            projectile.update(dt)
            if projectile.exploding or not projectile.active:
                continue

            brick = self.brickset.get_colliding_brick(projectile.get_collision_rect())
            if brick is not None:
                brick.hit()
                self.score += brick.score()
                settings.SOUNDS["explosion"].play()
                projectile.hit()

        self.cannon_projectiles = [
            projectile for projectile in self.cannon_projectiles if projectile.active
        ]

        if not self.balls:
            self.lives -= 1
            if self.lives == 0:
                self.state_machine.change("game_over", score=self.score)
            else:
                for powerup in self.powerups:
                    powerup.active = False
                self.powerups.clear()
                self.catch_ball_timer = 0.0
                self.catch_ball_ready = False
                self.cannons_active = False
                self.paddle.dec_size()
                self.state_machine.change(
                    "serve",
                    level=self.level,
                    score=self.score,
                    lives=self.lives,
                    paddle=self.paddle,
                    brickset=self.brickset,
                    points_to_next_live=self.points_to_next_live,
                    live_factor=self.live_factor,
                    powerups=self.powerups,
                    catch_ball_timer=self.catch_ball_timer,
                    catch_ball_ready=self.catch_ball_ready,
                    cannons_active=self.cannons_active,
                    cannon_projectiles=self.cannon_projectiles,
                )

        # Update powerups
        for powerup in self.powerups:
            powerup.update(dt)

            if powerup.collides(self.paddle):
                powerup.take(self)

            if hasattr(powerup, "collected") and powerup.collected:
                powerup.paddle_width = self.paddle.width
                powerup.x = self.paddle.x
                powerup.y = self.paddle.y

        # Remove powerups that are not in play
        self.powerups = [p for p in self.powerups if p.active]

        # Check victory
        if self.brickset.size == 1 and next(
            (True for _, b in self.brickset.bricks.items() if b.broken), False
        ):
            self.state_machine.change(
                "victory",
                lives=self.lives,
                level=self.level,
                score=self.score,
                paddle=self.paddle,
                balls=self.balls,
                points_to_next_live=self.points_to_next_live,
                live_factor=self.live_factor,
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

        for ball in self.balls:
            ball.render(surface)

        if self.cannons_active:
            pygame.draw.rect(
                surface,
                (255, 220, 80),
                pygame.Rect(self.paddle.x + 2, self.paddle.y - 6, 6, 8),
            )
            pygame.draw.rect(
                surface,
                (255, 220, 80),
                pygame.Rect(
                    self.paddle.x + self.paddle.width - 8,
                    self.paddle.y - 6,
                    6,
                    8,
                ),
            )

        for powerup in self.powerups:
            powerup.render(surface)

        for projectile in self.cannon_projectiles:
            projectile.render(surface)

    def on_input(self, input_id: str, input_data: InputData) -> None:
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
        elif input_id == "fire_cannons" and input_data.pressed:
            for powerup in self.powerups:
                if hasattr(powerup, "fire"):
                    powerup.fire(self)
        elif input_id == "pause" and input_data.pressed:
            if self.captured_ball is not None:
                self.launch_captured_ball()
                return

            self.state_machine.change(
                "pause",
                level=self.level,
                score=self.score,
                lives=self.lives,
                paddle=self.paddle,
                balls=self.balls,
                brickset=self.brickset,
                points_to_next_live=self.points_to_next_live,
                live_factor=self.live_factor,
                powerups=self.powerups,
                capture_available=self.capture_available,
                cannon_projectiles=self.cannon_projectiles,
            )
        elif input_id == "move_up" and input_data.pressed:
            for powerup in self.powerups:
                if hasattr(powerup, "fire"):
                    powerup.fire(self)

    def rebound_from_paddle(self, ball) -> None:
        settings.SOUNDS["paddle_hit"].stop()
        settings.SOUNDS["paddle_hit"].play()
        ball.rebound(self.paddle)
        ball.push(self.paddle)

    def capture_ball(self, ball) -> None:
        self.capture_available = False
        self.captured_ball = ball
        self.capture_timer = 0
        self.capture_x_offset = ball.x - self.paddle.x
        ball.vx = 0
        ball.vy = 0
        self.update_captured_ball()

    def update_captured_ball(self) -> None:
        self.captured_ball.x = self.paddle.x + self.capture_x_offset
        self.captured_ball.y = self.paddle.y - self.captured_ball.height

    def launch_captured_ball(self) -> None:
        if self.captured_ball is None:
            return

        self.update_captured_ball()
        self.captured_ball.vx = random.randint(-80, 80)
        self.captured_ball.vy = random.randint(-170, -100)
        settings.SOUNDS["paddle_hit"].play()
        self.captured_ball = None
        self.capture_timer = 0
