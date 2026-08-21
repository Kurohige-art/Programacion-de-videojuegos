"""
Actividad 2 Ricardo Felzani Olmedillo

Curso: ISPPV1 I2026

"""

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings


class PauseState(BaseState):
    options = ["Resume", "Restart", "Quit"]

    def enter(self, **enter_params: dict) -> None:
        self.bird = enter_params["bird"]
        self.world = enter_params["world"]
        self.score = enter_params["score"]
        self.selected_option = 0

    def on_input(self, input_id: str, input_data: InputData) -> None:
       
            if input_id == "down" and input_data.pressed:
                settings.SOUNDS["score"].play()
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif input_id == "up" and input_data.pressed:
                settings.SOUNDS["score"].play()
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif input_id == "confirm" and input_data.pressed:
                if self.selected_option == 0:  # Resume
                    self.state_machine.change(
                        "count_down",
                        bird=self.bird,
                        world=self.world,
                        score=self.score
                    )
                elif self.selected_option == 1:  # Restart
                    self.state_machine.change("count_down")
                elif self.selected_option == 2:  # Quit
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        # Dibujamos el mundo (incluye troncos) y el pájaro
        self.world.render(surface)
        self.bird.render(surface)
        
        # Título y menú
        render_text(surface, "PAUSE", settings.FONTS["flappy"], settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 3, (255, 255, 255), center=True)
        start_y = (settings.VIRTUAL_HEIGHT // 2) + 20
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
            render_text(surface, option, settings.FONTS["medium"], settings.VIRTUAL_WIDTH // 2, start_y + (i * 30), color, center=True)