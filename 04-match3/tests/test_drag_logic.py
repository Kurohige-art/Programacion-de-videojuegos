import unittest
from types import SimpleNamespace

from src.states.PlayState import PlayState


class DummyTile:
    def __init__(self, i, j, color):
        self.i = i
        self.j = j
        self.x = j * 32
        self.y = i * 32
        self.color = color


class PlayStateDragLogicTests(unittest.TestCase):
    def setUp(self):
        self.state = PlayState.__new__(PlayState)
        self.state.board = SimpleNamespace(tiles=[[None for _ in range(8)] for _ in range(8)])

    def test_valid_drop_on_adjacent_tile_with_matching_neighbor(self):
        source = DummyTile(2, 2, 0)
        target = DummyTile(2, 3, 1)
        same_color_neighbor = DummyTile(1, 3, 0)

        self.state.board.tiles[2][2] = source
        self.state.board.tiles[2][3] = target
        self.state.board.tiles[1][3] = same_color_neighbor

        self.assertTrue(self.state._can_drop_on_tile(source, target))

    def test_invalid_drop_on_non_adjacent_tile(self):
        source = DummyTile(2, 2, 0)
        target = DummyTile(0, 0, 1)

        self.state.board.tiles[2][2] = source
        self.state.board.tiles[0][0] = target

        self.assertFalse(self.state._can_drop_on_tile(source, target))

    def test_invalid_drop_without_matching_neighbor(self):
        source = DummyTile(2, 2, 0)
        target = DummyTile(2, 3, 1)
        different_neighbor = DummyTile(1, 3, 2)

        self.state.board.tiles[2][2] = source
        self.state.board.tiles[2][3] = target
        self.state.board.tiles[1][3] = different_neighbor

        self.assertFalse(self.state._can_drop_on_tile(source, target))


if __name__ == "__main__":
    unittest.main()
