"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

This file contains the class StatusMenuState: the party member selection
menu available while exploring the world.
"""

from typing import Any

import pygame

import settings
from gale.state import BaseState
from src.gui.Menu import Menu


class StatusMenuState(BaseState):
    def enter(self, play_state: Any) -> None:
        self.play_state = play_state
        characters = list(play_state.world.party.characters.values())
        items = [
            (character.name, self._open_character(character))
            for character in characters
        ]
        items.append(("Exit", self.close))
        self.menu = Menu(
            settings.VIRTUAL_WIDTH / 2 - 72,
            20,
            144,
            184,
            items=items,
            font=settings.FONTS["small"],
        )

    def _open_character(self, character: Any) -> Any:
        return lambda: self._show_character(character)

    def _show_character(self, character: Any) -> None:
        from src.states.game.CharacterStatusState import CharacterStatusState

        self.state_machine.push(
            CharacterStatusState(self.state_machine),
            play_state=self.play_state,
            character=character,
        )

    def close(self) -> None:
        self.state_machine.pop()

    def update(self, dt: float) -> None:
        self.menu.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed:
            return

        if input_id == "move_up":
            self.menu.navigate((0, -1))
        elif input_id == "move_down":
            self.menu.navigate((0, 1))
        elif input_id == "enter":
            self.menu.confirm()

    def render(self, surface: pygame.Surface) -> None:
        self.menu.render(surface)