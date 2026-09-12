# Throw a Bird

Throw a Bird is a physics-based slingshot game built with Python, Pygame, and the Gale framework. It recreates the original Defold study case with a destructible tower, throwable birds, camera movement, wind boundaries, sound effects, and a victory state.

## Implemented Features

### Slingshot Gameplay

- Drag the bird backward to aim and release the mouse button to launch it.
- The pull distance is clamped to keep launches controllable.
- The launch impulse is scaled from the bird's mass and pull distance.
- Dragging away from the bird pans the camera instead of aiming.
- The bird is held at the slingshot while it is not being aimed or launched.
- A launch is considered complete after every active bird remains below the movement thresholds for a short period, then the bird returns to the slingshot.

### Multiple Birds

- Press `Space` once during a launch to split the flying bird into two birds.
- The new birds keep the current speed and follow trajectories offset by 15 degrees in opposite directions.
- Splitting is allowed only once per launch and is disabled after the first collision.
- All active birds are tracked, rendered, checked for idle movement, and included in collision handling.
- Extra birds are removed from the physics world when a launch ends.

### Destructible Level

- The level contains stone blocks, wooden blocks, square aliens, and round aliens.
- Blocks use mass, friction, restitution, damping, energy, and sprite data defined in `src/definitions/entity.py`.
- Collision damage is calculated from impact speed and the relative mass of the colliding body.
- Stone and wood blocks change sprite as their energy decreases.
- Destroyed wood blocks spawn animated cosmetic debris.
- The game is won when every alien has been destroyed.

### Wind Boundaries and Camera

- Sensor zones at both sides of the playable area gradually slow and turn birds back toward the level.
- The camera follows the active bird during flight.
- The camera zooms out as the bird travels farther from the slingshot.
- The level background uses parallax layers, a tiled ground strip, and a filled ground area.
- The original Defold Y-up coordinates are converted to the Pygame Y-down coordinate system.

### Audio

- Background music loops during gameplay.
- Stretch, launch, and impact sound effects are played at the corresponding gameplay events.
- Audio assets are loaded from `assets/sounds/` through `settings.py`.

### Victory State

- A victory screen appears after all alien enemies are defeated.
- Clicking the screen starts a new game.

## Controls

| Input | Action |
| --- | --- |
| Left mouse button | Drag the bird to aim and release to launch; drag elsewhere to pan the camera |
| `Space` | Split the flying bird once per launch |
| `Escape` | Quit the game |

## Project Structure

```text
08-throw_a_bird/
├── main.py
├── settings.py
├── assets/
│   ├── fonts/
│   ├── graphics/
│   └── sounds/
└── src/
    ├── definitions/
    ├── entity/
    ├── states/
    │   └── game/
    ├── world/
    └── ThrowABird.py
```

Important modules include:

- `Bird.py`: creates, resets, renders, and splits birds.
- `PlayState.py`: owns input, aiming, launching, camera behavior, audio, and active bird management.
- `Level.py`: builds the ground, tower, wind zones, parallax background, collisions, and win condition.
- `Destructible.py`: handles block physics, impact damage, sprite damage tiers, and destruction.
- `Debris.py`: animates cosmetic wood debris after a block is destroyed.
- `VictoryState.py`: displays the completion screen and restarts the game.

## Running the Game

From the repository root, install the dependencies and run:

```bash
pip install -r requirements.txt
python 08-throw_a_bird/main.py
```

The game uses the virtual resolution configured in `settings.py` and scales it to the configured window size.
