"""
ISPPV1 2023
Study Case: Pong

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class TitleState.
"""

import random

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.rendering import render_table


class TitleState(BaseState):
    def enter(self, pong) -> None:
        self.pong = pong

    def render(self, surface: pygame.Surface) -> None:
        render_table(surface, self.pong)
        render_text(
            surface,
            "Choose game mode",
            settings.FONTS["large"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2 - 40,
            settings.COLOR_WHITE,
            center=True,
        )
        render_text(
            surface,
            "Press 1 to Human vs Human",
            settings.FONTS["large"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2 - 20,
            settings.COLOR_WHITE,
            center=True
        )
        render_text(surface,
        "Press 2 to Human (Paddle left) vs IA",
        settings.FONTS["options"],
        settings.VIRTUAL_WIDTH / 2,
        settings.VIRTUAL_HEIGHT / 2,
        settings.COLOR_WHITE,
        center=True
        )
        render_text(surface,
        "Press 3 to IA vs HHuman (Paddle right)",
        settings.FONTS["options"],
        settings.VIRTUAL_WIDTH / 2,
        settings.VIRTUAL_HEIGHT / 2 + 15,
        settings.COLOR_WHITE,
        center=True
        )
        render_text(surface,
        "Press 4 to IA vs IA",
        settings.FONTS["options"],
        settings.VIRTUAL_WIDTH / 2,
        settings.VIRTUAL_HEIGHT / 2 + 30,
        settings.COLOR_WHITE,
        center=True
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "mode_1" and input_data.pressed:
            self._start_game()
        elif input_id == "mode_2" and input_data.pressed:
            self.pong.player2.is_ai = True
            self._start_game()
        elif input_id == "mode_3" and input_data.pressed:
            self.pong.player1.is_ai = True
            self._start_game()
        elif input_id == "mode_4" and input_data.pressed:
            self.pong.player1.is_ai = True
            self.pong.player2.is_ai = True
            self._start_game()

    def _start_game(self) -> None:
        self.pong.serving_player = random.randint(1, 2)
        self.state_machine.change("serve", pong=self.pong)
