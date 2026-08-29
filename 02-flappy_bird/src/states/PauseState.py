"""
#
Course: ISPPV1 I2026

"""

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings


class PauseState(BaseState):
    options = ["Resume", "Mode Menu", "Quit"]

    def enter(self, **enter_params: dict) -> None:
        self.bird = enter_params["bird"]
        self.world = enter_params["world"]
        self.score = enter_params["score"]
        self.mode = enter_params.get("mode", "normal")
        self.selected_option = 0

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "down" and input_data.pressed:
            settings.SOUNDS["selection"].play()
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif input_id == "up" and input_data.pressed:
            settings.SOUNDS["selection"].play()
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif input_id == "confirm" and input_data.pressed:
            if self.selected_option == 0:  # Resume the game
                self.state_machine.change(
                    "count_down",
                    bird=self.bird,
                    world=self.world,
                    score=self.score,
                    mode=self.mode,
                )
            elif self.selected_option == 1:  # Return to the mode menu
                pygame.mixer.music.load(settings.BASE_DIR / "assets" / "sounds" / "marios_way.ogg")
                pygame.mixer.music.play(loops=-1)
                self.state_machine.change("title")
            elif self.selected_option == 2:  # Exit the game
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        # Draw the PlayState world
        self.world.render(surface)
        self.bird.render(surface)

        # Title and menu
        render_text(
            surface,
            "PAUSE",
            settings.FONTS["flappy"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 3,
            (255, 255, 255),
            center=True,
        )
        
        start_y = (settings.VIRTUAL_HEIGHT // 2) + 20
        for index, option in enumerate(self.options):
            color = (
                (255, 255, 0)
                if index == self.selected_option
                else (255, 255, 255)
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
