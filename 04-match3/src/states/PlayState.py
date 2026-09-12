"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

import math
from typing import Dict, Any, List, Optional, Tuple

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings
from src.Tile import Tile


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params["level"]
        self.board = enter_params["board"]
        self.score = enter_params["score"]

        # Position in the grid which we are highlighting
        self.board_highlight_i1 = -1
        self.board_highlight_j1 = -1
        self.board_highlight_i2 = -1
        self.board_highlight_j2 = -1

        self.highlighted_tile = False
        self.dragged_tile = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.previous_mouse_position = None
        self.idle_time = 0
        self.suggested_tiles: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None
        self.suggestion_time = 0

        self.active = True
        self.powerup_animations: List[Dict[str, Any]] = []
        self.current_powerup_animation: Optional[Dict[str, Any]] = None

        # TEMPORARY DEBUG MODE: remove once the power-up logic is fully validated.
        # Hold Shift or Ctrl while clicking a tile to change its color for testing.
        self.debug_tile_color_cycle = True

        self.timer = settings.LEVEL_TIME

        self.goal_score = self.level * 1.25 * 1000

        # A surface that supports alpha to highlight a selected tile
        self.tile_alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.tile_alpha_surface,
            (255, 255, 255, 96),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )

        # A surface that supports alpha to draw behind the text.
        self.text_alpha_surface = pygame.Surface((212, 136), pygame.SRCALPHA)
        pygame.draw.rect(
            self.text_alpha_surface, (56, 56, 56, 234), pygame.Rect(0, 0, 212, 136)
        )

        def decrement_timer():
            if self.current_powerup_animation is not None or self.powerup_animations:
                return

            self.timer -= 1

            # Play warning sound on timer if we get low
            if self.timer <= 5:
                settings.SOUNDS["clock"].play()

        Timer.every(1, decrement_timer)

    def update(self, _: float) -> None:
        delta_time = _

        if self.current_powerup_animation is None and self.powerup_animations:
            self.current_powerup_animation = self.powerup_animations.pop(0)

        if self.current_powerup_animation is not None:
            animation = self.current_powerup_animation
            animation["timer"] += delta_time
            if animation["timer"] >= 0.08:
                animation["timer"] = 0.0
                animation["frame_index"] += 1
                if animation["frame_index"] >= len(animation["frames"]):
                    tile = animation["tile"]
                    if tile is not None:
                        if animation["type"] == Tile.POWERUP_LINE:
                            settings.SOUNDS["lightning"].play()
                        elif animation["type"] == Tile.POWERUP_COLOR_BOMB:
                            settings.SOUNDS["bomb"].play()
                        self.board.tiles[tile.i][tile.j] = None

                    self.current_powerup_animation = None
                    if not self.powerup_animations:
                        self.active = True
                        falling_tiles = self.board.get_falling_tiles()
                        if falling_tiles:
                            Timer.tween(
                                0.25,
                                falling_tiles,
                                on_finish=lambda: self._calculate_matches(
                                    [item[0] for item in falling_tiles],
                                    last_moved=falling_tiles[-1][0]
                                    if falling_tiles
                                    else None,
                                ),
                            )

        if self.active and self.dragged_tile is None:
            self.idle_time += delta_time
            if self.idle_time >= 3 and self.suggested_tiles is None:
                self.suggested_tiles = self._find_suggestion()
        self.suggestion_time += delta_time

        if self.timer <= 0:
            Timer.clear()
            settings.SOUNDS["game-over"].play()
            self.state_machine.change("game-over", score=self.score)

        if self.score >= self.goal_score:
            if self.current_powerup_animation is not None or self.powerup_animations:
                return

            active_powerups = self._get_active_powerups()
            if active_powerups:
                for tile in active_powerups:
                    self._queue_powerup_animation(tile)
                return

            Timer.clear()
            settings.SOUNDS["next-level"].play()
            self.state_machine.change("begin", level=self.level + 1, score=self.score)

    def render(self, surface: pygame.Surface) -> None:
        self.board.render(surface)

        if self.current_powerup_animation is not None:
            animation = self.current_powerup_animation
            frame_index = min(animation["frame_index"], len(animation["frames"]) - 1)
            frame = animation["frames"][frame_index]
            tile = animation["tile"]
            sprite = (
                settings.TEXTURES["spritesheet_bomb"]
                if animation["type"] == "color_bomb"
                else settings.TEXTURES["spritesheet_lightning"]
            )
            x = tile.x + self.board.x + (settings.TILE_SIZE - frame.width) // 2
            y = tile.y + self.board.y + (settings.TILE_SIZE - frame.height) // 2
            surface.blit(sprite, (x, y), frame)

        if self.suggested_tiles is not None and self.dragged_tile is None:
            suggestion_alpha = 80 + int(
                (math.sin(self.suggestion_time * 7) + 1) * 88
            )
            self.tile_alpha_surface.set_alpha(suggestion_alpha)
            for i, j in self.suggested_tiles:
                surface.blit(
                    self.tile_alpha_surface,
                    (
                        j * settings.TILE_SIZE + self.board.x,
                        i * settings.TILE_SIZE + self.board.y,
                    ),
                )

        if self.highlighted_tile:
            self.tile_alpha_surface.set_alpha(255)
            x = self.highlighted_j1 * settings.TILE_SIZE + self.board.x
            y = self.highlighted_i1 * settings.TILE_SIZE + self.board.y
            if self.dragged_tile is not None:
                x = self.dragged_tile.x + self.board.x
                y = self.dragged_tile.y + self.board.y
            surface.blit(self.tile_alpha_surface, (x, y))

        surface.blit(self.text_alpha_surface, (16, 16))
        render_text(
            surface,
            f"Level: {self.level}",
            settings.FONTS["medium"],
            30,
            24,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["medium"],
            30,
            52,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Goal: {self.goal_score}",
            settings.FONTS["medium"],
            30,
            80,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Timer: {self.timer}",
            settings.FONTS["medium"],
            30,
            108,
            (99, 155, 255),
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not self.active:
            return

        if input_id == "click":
            self.idle_time = 0
            self.suggested_tiles = None
            if input_data.pressed:
                self._start_drag(input_data.position)
            elif input_data.released:
                self._finish_drag(input_data.position)
        elif input_id == "click_motion" and self.dragged_tile is not None:
            self.idle_time = 0
            self.suggested_tiles = None
            position = self._mouse_to_virtual(input_data.position)
            self._move_dragged_tile(input_data.position)
            self.previous_mouse_position = position

    def _mouse_to_virtual(self, position) -> tuple:
        return (
            position[0] * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH,
            position[1] * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT,
        )

    def _get_tile_position(self, position) -> tuple:
        pos_x, pos_y = self._mouse_to_virtual(position)
        return (
            (pos_y - self.board.y) // settings.TILE_SIZE,
            (pos_x - self.board.x) // settings.TILE_SIZE,
        )

    def _debug_cycle_tile_color(self, tile) -> None:
        if tile is None:
            return

        next_color = (tile.color + 1) % settings.NUM_COLORS
        tile.color = next_color
        tile.variety = (tile.variety + 1) % settings.NUM_VARIETIES

    def _start_drag(self, position) -> None:
        i, j = self._get_tile_position(position)
        if not (0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH):
            return

        tile = self.board.tiles[i][j]
        if tile is not None and tile.powerup_type is not None:
            self._activate_powerup(tile)
            return

        modifier_pressed = bool(
            pygame.key.get_mods() & (pygame.KMOD_SHIFT | pygame.KMOD_CTRL)
        )
        if self.debug_tile_color_cycle and modifier_pressed:
            self._debug_cycle_tile_color(tile)
            return

        pos_x, pos_y = self._mouse_to_virtual(position)
        self.dragged_tile = tile
        self.drag_offset_x = pos_x - self.board.x - tile.x
        self.drag_offset_y = pos_y - self.board.y - tile.y
        self.highlighted_tile = True
        self.highlighted_i1 = i
        self.highlighted_j1 = j
        self.previous_mouse_position = (pos_x, pos_y)
        self._move_dragged_tile(position)

    def _move_dragged_tile(self, position) -> None:
        pos_x, pos_y = self._mouse_to_virtual(position)
        self.dragged_tile.x = pos_x - self.board.x - self.drag_offset_x
        self.dragged_tile.y = pos_y - self.board.y - self.drag_offset_y

    def _get_drag_direction(self, position) -> Optional[Tuple[int, int]]:
        previous_x, previous_y = self.previous_mouse_position
        delta_x = position[0] - previous_x
        delta_y = position[1] - previous_y

        if delta_x == 0 and delta_y == 0:
            return None
        if abs(delta_x) >= abs(delta_y):
            return (0, 1 if delta_x > 0 else -1)
        return (1 if delta_y > 0 else -1, 0)

    def _can_drop_on_tile(self, dragged_tile: Tile, target_tile: Tile) -> bool:
        if dragged_tile is None or target_tile is None:
            return False
        if dragged_tile is target_tile:
            return False
        if abs(dragged_tile.i - target_tile.i) + abs(dragged_tile.j - target_tile.j) != 1:
            return False

        drop_i, drop_j = target_tile.i, target_tile.j
        for delta_i, delta_j in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            neighbor_i = drop_i + delta_i
            neighbor_j = drop_j + delta_j
            if not (
                0 <= neighbor_i < settings.BOARD_HEIGHT
                and 0 <= neighbor_j < settings.BOARD_WIDTH
            ):
                continue
            if (neighbor_i, neighbor_j) == (dragged_tile.i, dragged_tile.j):
                continue
            neighbor = self.board.tiles[neighbor_i][neighbor_j]
            if neighbor is not None and neighbor.color == dragged_tile.color:
                return True

        return False

    def _get_hovered_adjacent_tile(self, tile: Tile) -> Optional[Tile]:
        tile_rect = pygame.Rect(
            tile.x, tile.y, settings.TILE_SIZE, settings.TILE_SIZE
        )
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                other = self.board.tiles[i][j]
                if other is None or other is tile:
                    continue
                if abs(tile.i - other.i) + abs(tile.j - other.j) != 1:
                    continue
                other_rect = pygame.Rect(
                    other.x, other.y, settings.TILE_SIZE, settings.TILE_SIZE
                )
                if tile_rect.colliderect(other_rect):
                    return other
        return None

    def _check_adjacent_collision(self, direction: Tuple[int, int]) -> None:
        tile1 = self.dragged_tile
        if tile1 is None:
            return

        i = tile1.i + direction[0]
        j = tile1.j + direction[1]
        if not (0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH):
            return

        tile2 = self.board.tiles[i][j]
        if tile2 is None:
            return

        if self._can_drop_on_tile(tile1, tile2):
            self._try_swap(tile1, tile2)
        else:
            self._return_dragged_tile(tile1)

    def _get_active_powerups(self) -> List[Tile]:
        active_powerups = []
        seen = set()

        for row in self.board.tiles:
            for tile in row:
                if tile is None or tile.powerup_type is None:
                    continue

                tile_id = id(tile)
                if tile_id in seen:
                    continue

                seen.add(tile_id)
                active_powerups.append(tile)

        return active_powerups

    def _find_suggestion(
        self,
    ) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                for next_i, next_j in ((i + 1, j), (i, j + 1)):
                    if (
                        next_i >= settings.BOARD_HEIGHT
                        or next_j >= settings.BOARD_WIDTH
                    ):
                        continue

                    first_can_move = self._can_move_to_match(
                        i, j, next_i, next_j
                    )
                    second_can_move = self._can_move_to_match(
                        next_i, next_j, i, j
                    )
                    adjacent_same_color = self._swap_creates_adjacent_same_color(
                        i, j, next_i, next_j
                    )

                    if first_can_move != second_can_move or adjacent_same_color:
                        moving_tile = (i, j) if first_can_move else (next_i, next_j)
                        target_tile = (next_i, next_j) if first_can_move else (i, j)
                        if adjacent_same_color and not (
                            first_can_move or second_can_move
                        ):
                            moving_tile, target_tile = (i, j), (next_i, next_j)
                        return moving_tile, target_tile

        return None

    def _can_move_to_match(
        self, source_i: int, source_j: int, target_i: int, target_j: int
    ) -> bool:
        color = self.board.tiles[source_i][source_j].color
        matching_neighbors = 0
        neighbor_positions = (
            (target_i - 1, target_j),
            (target_i + 1, target_j),
            (target_i, target_j - 1),
            (target_i, target_j + 1),
        )

        for neighbor_i, neighbor_j in neighbor_positions:
            if not (
                0 <= neighbor_i < settings.BOARD_HEIGHT
                and 0 <= neighbor_j < settings.BOARD_WIDTH
            ):
                continue
            if neighbor_i == source_i and neighbor_j == source_j:
                continue
            if self.board.tiles[neighbor_i][neighbor_j].color == color:
                matching_neighbors += 1

        return matching_neighbors == 2

    def _swap_creates_adjacent_same_color(
        self, source_i: int, source_j: int, target_i: int, target_j: int
    ) -> bool:
        if self.board.tiles[source_i][source_j] is None:
            return False
        if self.board.tiles[target_i][target_j] is None:
            return False

        source_color = self.board.tiles[source_i][source_j].color
        target_color = self.board.tiles[target_i][target_j].color

        def count_same_neighbors(i: int, j: int, color: int) -> int:
            count = 0
            for delta_i, delta_j in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                neighbor_i = i + delta_i
                neighbor_j = j + delta_j
                if not (
                    0 <= neighbor_i < settings.BOARD_HEIGHT
                    and 0 <= neighbor_j < settings.BOARD_WIDTH
                ):
                    continue
                if (neighbor_i, neighbor_j) in ((source_i, source_j), (target_i, target_j)):
                    continue
                neighbor = self.board.tiles[neighbor_i][neighbor_j]
                if neighbor is not None and neighbor.color == color:
                    count += 1
            return count

        return (
            1 <= count_same_neighbors(source_i, source_j, target_color) <= 2
            or 1 <= count_same_neighbors(target_i, target_j, source_color) <= 2
        )

    def _has_matching_neighbor(self, tile, i: int, j: int) -> bool:
        neighbor_positions = (
            (i - 1, j),
            (i + 1, j),
            (i, j - 1),
            (i, j + 1),
        )

        for neighbor_i, neighbor_j in neighbor_positions:
            if not (
                0 <= neighbor_i < settings.BOARD_HEIGHT
                and 0 <= neighbor_j < settings.BOARD_WIDTH
            ):
                continue
            if neighbor_i == tile.i and neighbor_j == tile.j:
                continue
            if self.board.tiles[neighbor_i][neighbor_j].color == tile.color:
                return True

        return False

    def _return_dragged_tile(self, tile) -> None:
        tile.x = tile.j * settings.TILE_SIZE
        tile.y = tile.i * settings.TILE_SIZE
        self.dragged_tile = None
        self.highlighted_tile = False
        settings.SOUNDS["error"].play()

    def _try_swap(self, tile1, tile2) -> bool:
        self.active = False
        self.dragged_tile = None
        self.highlighted_tile = False
        tile1_x = tile1.j * settings.TILE_SIZE
        tile1_y = tile1.i * settings.TILE_SIZE
        tile2_x, tile2_y = tile2.x, tile2.y

        def arrive():
            (
                self.board.tiles[tile1.i][tile1.j],
                self.board.tiles[tile2.i][tile2.j],
            ) = (tile2, tile1)
            tile1.i, tile1.j, tile2.i, tile2.j = (
                tile2.i,
                tile2.j,
                tile1.i,
                tile1.j,
            )
            self._calculate_matches([tile1, tile2], last_moved=tile1)

        Timer.tween(
            0.25,
            [
                (tile1, {"x": tile2_x, "y": tile2_y}),
                (tile2, {"x": tile1_x, "y": tile1_y}),
            ],
            on_finish=arrive,
        )
        return True

    def _finish_drag(self, position) -> None:
        if self.dragged_tile is None:
            return

        tile1 = self.dragged_tile
        self._move_dragged_tile(position)
        target_tile = self._get_hovered_adjacent_tile(tile1)

        if target_tile is None:
            self.dragged_tile = None
            self.highlighted_tile = False
            self._return_dragged_tile(tile1)
            return

        if not self._can_drop_on_tile(tile1, target_tile):
            self.dragged_tile = None
            self.highlighted_tile = False
            self._return_dragged_tile(tile1)
            return

        self.dragged_tile = None
        self.highlighted_tile = False
        self._try_swap(tile1, target_tile)

    def _queue_powerup_animation(self, tile, source_tile=None, processed=None) -> None:
        if tile is None or tile.powerup_type is None:
            return

        if source_tile is None:
            source_tile = tile
        if processed is None:
            processed = set()

        if tile in processed:
            return
        processed.add(tile)

        targets = self.board.get_powerup_targets(tile)
        if not targets:
            return

        frames = (
            settings.FRAMES["powerup_lightning"]
            if tile.powerup_type == Tile.POWERUP_LINE
            else settings.FRAMES["powerup_bomb"]
        )

        for target in targets:
            if target is None:
                continue

            if target is source_tile:
                if any(
                    animation["tile"] is target for animation in self.powerup_animations
                ):
                    continue
                self.score += 50
                self.powerup_animations.append(
                    {
                        "tile": target,
                        "type": tile.powerup_type,
                        "frames": frames,
                        "frame_index": 0,
                        "timer": 0.0,
                    }
                )
                continue

            if target in processed:
                continue

            if target.powerup_type is not None:
                self._queue_powerup_animation(
                    target,
                    source_tile=target,
                    processed=processed,
                )
                continue

            if any(
                animation["tile"] is target for animation in self.powerup_animations
            ):
                continue

            self.score += 50
            self.powerup_animations.append(
                {
                    "tile": target,
                    "type": tile.powerup_type,
                    "frames": frames,
                    "frame_index": 0,
                    "timer": 0.0,
                }
            )

        self.active = False

    def _calculate_matches(self, tiles: List, last_moved=None) -> None:
        matches = self.board.calculate_matches_for(tiles, last_moved=last_moved)

        if matches is None:
            self.board.recreate_until_playable()
            self.active = True
            return

        settings.SOUNDS["match"].stop()
        settings.SOUNDS["match"].play()

        triggered_powerups = []
        for match in matches:
            self.score += len(match) * 50
            for tile in match:
                if tile is not None and tile.powerup_type is not None:
                    triggered_powerups.append(tile)

        if triggered_powerups:
            for tile in triggered_powerups:
                self._queue_powerup_animation(tile)
            self.board.remove_matches()
            return

        self.board.remove_matches()

        falling_tiles = self.board.get_falling_tiles()

        Timer.tween(
            0.25,
            falling_tiles,
            on_finish=lambda: self._calculate_matches(
                [item[0] for item in falling_tiles],
                last_moved=falling_tiles[-1][0] if falling_tiles else None,
            ),
        )

    def _activate_powerup(self, tile) -> None:
        if tile is None or tile.powerup_type is None:
            return

        self._queue_powerup_animation(tile)
