"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition for creatures.
"""

from typing import Dict, Any

from src.states.entities import creatures_states

def _definition(
    tile_index: int, flying: bool = False, death_tile_index: int | None = None
) -> Dict[str, Any]:
    frame_pair = [tile_index, tile_index + 1]
    death_start = tile_index + 6 if death_tile_index is None else death_tile_index
    death_frames = [death_start, death_start + 1]
    return {
        "texture_id": "creatures",
        "walk_speed": 10 if not flying else 25,
        "flying": flying,
        "animation_defs": {
            "walk": {"frames": frame_pair, "interval": 0.18},
            "death": {"frames": death_frames, "interval": 0.12, "loops": 1},
        },
        "states": {
            "walk": creatures_states.FlyingState
            if flying
            else creatures_states.SnailWalkState,
            "dead": creatures_states.DeathState,
        },
        "first_state": "walk",
    }


CREATURES: Dict[int, Dict[str, Any]] = {
    tile_index: _definition(tile_index, tile_index in {32, 40})
    for tile_index in range(0, 56, 8)
}

CREATURES[52] = _definition(52, death_tile_index=54)
