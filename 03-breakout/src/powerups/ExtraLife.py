"""
This file contains the specialization of PowerUp to add an extra life.
"""

from typing import TypeVar

import settings

from src.powerups.PowerUp import PowerUp


class ExtraLife(PowerUp):
    """
    Power-up to add one life, up to the maximum allowed lives.
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 2)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        settings.SOUNDS["extra_life"].play()

        if play_state.lives < 3:
            play_state.lives += 1

        self.active = False