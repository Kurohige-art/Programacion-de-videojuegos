import pygame

import settings


class CannonProjectile:
    SPEED = 180
    EXPLOSION_TIME = 0.08

    def __init__(self, x: float, y: float, direction: int) -> None:
        self.x = x
        self.y = y
        self.width = 28
        self.height = 8
        self.direction = direction
        self.active = True
        self.exploding = False
        self.explosion_frame = 0
        self.explosion_timer = 0

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, dt: float) -> None:
        if self.exploding:
            self.explosion_timer += dt
            self.explosion_frame = int(self.explosion_timer / self.EXPLOSION_TIME)
            if self.explosion_frame >= len(settings.FRAMES["cannon"]["explosion"]):
                self.active = False
            return

        self.y -= self.SPEED * dt
        if self.y + self.height < 0:
            self.active = False

    def hit(self) -> None:
        self.exploding = True
        self.explosion_timer = 0
        self.explosion_frame = 0

    def render(self, surface: pygame.Surface) -> None:
        if self.exploding:
            frame = settings.FRAMES["cannon"]["explosion"][self.explosion_frame]
            surface.blit(settings.TEXTURES["spritesheet_canon"], (self.x, self.y), frame)
            return

        frame = settings.FRAMES["cannon"]["missile"][0]
        missile = settings.TEXTURES["spritesheet_canon"].subsurface(frame).copy()
        rotated = pygame.transform.rotate(missile, 90)
        surface.blit(rotated, (self.x, self.y))