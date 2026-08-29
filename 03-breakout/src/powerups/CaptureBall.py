"""
This file contains the specialization of PowerUp to capture a ball.
"""

from typing import TypeVar

from src.powerups.PowerUp import PowerUp


class CaptureBall(PowerUp):
    """
    Power-up to capture the ball on the next paddle collision.
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 9)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        play_state.capture_available = True
        self.active = False