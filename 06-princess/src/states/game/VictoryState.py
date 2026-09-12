"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class VictoryState.
"""

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings


class VictoryState(BaseState):
    def __init__(self, state_machine) -> None:
        super().__init__(state_machine)
        self.selected_option = 0
        self.options = ["Main Menu", "Quit"]

    def enter(self) -> None:
        self.selected_option = 0
        pygame.mixer.music.load(settings.MUSIC["start"])
        pygame.mixer.music.play(loops=-1)

    def exit(self) -> None:
        pygame.mixer.music.stop()

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        if input_id == "move_up":
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif input_id == "move_down":
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif input_id == "enter":
            if self.selected_option == 0:
                self.state_machine.change("start")
            elif self.selected_option == 1:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    def render(self, surface: pygame.Surface) -> None:
        background = settings.TEXTURES["background"]
        surface.blit(
            pygame.transform.scale(background, (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)),
            (0, 0),
        )

        render_text(
            surface,
            "YOU WIN!",
            settings.FONTS["princess"],
            settings.VIRTUAL_WIDTH / 2 + 2,
            settings.VIRTUAL_HEIGHT / 2 - 40,
            settings.COLOR_TITLE_SHADOW,
            center=True,
        )
        render_text(
            surface,
            "YOU WIN!",
            settings.FONTS["princess"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2 - 42,
            settings.COLOR_TITLE,
            center=True,
        )

        for i, option in enumerate(self.options):
            color = settings.COLOR_TITLE if i == self.selected_option else settings.COLOR_WHITE
            render_text(
                surface,
                option,
                settings.FONTS["princess-small"],
                settings.VIRTUAL_WIDTH / 2,
                settings.VIRTUAL_HEIGHT / 2 + 20 + i * 30,
                color,
                center=True,
            )
