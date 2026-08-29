"""
#
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class TitleScreenState.
"""

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.World import World
from src.Strategy import MenuStrategy


class TitleScreenState(BaseState):
    options = ["normal_mode", "hard_mode"]

    def enter(self) -> None:
        self.world = World()
        self.menu_strategy = MenuStrategy()
        self.selected_option = 0

    def update(self, dt: float) -> None:
        self.world.update_with_strategy(dt, self.menu_strategy)

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        render_text(
            surface,
            "Flappy Bird",
            settings.FONTS["flappy"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 3,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )
        render_text(
            surface,
            "Menu",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH / 2,
            2 * settings.VIRTUAL_HEIGHT / 3 - 10,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )

        for index, option in enumerate(self.options):
            color = (
                (255, 255, 0)
                if index == self.selected_option
                else settings.COLOR_WHITE
            )
            render_text(
                surface,
                option.replace("_", " ").title(),
                settings.FONTS["medium"],
                settings.VIRTUAL_WIDTH / 2,
                2 * settings.VIRTUAL_HEIGHT / 3 + 10 + index * 20,
                color,
                center=True,
                shadowed=True,
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
                self.state_machine.change("count_down", mode="normal")
            else:
                self.state_machine.change("count_down", mode="hard")
