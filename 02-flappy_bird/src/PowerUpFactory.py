import pygame

import settings


class GhostPowerUp:
    def __init__(self, log_pair=None, x: float = 0, y: float = 0) -> None:
        self.log_pair = log_pair
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.is_active = True
        if self.log_pair is not None:
            self._update_position()
            self._static_y = self.y

    def _update_position(self) -> None:
        top_log = self.log_pair.get_top_rect()
        bottom_log = self.log_pair.get_bottom_rect()
        gap_center_y = (top_log.bottom + bottom_log.top) / 2
        self.x = self.log_pair.x + (settings.LOG_WIDTH - self.width) / 2
        self.y = gap_center_y - self.height / 2
        self.rect.topleft = (round(self.x), round(self.y))

    def update(self, dt: float) -> None:
        if self.log_pair is not None:
            self.x = self.log_pair.x + (settings.LOG_WIDTH - self.width) / 2
            self.y = self._static_y
            self.rect.topleft = (round(self.x), round(self.y))
            out_of_game = self.log_pair.is_out_of_game()
        else:
            self.x += -settings.MAIN_SCROLL_SPEED * dt
            self.rect.x = round(self.x)
            out_of_game = self.x < -self.width

        if out_of_game:
            self.is_active = False

    def render(self, surface: pygame.Surface) -> None:
        if self.is_active:
            surface.blit(settings.TEXTURES["skull"], self.rect)


class PowerUpFactory:
    @staticmethod
    def create_ghost_powerup(log_pair=None, x: float = 0, y: float = 0):
        return GhostPowerUp(log_pair, x, y)

    @staticmethod
    def destroy_powerup(powerup: GhostPowerUp) -> None:
        powerup.is_active = False
