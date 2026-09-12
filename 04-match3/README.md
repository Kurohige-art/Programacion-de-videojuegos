# Match-3

This project is a Pygame match-3 game built with the Gale engine. The player
must swap adjacent tiles to create horizontal or vertical matches before the
level timer expires.

## Changes and Features

- Added mouse drag-and-drop tile movement with virtual-resolution coordinate
  conversion.
- Added validation for adjacent drops and rejected swaps that do not create a
  valid match.
- Added an animated suggestion system that highlights a possible move after a
  period of inactivity.
- Added playable-board validation. The board is regenerated when no valid move
  remains and no power-up is active.
- Added line-clear power-ups for matches of four tiles. They clear the full
  row and column that cross the activated tile.
- Added color-bomb power-ups for matches of five or more tiles. They clear all
  tiles with the activated tile's color.
- Added power-up chaining, animated effects, scoring, and dedicated sound
  effects for lightning and bomb power-ups.
- Added power-up textures, spritesheets, and sounds to the asset folders.
- Added debug color cycling while holding Shift or Ctrl during tile selection
  to support gameplay testing.
- Added automated tests for valid adjacent drops and invalid drop scenarios.
- Standardized the modified Python files to match the existing project style,
  including import ordering, type annotations, comments, and whitespace.

## Running the Game

Install the project dependencies and run the game from the repository root:

```bash
pip install -r requirements.txt
python 04-match3/main.py
```

Run the Match-3 tests with:

```bash
python -m unittest discover -s 04-match3/tests
```