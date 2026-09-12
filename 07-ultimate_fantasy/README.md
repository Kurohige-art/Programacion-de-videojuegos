# Ultimate Fantasy

Ultimate Fantasy is a small turn-based RPG built with Python, Pygame, and the Gale framework. The game combines overworld exploration, party management, procedural battles, character progression, and a state-stack based user interface.

## Implemented Features

### World Exploration

- Five connected regions: the town, north, south, east, and west areas.
- Party movement with a leader and following party members.
- Region transitions with fade effects and music changes.
- NPC interaction and dialogue.
- Random encounters while travelling through the world.
- Save and load support through the existing save slot.

### Party Status Menu

Press `Space` while exploring the world to open the party status menu. This menu is only registered by `PlayState`, so it cannot be opened during a battle.

The menu contains:

1. The four selected party members.
2. An `Exit` option that returns to exploration.

Selecting a party member opens two side-by-side panels:

- A read-only statistics panel with class, level, experience, HP, attack, defense, magic, and current status.
- An actions panel containing the character's available actions and a `Return` option.

Offensive actions are displayed with reduced opacity and cannot be selected from the exploration menu. Healing actions remain enabled.

### Exploration Healing

- Individual healing opens a target list containing only living party members whose HP is below maximum.
- Each target displays its current HP and maximum HP.
- Individual healing animates the target's HP increase.
- The target list is refreshed after healing, so fully healed characters are removed automatically.
- The target menu includes a `Return` option that goes back to the selected character's status and actions panel.
- Global healing affects every living party member using the same healing functions as battle.
- Global healing opens a temporary party overview showing every affected character and an animated HP bar for each one.
- The global healing overview closes automatically and returns to the character status panel.

### Battle System

- Battles use a separate battle map with party members and randomly generated enemies.
- Characters and enemies share the `BattleEntity` statistics and action model.
- Actions support single-target and area-of-effect behavior.
- Damage, defense, healing, sound effects, HP bars, victory, defeat, experience, and level-up flows are supported.
- Enemy actions are selected automatically by the battle AI.

### Recovery-Based Turn Management

Every battle entity has:

- `rest_time`: the duration required to recover after acting.
- `rest_timer`: the current remaining recovery time.

`BattleState` updates the recovery timers for all living characters and enemies. The first entity whose timer reaches zero receives the next turn. A circular tie-break cursor ensures that characters and enemies that become ready at the same time receive turns fairly instead of repeatedly selecting the first entity.

After an action, the entity enters a temporary recovery state displaying:

```text
charging energy...
```

The message remains visible for the entity's recovery period. When recovery completes, the next ready character or enemy automatically receives a turn. This gives every living party member and every living enemy an opportunity to act.

## Controls

| Key | Action |
| --- | --- |
| Arrow keys | Move, navigate menus, or select a healing target |
| `Enter` | Confirm a menu selection |
| `Space` | Open the party status menu while exploring; advance dialogue elsewhere |
| `P` | Open the pause menu while exploring |
| `C` | Continue from the title screen when a save exists |
| `Escape` | Quit the game |

## Project Structure

```text
07-ultimate_fantasy/
├── main.py
├── settings.py
├── assets/
└── src/
    ├── entity/
    ├── gui/
    ├── states/
    │   ├── entity/
    │   └── game/
    └── world/
```

Important game states include:

- `PlayState`: owns the overworld and routes exploration-only input.
- `StatusMenuState`: selects a party member.
- `CharacterStatusState`: displays character statistics and usable actions.
- `StatusTargetState`: selects an individual healing target.
- `GlobalHealState`: displays animated global healing.
- `BattleState`: owns the battle map, entities, HP bars, and recovery timers.
- `TakeTurnState`: resolves the next ready entity's turn.
- `ChargingEnergyState`: displays post-action recovery.

## Running the Game

From this directory, install the dependencies and run:

```bash
pip install -r ../requirements.txt
python main.py
```

The game uses a virtual resolution configured in `settings.py` and scales it to the configured window size.
