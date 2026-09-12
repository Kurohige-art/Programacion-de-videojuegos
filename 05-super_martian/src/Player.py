"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Player.
"""

from typing import TypeVar

from gale.input_handler import InputData

from src.GameEntity import GameEntity
from src.states.entities import player_states


class Player(GameEntity):
    def __init__(self, x: int, y: int, game_level: TypeVar("GameLevel")) -> None:
        super().__init__(
            x,
            y,
            16,
            20,
            "martian",
            game_level,
            states={
                "idle": lambda sm: player_states.IdleState(self, sm),
                "walk": lambda sm: player_states.WalkState(self, sm),
                "jump": lambda sm: player_states.JumpState(self, sm),
                "fall": lambda sm: player_states.FallState(self, sm),
                "dead": lambda sm: player_states.DeadState(self, sm),
            },
            animation_defs={
                "idle": {"frames": [0]},
                "walk": {"frames": [9, 10], "interval": 0.15},
                "jump": {"frames": [2]},
            },
        )
        self.score = 0
        self.coins_counter = {54: 0, 55: 0, 61: 0, 62: 0}
        self.climbing = False
        self.climb_direction = 0
        self.ladder_top_locked = False
        self.ladder_top_y = None

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id in ("move_left", "move_right", "jump") and input_data.pressed:
            if input_id in ("move_left", "move_right"):
                self.climbing = False
            if input_id == "jump":
                self.ladder_top_locked = False
        if input_id in ("climb_up", "climb_down") and input_data.pressed:
            self.ladder_top_locked = False
            self.climbing = True
            self.climb_direction = -1 if input_id == "climb_up" else 1
            return
        if input_id in ("climb_up", "climb_down") and input_data.released:
            self.climb_direction = 0
            return
        self.state_machine.on_input(input_id, input_data)
