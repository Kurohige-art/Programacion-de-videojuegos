"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class GameOverState.
"""

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.Strategy import MenuStrategy


class GameOverState(BaseState):
    options = ["Mode Menu", "Exit Game"]

    def enter(self, **enter_params: dict) -> None:
        self.world = enter_params["world"]
        self.bird = enter_params["bird"]
        self.score = enter_params.get("score", 0)
        self.selected_option = 0
        self.menu_strategy = MenuStrategy()

    def update(self, dt: float) -> None:
        self.world.update_with_strategy(dt, self.menu_strategy)

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface, render_logs=False)

        render_text(
            surface,
            "GAME OVER",
            settings.FONTS["flappy"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 4,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 2 - 20,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )

        start_y = settings.VIRTUAL_HEIGHT // 2 + 20
        for index, option in enumerate(self.options):
            color = (
                (255, 255, 0)
                if index == self.selected_option
                else settings.COLOR_WHITE
            )
            render_text(
                surface,
                option,
                settings.FONTS["medium"],
                settings.VIRTUAL_WIDTH // 2,
                start_y + index * 30,
                color,
                center=True,
            )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        if input_id == "down":
            settings.SOUNDS["selection"].play()
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif input_id == "up":
            settings.SOUNDS["selection"].play()
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif input_id == "confirm":
            if self.selected_option == 0:
                settings.SOUNDS["game_over"].stop()
                pygame.mixer.music.load(settings.BASE_DIR / "assets" / "sounds" / "marios_way.ogg")
                pygame.mixer.music.play(loops=-1)
                self.state_machine.change("title")
            else:
                pygame.event.post(pygame.event.Event(pygame.QUIT))