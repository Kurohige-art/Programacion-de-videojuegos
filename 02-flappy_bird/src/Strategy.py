#
import random

import pygame

import settings
from src.LogPair import LogPair
from src.PowerUpFactory import PowerUpFactory


class MenuStrategy:
    """Strategy used to animate the menu background."""

    def spawn_logs(self, world, dt):
        pass

    def update_world(self, world, dt):
        pass


class NormalModeStrategy:
    def apply_input(self, bird, input_id, input_data):
        if input_id == "jump" and input_data.pressed:
            bird.jump()

    def update_bird(self, bird, dt):
        pass

    def spawn_logs(self, world, dt):
        world.logs_spawn_timer += dt
        if world.logs_spawn_timer >= settings.TIME_TO_SPAWN_LOGS:
            world.logs_spawn_timer = 0.0
            y = max(
                -settings.LOG_HEIGHT + 10,
                min(
                    world.last_log_y + random.randint(-20, 20),
                    settings.VIRTUAL_HEIGHT + 90 - settings.LOG_HEIGHT,
                ),
            )
            world.last_log_y = y
            world.logs.append(
                world.log_pair_factory.create(settings.VIRTUAL_WIDTH, y)
            )

    def update_world(self, world, dt):
        for log in world.logs:
            log.update(dt)

    def check_collisions(self, world, bird):
        return world.collides(bird.get_rect())

    def render(self, surface):
        pass


class HardModeStrategy:
    def __init__(self):
        self.current_spawn_time = random.uniform(1.2, 2.5)
        self.powerups = []
        self.powerup_timer = 0.0

    def apply_input(self, bird, input_id, input_data):
        if input_id == "jump" and input_data.pressed:
            bird.jump()
        elif input_id == "left":
            bird.vx = -150 if input_data.pressed else 0
        elif input_id == "right":
            bird.vx = 150 if input_data.pressed else 0

    def update_bird(self, bird, dt):
        pass

    def spawn_logs(self, world, dt):
        world.logs_spawn_timer += dt
        if world.logs_spawn_timer >= self.current_spawn_time:
            world.logs_spawn_timer = 0.0

            self.current_spawn_time = settings.TIME_TO_SPAWN_LOGS * random.uniform(0.8, 1.5)
            gap = settings.LOGS_GAP * random.uniform(0.7, 1.3)

            y = max(
                -settings.LOG_HEIGHT + 10,
                min(
                    world.last_log_y + random.randint(-30, 30),
                    settings.VIRTUAL_HEIGHT + gap - settings.LOG_HEIGHT,
                ),
            )
            world.last_log_y = y

            is_moving = random.random() < 0.35

            log_pair = LogPair(
                settings.VIRTUAL_WIDTH, y, is_moving=is_moving, gap=gap
            )
            world.logs.append(log_pair)

            if self.powerup_timer > 7.0 and random.random() < 0.6:
                self.powerup_timer = 0.0
                position = self._random_free_powerup_position(world)
                if position is not None:
                    x, y = position
                    self.powerups.append(
                        PowerUpFactory.create_ghost_powerup(x=x, y=y)
                    )

    @staticmethod
    def _random_free_powerup_position(world):
        right_side_start = settings.VIRTUAL_WIDTH
        right_side_end = settings.VIRTUAL_WIDTH + settings.LOG_WIDTH + 30

        for _ in range(100):
            x = random.randint(right_side_start, right_side_end)
            y = random.randint(0, settings.VIRTUAL_HEIGHT - 30)
            skull_rect = pygame.Rect(x, y, 30, 30)
            if not any(
                log_pair.collides(skull_rect) for log_pair in world.logs
            ):
                return x, y

        return None

    def update_world(self, world, dt):
        for log in world.logs:
            log.update(dt)

        self.powerup_timer += dt
        bird_rect = world.bird.get_rect()
        for p in self.powerups:
            p.update(dt)
            if p.is_active and p.rect.colliderect(bird_rect):
                PowerUpFactory.destroy_powerup(p)
                world.bird.ghost_mode = True
                world.bird.ghost_timer = 6.0
                world.bird.ghost_blink_timer = 0.0
                pygame.mixer.music.load(str(settings.SOUNDS_PATHS["hell"]))
                pygame.mixer.music.play(loops=-1)

        self.powerups = [
            powerup
            for powerup in self.powerups
            if powerup.is_active and powerup.x > -50
        ]

    def check_collisions(self, world, bird):
        bird_rect = bird.get_rect()
        if bird_rect.bottom >= settings.VIRTUAL_HEIGHT:
            return True

        if bird.ghost_mode:
            return False

        return world.collides(bird_rect)

    def render(self, surface):
        for p in self.powerups:
            p.render(surface)
