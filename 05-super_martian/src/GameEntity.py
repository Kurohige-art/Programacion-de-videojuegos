"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the base class GameEntity.
"""

from typing import TypeVar, Dict, Any, Tuple

from gale.state import StateMachine, BaseState
from gale.tilemap import move_and_collide

import settings
from src import mixins


class GameEntity(mixins.DrawableMixin, mixins.AnimatedMixin, mixins.CollidableMixin):
    COLLISION_LAYER = "ground"

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        texture_id: str,
        game_level: TypeVar("GameLevel"),
        states: Dict[str, BaseState],
        animation_defs: Dict[str, Dict[str, Any]],
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vx: float = 0
        self.vy: float = 0
        self.texture_id = texture_id
        self.frame_index = -1
        self.game_level = game_level
        self.tilemap = self.game_level.tilemap
        self.COLLISION_LAYER = self.game_level.collision_layer
        self.on_ground = False
        self.collided_x = False
        self.state_machine = StateMachine(states)
        self.current_animation = None
        self.animations = {}
        self.generate_animations(animation_defs)
        self.flipped = False
        self.is_dead = False

    def change_state(
        self, state_id: str, *args: Tuple[Any], **kwargs: Dict[str, Any]
    ) -> None:
        self.state_machine.change(state_id, *args, **kwargs)

    def update(self, dt: float) -> None:
        ladder_bounds = self.game_level.ladder_bounds(self)
        climbing = getattr(self, "climbing", False) and ladder_bounds is not None
        ladder_top_locked = getattr(self, "ladder_top_locked", False)
        if climbing:
            self.vy = 0
            climb_direction = getattr(self, "climb_direction", 0)
            self.y += climb_direction * settings.PLAYER_CLIMB_SPEED * dt
            if "walk" in self.animations:
                self.change_animation("walk")

            ladder_top, ladder_bottom = ladder_bounds
            if climb_direction < 0 and self.y <= ladder_top - self.height:
                self.y = ladder_top - self.height
                self.climbing = False
                self.ladder_top_locked = True
                self.ladder_top_y = self.y
                ladder_top_locked = True
            elif climb_direction > 0 and self.y + self.height >= ladder_bottom:
                self.y = ladder_bottom - self.height
                self.climbing = False

        if not getattr(self, "climbing", False):
            climbing = False

        if ladder_top_locked and self.ladder_top_y is not None:
            self.y = self.ladder_top_y

        # Applied unconditionally (not just while jumping/falling) so the
        # vertical move below is never a no-op dy=0 call, which would skip
        # move_and_collide's y-axis check and leave on_ground stale.
        if (
            not climbing
            and not ladder_top_locked
            and not getattr(self, "flying", False)
        ):
            self.vy += settings.GRAVITY * dt

        self.state_machine.update(dt)
        mixins.AnimatedMixin.update(self, dt)

        previous_vy = self.vy
        self.x, self.y, self.collided_x, collided_y = move_and_collide(
            self.tilemap,
            self.COLLISION_LAYER,
            self.x,
            self.y,
            self.width,
            self.height,
            self.vx * dt,
            0
            if climbing or ladder_top_locked or getattr(self, "flying", False)
            else self.vy * dt,
        )

        if collided_y:
            if previous_vy < 0:
                self.game_level.on_ceiling_hit(self, previous_vy)
            if self.vy > 0:
                self.on_ground = True
            self.vy = 0
        else:
            self.on_ground = False

        if ladder_top_locked:
            self.on_ground = True

        # Keep the entity from walking off either edge of the world.
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > self.tilemap.pixel_width:
            self.x = self.tilemap.pixel_width - self.width
