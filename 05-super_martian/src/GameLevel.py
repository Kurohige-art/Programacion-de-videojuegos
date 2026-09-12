"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class GameLevel.
"""

import json
from typing import Any, Dict

import pygame

from gale.tilemap import CollisionType, collision_type_at, load_tiled_map

import settings
from src.Creature import Creature
from src.GameItem import GameItem
from src.definitions import creatures, items


class GameLevel:
    def __init__(self, num_level: int) -> None:
        self.tilemap = load_tiled_map(settings.TILEMAPS[num_level])
        self.raw_object_gids = self.load_object_gids(settings.TILEMAPS[num_level])
        self.collision_layer = next(
            (
                layer_name
                for layer_name in ("ground", "ground0")
                if layer_name in self.tilemap.layer_names()
            ),
        )
        self.creatures = []
        self.items = []
        self.key_block = None
        self.key = None
        self.key_animation = None
        self.key_target_y = None

        self.ladder_tile_ids = {22, 23, 29, 30, 36}

        key_block_objects = self.tilemap.object_layers.get("key_block", [])
        if num_level == 2 and not key_block_objects:
            key_block_objects = [
                {
                    "x": 784,
                    "y": 224,
                    "properties": {
                        "tile_id": 0,
                        "first_gid": 134,
                        "activation_score": 150,
                    },
                }
            ]

        for obj in key_block_objects:
            if isinstance(obj, dict):
                platform_x, platform_y = obj["x"], obj["y"]
                properties = obj["properties"]
            else:
                platform_x, platform_y = self.find_key_platform()
                properties = obj.properties
            self.key_block = {
                "x": platform_x,
                "y": platform_y,
                "row": int(platform_y // self.tilemap.tile_height),
                "col": int(platform_x // self.tilemap.tile_width),
                "tile_id": properties.get("tile_id", 0),
                "first_gid": properties.get("first_gid", 1),
                "activation_score": properties.get("activation_score", 150),
                "active": False,
                "hit": False,
            }

        for index, obj in enumerate(self.tilemap.object_layers.get("creatures", [])):
            raw_gid = self.raw_object_gids.get(("creatures", index))
            self.add_creature(
                {
                    "tile_index": self.creature_tile_index(raw_gid)
                    if raw_gid is not None
                    else obj.properties.get("tile_index", 48),
                    "x": obj.x,
                    "y": obj.y - obj.height,
                    "width": obj.width,
                    "height": obj.height,
                }
            )

        for index, obj in enumerate(self.tilemap.object_layers.get("coins", [])):
            raw_gid = self.raw_object_gids.get(("coins", index))
            frame_index = obj.properties.get(
                "frame_index", self.coin_frame_index(raw_gid)
            )
            if frame_index not in items.ITEMS["coins"]:
                continue
            self.add_item(
                {
                    "item_name": "coins",
                    "frame_index": frame_index,
                    "x": obj.x,
                    "y": obj.y - obj.height,
                    "width": obj.width,
                    "height": obj.height,
                }
            )

    def add_item(self, item_data: Dict[str, Any]) -> None:
        item_name = item_data.pop("item_name")
        definition = items.ITEMS[item_name][item_data["frame_index"]]
        definition.update(item_data)
        self.items.append(GameItem(**definition))

    @staticmethod
    def load_object_gids(path: str) -> Dict[Any, int]:
        with open(path, "r", encoding="utf-8") as map_file:
            map_data = json.load(map_file)

        gids = {}

        def visit_layers(layers: Any) -> None:
            for layer in layers:
                if layer.get("type") == "objectgroup":
                    for index, obj in enumerate(layer.get("objects", [])):
                        if "gid" in obj:
                            gids[(layer["name"], index)] = obj["gid"]
                visit_layers(layer.get("layers", []))

        visit_layers(map_data.get("layers", []))
        return gids

    def add_creature(self, creature_data: Dict[str, Any]) -> None:
        definition = creatures.CREATURES[creature_data["tile_index"]]
        self.creatures.append(
            Creature(
                creature_data["x"],
                creature_data["y"],
                creature_data["width"],
                creature_data["height"],
                self,
                **definition,
            )
        )

    def creature_tile_index(self, gid: Any) -> int:
        if gid is None:
            return 48
        local_index = (gid & 0x1FFFFFFF) - 78
        return max(0, local_index // 8 * 8)

    @staticmethod
    def coin_frame_index(gid: Any) -> int:
        if gid is None:
            return 61
        return gid - 1

    def is_on_ladder(self, entity: Any) -> bool:
        return self.ladder_bounds(entity) is not None

    def has_support_under(self, entity: Any) -> bool:
        row = int((entity.y + entity.height) // self.tilemap.tile_height)
        left = int(entity.x // self.tilemap.tile_width)
        right = int((entity.x + entity.width - 1e-6) // self.tilemap.tile_width)
        return any(
            collision_type_at(self.tilemap, self.collision_layer, row, col)
            in (CollisionType.SOLID, CollisionType.PLATFORM)
            for col in range(left, right + 1)
        )

    def ladder_bounds(self, entity: Any) -> Any:
        center_x = entity.x + entity.width / 2
        center_y = entity.y + entity.height / 2
        row, col = self.tilemap.tile_at(center_x, center_y)
        if not self.tilemap.in_bounds(row, col):
            return None

        ladder_rows = [
            ladder_row
            for ladder_row in range(self.tilemap.rows)
            if self.tilemap.get_gid(
                self.collision_layer, ladder_row, col
            ) in self.ladder_tile_ids
        ]
        if not ladder_rows:
            return None

        ladder_center_x = col * self.tilemap.tile_width + self.tilemap.tile_width / 2
        if abs(center_x - ladder_center_x) > 5:
            return None

        ladder_top = min(ladder_rows) * self.tilemap.tile_height
        ladder_bottom = (max(ladder_rows) + 1) * self.tilemap.tile_height
        if entity.y + entity.height < ladder_top or entity.y > ladder_bottom:
            return None
        return ladder_top, ladder_bottom

    def find_key_platform(self) -> tuple[float, float]:
        grid = self.tilemap.get_layer(self.collision_layer)
        candidates = []

        for row, values in enumerate(grid):
            start = None
            for col in range(self.tilemap.cols + 1):
                occupied = col < self.tilemap.cols and values[col] != 0
                if occupied and start is None:
                    start = col
                elif not occupied and start is not None:
                    width = (col - start) * self.tilemap.tile_width
                    if width > 64:
                        platform_center = (start + col - 1) / 2
                        block_row = row - 3
                        if block_row >= 0:
                            clear_columns = [
                                candidate_col
                                for candidate_col in range(start, col)
                                if all(
                                    grid[clear_row][candidate_col] == 0
                                    for clear_row in range(block_row, row)
                                )
                            ]
                            if clear_columns:
                                block_col = min(
                                    clear_columns,
                                    key=lambda candidate_col: abs(
                                        candidate_col - platform_center
                                    ),
                                )
                                candidates.append((width, row, block_col))
                    start = None

        if not candidates:
            raise ValueError("No platform wider than 64 pixels was found")

        _, platform_row, block_col = max(
            candidates, key=lambda candidate: candidate[0]
        )
        block_x = block_col * self.tilemap.tile_width
        block_y = (
            platform_row * self.tilemap.tile_height
            - self.tilemap.tile_height
            - 32
        )
        return block_x, block_y

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(0, 0, self.tilemap.pixel_width, self.tilemap.pixel_height)

    def update(self, dt: float) -> None:
        for creature in self.creatures:
            creature.update(dt)

        # Remove dead creatures
        self.creatures = [
            creature for creature in self.creatures if not creature.is_dead
        ]

        if self.key is not None:
            self.key.y = max(self.key_target_y, self.key.y - 40 * dt)

    def update_key_block(self, score: int) -> bool:
        if self.key_block is None or self.key_block["active"]:
            return False

        if score >= self.key_block["activation_score"]:
            self.key_block["active"] = True
            self.creatures.clear()
            self.items.clear()
            self.tilemap.set_gid(
                self.collision_layer,
                self.key_block["row"],
                self.key_block["col"],
                self.key_block["first_gid"] + self.key_block["tile_id"],
            )
            return True

        return False

    def on_ceiling_hit(self, entity: Any, previous_vy: float) -> None:
        if (
            self.key_block is None
            or not self.key_block["active"]
            or self.key_block["hit"]
            or previous_vy >= 0
        ):
            return

        block_rect = pygame.Rect(
            self.key_block["x"],
            self.key_block["y"],
            self.tilemap.tile_width,
            self.tilemap.tile_height,
        )
        entity_rect = pygame.Rect(entity.x, entity.y, entity.width, entity.height)
        horizontal_overlap = (
            entity_rect.right > block_rect.left
            and entity_rect.left < block_rect.right
        )
        touching_block_bottom = (
            abs(entity_rect.top - block_rect.bottom) <= 1
        )
        if not horizontal_overlap or not touching_block_bottom:
            return

        self.key_block["hit"] = True
        self.tilemap.set_gid(
            self.collision_layer,
            self.key_block["row"],
            self.key_block["col"],
            self.key_block["first_gid"] + 1,
        )
        key_width = settings.FRAMES["key"][2].width
        key_x = self.key_block["x"] + (
            self.tilemap.tile_width - key_width
        ) / 2 + 2
        self.key = GameItem(
            key_x,
            self.key_block["y"],
            self.tilemap.tile_width,
            self.tilemap.tile_height,
            "key",
            2,
            True,
            False,
        )
        self.key_target_y = self.key_block["y"] - self.tilemap.tile_height

    def render(self, surface: pygame.Surface, camera: Any) -> None:
        self.tilemap.render(surface, camera)
        for creature in self.creatures:
            creature.render(surface, camera)
        for item in self.items:
            if item.active:
                item.render(surface, camera)
        if self.key is not None:
            self.key.render(surface, camera)
