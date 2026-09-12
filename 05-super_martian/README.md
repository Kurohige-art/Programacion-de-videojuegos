# Super Martian

Super Martian is a small Python and Pygame platformer built on the Gale framework. The player explores two tilemap-based levels, collects coins, defeats creatures, and reaches the key to advance.

## Changes and Added Features

- Added a second playable level and configured level progression with `NUM_LEVELS` and per-level tilemaps.
- Added a key item to each level. Collecting it completes the current level and starts the level transition.
- Added a circular iris transition between levels, including the final transition back to the start screen after the last level.
- Added a victory sound and playback management for level completion, pauses, deaths, and transitions.
- Added flying creature behavior with horizontal movement and automatic direction changes at world boundaries.
- Added a shared creature death state with a death animation and a dead flag after the animation finishes.
- Improved walking creature boundary checks so snails turn around at walls and avoid walking off ledges.
- Added stomp detection: landing on a creature defeats it and bounces the player; side collisions still cause player death.
- Added ladder climbing controls and player handling for climbing direction and the top-of-ladder lock.
- Improved the initial player spawn so one-way platform collision is detected on the first frame.
- Standardized the modified and newly added Python modules with the existing project documentation, naming, import, and type-annotation style.
- Translated the remaining Spanish code identifier and asset references from `llave` to `key`.

## Controls

- `A` / `Left Arrow`: move left
- `D` / `Right Arrow`: move right
- `Space` or left mouse button: jump
- `Up Arrow`: climb up
- `Down Arrow`: climb down
- `P`: pause or resume
- `Enter`: start the game, restart after game over, or continue through menus
- `Escape`: quit

## Running the Game

Install the dependencies from the repository root:

```bash
pip install -r requirements.txt
```

Run the game from this project directory:

```bash
python main.py
```

The game uses a 400 x 192 virtual resolution and scales the window to 1200 x 576.
