"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Board.
"""

from typing import List, Optional, Tuple, Any, Dict, Set

import pygame

import random

import settings
from src.Tile import Tile


class Board:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.matches: List[List[Tile]] = []
        self.tiles: List[List[Tile]] = []
        self._initialize_tiles()
        self.recreate_until_playable()

    def render(self, surface: pygame.Surface) -> None:
        for row in self.tiles:
            for tile in row:
                if tile is not None:
                    tile.render(surface, self.x, self.y)

    def _create_powerup(self, tile: Tile, powerup_type: str) -> None:
        if tile is None:
            return

        spawned = Tile(tile.i, tile.j, tile.color, tile.variety)
        spawned.powerup_type = powerup_type
        self.tiles[tile.i][tile.j] = spawned

    def _collect_line_powerup_targets(self, tile: Tile) -> List[Tile]:
        targets: List[Tile] = []
        seen: Set[Tile] = set()

        for axis in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            delta_i, delta_j = axis
            i = tile.i + delta_i
            j = tile.j + delta_j
            while 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:
                candidate = self.tiles[i][j]
                if candidate is not None and candidate not in seen:
                    targets.append(candidate)
                    seen.add(candidate)
                i += delta_i
                j += delta_j

        if tile not in seen:
            targets.append(tile)
            seen.add(tile)

        return targets

    def _collect_color_bomb_targets(self, tile: Tile) -> List[Tile]:
        return [
            candidate
            for row in self.tiles
            for candidate in row
            if candidate is not None and candidate.color == tile.color
        ]

    def get_powerup_targets(self, tile: Tile) -> List[Tile]:
        if tile is None or tile.powerup_type is None:
            return []

        if tile.powerup_type == Tile.POWERUP_LINE:
            return self._collect_line_powerup_targets(tile)
        if tile.powerup_type == Tile.POWERUP_COLOR_BOMB:
            return self._collect_color_bomb_targets(tile)

        return [tile]

    def activate_powerup(self, tile: Tile) -> bool:
        if tile is None or tile.powerup_type is None:
            return False

        targets = self.get_powerup_targets(tile)
        for target in targets:
            if target is not None:
                self.tiles[target.i][target.j] = None

        return True

    def _is_match_generated(self, i: int, j: int, color: int) -> bool:
        if (
            i >= 2
            and self.tiles[i - 1][j].color == color
            and self.tiles[i - 2][j].color == color
        ):
            return True

        return (
            j >= 2
            and self.tiles[i][j - 1].color == color
            and self.tiles[i][j - 2].color == color
        )

    def _initialize_tiles(self) -> None:
        self.tiles = [
            [None for _ in range(settings.BOARD_WIDTH)]
            for _ in range(settings.BOARD_HEIGHT)
        ]
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                color = random.randint(0, settings.NUM_COLORS - 1)
                while self._is_match_generated(i, j, color):
                    color = random.randint(0, settings.NUM_COLORS - 1)

                self.tiles[i][j] = Tile(
                    i, j, color, random.randint(0, settings.NUM_VARIETIES - 1)
                )

    def _calculate_match_rec(self, tile: Tile) -> Set[Tile]:
        if tile in self.in_stack:
            return []

        self.in_stack.add(tile)

        color_to_match = tile.color

        ## Check horizontal match
        h_match: List[Tile] = []

        # Check left
        if tile.j > 0:
            left = max(0, tile.j - 2)
            for j in range(tile.j - 1, left - 1, -1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        # Check right
        if tile.j < settings.BOARD_WIDTH - 1:
            right = min(settings.BOARD_WIDTH - 1, tile.j + 2)
            for j in range(tile.j + 1, right + 1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        ## Check vertical match
        v_match: List[Tile] = []

        # Check top
        if tile.i > 0:
            top = max(0, tile.i - 2)
            for i in range(tile.i - 1, top - 1, -1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        # Check bottom
        if tile.i < settings.BOARD_HEIGHT - 1:
            bottom = min(settings.BOARD_HEIGHT - 1, tile.i + 2)
            for i in range(tile.i + 1, bottom + 1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        match: List[Tile] = []

        if len(h_match) >= 2:
            for t in h_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(v_match) >= 2:
            for t in v_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(match) > 0:
            if tile not in self.in_match:
                self.in_match.add(tile)
                match.append(tile)

        for t in match:
            match += self._calculate_match_rec(t)

        self.in_stack.remove(tile)
        return match

    def calculate_matches_for(
        self, new_tiles: List[Tile], last_moved: Optional[Tile] = None
    ) -> Optional[List[List[Tile]]]:
        self.matches = []
        self.in_match: Set[Tile] = set()
        self.in_stack: Set[Tile] = set()

        for tile in new_tiles:
            if tile in self.in_match:
                continue
            match = self._calculate_match_rec(tile)
            if len(match) > 0:
                self.matches.append(match)

        delattr(self, "in_match")
        delattr(self, "in_stack")

        if last_moved is not None:
            for match in self.matches:
                if last_moved in match and len(match) == 4:
                    self._create_powerup(last_moved, Tile.POWERUP_LINE)
                    match[:] = [tile for tile in match if tile is not last_moved]
                elif last_moved in match and len(match) >= 5:
                    self._create_powerup(last_moved, Tile.POWERUP_COLOR_BOMB)
                    match[:] = [tile for tile in match if tile is not last_moved]

        return self.matches if len(self.matches) > 0 else None

    def has_valid_move(self) -> bool:
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                if self.tiles[i][j] is None:
                    continue
                for next_i, next_j in ((i + 1, j), (i, j + 1)):
                    if next_i >= settings.BOARD_HEIGHT or next_j >= settings.BOARD_WIDTH:
                        continue
                    if self.tiles[next_i][next_j] is None:
                        continue
                    if self._swap_creates_match(i, j, next_i, next_j):
                        return True

        return False

    def _swap_creates_match(
        self, source_i: int, source_j: int, target_i: int, target_j: int
    ) -> bool:
        if self.tiles[source_i][source_j] is None or self.tiles[target_i][target_j] is None:
            return False

        source_color = self.tiles[source_i][source_j].color
        target_color = self.tiles[target_i][target_j].color

        def color_at(i: int, j: int) -> int:
            if i == source_i and j == source_j:
                return target_color
            if i == target_i and j == target_j:
                return source_color
            return self.tiles[i][j].color

        def has_match_at(i: int, j: int) -> bool:
            color = color_at(i, j)
            horizontal = 1
            for offset in (-1, 1):
                neighbor_j = j + offset
                while 0 <= neighbor_j < settings.BOARD_WIDTH and color_at(
                    i, neighbor_j
                ) == color:
                    horizontal += 1
                    neighbor_j += offset

            vertical = 1
            for offset in (-1, 1):
                neighbor_i = i + offset
                while 0 <= neighbor_i < settings.BOARD_HEIGHT and color_at(
                    neighbor_i, j
                ) == color:
                    vertical += 1
                    neighbor_i += offset

            return horizontal >= 3 or vertical >= 3

        return has_match_at(source_i, source_j) or has_match_at(target_i, target_j)

    def has_active_powerups(self) -> bool:
        for row in self.tiles:
            for tile in row:
                if tile is not None and tile.powerup_type is not None:
                    return True
        return False

    def recreate_until_playable(self) -> None:
        if not self.has_valid_move() and not self.has_active_powerups():
            while not self.has_valid_move():
                self._initialize_tiles()
        self.matches = []

    def remove_matches(self) -> None:
        tiles_to_remove: Set[Tile] = set()

        for match in self.matches:
            for tile in match:
                if tile is None:
                    continue
                if tile.powerup_type is not None:
                    continue
                tiles_to_remove.add(tile)

        for tile in tiles_to_remove:
            if tile is not None:
                self.tiles[tile.i][tile.j] = None

        self.matches = []

    def get_falling_tiles(self) -> Tuple[Any, Dict[str, Any]]:
        # List of tweens to create
        tweens: Tuple[Tile, Dict[str, Any]] = []

        # for each column, go up tile by tile until we hit a space
        for j in range(settings.BOARD_WIDTH):
            space = False
            space_i = -1
            i = settings.BOARD_HEIGHT - 1

            while i >= 0:
                tile = self.tiles[i][j]

                # if our previous tile was a space
                if space:
                    # if the current tile is not a space
                    if tile is not None:
                        self.tiles[space_i][j] = tile
                        tile.i = space_i

                        # set its prior position to None
                        self.tiles[i][j] = None

                        tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))
                        space = False
                        i = space_i
                        space_i = -1
                elif tile is None:
                    space = True

                    if space_i == -1:
                        space_i = i

                i -= 1

        # create a replacement tiles at the top of the screen
        for j in range(settings.BOARD_WIDTH):
            for i in range(settings.BOARD_HEIGHT):
                tile = self.tiles[i][j]

                if tile is None:
                    tile = Tile(
                        i,
                        j,
                        random.randint(0, settings.NUM_COLORS - 1),
                        random.randint(0, settings.NUM_VARIETIES - 1),
                    )
                    tile.y -= settings.TILE_SIZE
                    self.tiles[i][j] = tile
                    tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))

        return tweens
