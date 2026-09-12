# The Legend of the Princess

`06-princess` is a top-down action RPG built with Python, Pygame, and the Gale framework.

## Added Features

- Added a collectible bow and a single chest that can appear during a dungeon run.
- Added directional bow animations and arrow projectiles.
- Added a boss room that can be generated after the bow is collected.
- Added the boss enemy with directional animations, health, contact damage, and a fireball attack.
- Added the boss vulnerability mechanic: arrows stun the boss, while sword attacks damage it only during the vulnerable period.
- Added projectile collision handling for enemies, the player, and the boss.
- Added a boss health bar that changes color while the boss is vulnerable.
- Added a victory state with options to return to the main menu or quit the game.
- Added the boss, chest, bow, arrow, character attack, and fireball graphics to the project assets.
- Added the corresponding texture frames, input mappings, object definitions, and state-machine registrations.
- Kept the existing room transitions, pot interactions, enemy behavior, health system, and game-over flow intact.

## Controls

- Arrow keys: Move.
- Space: Swing the sword.
- Enter: Pick up and throw pots.
- A: Open the chest and collect the bow.
- B: Shoot an arrow after collecting the bow.

## Project Structure

- `main.py`: Starts the game.
- `settings.py`: Configures input mappings, textures, animation frames, sounds, and music.
- `src/`: Contains game entities, world logic, projectiles, and game states.
- `assets/`: Contains the fonts, graphics, sounds, and other game resources.

## Validation

The Python source was checked with:

```bash
python -m compileall -q 06-princess
git diff --check -- 06-princess
```
