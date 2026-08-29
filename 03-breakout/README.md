## Breakout power-ups

The `03-breakout` study case includes power-ups that fall from destroyed bricks.
Each power-up moves downward until it leaves the play area or collides with the
paddle. When the paddle catches one, its `take()` method applies the effect and
the power-up is removed from the active list.

### Extra life

`ExtraLife` uses the heart power-up icon and attempts to award one additional
life when the paddle catches it. The game has a maximum of three lives:

- If the current number of lives is less than three, one life is added.
- If the player already has three lives, the power-up has no effect.
- In both cases, the power-up is consumed and disappears after the collision.

Power-ups are generated with a 10 percent chance after a brick is hit. When a
power-up is generated, the game randomly selects between `CaptureBall`,
`ExtraLife`, and `TwoMoreBall`. Their implementations are registered in
`03-breakout/src/powerups/__init__.py`, allowing the existing abstract factory
to instantiate them by class name.

# Measurements of the cannon, missile and explosion sprites

- cannon: 14x16 pixels
- separation from the missile sprite frames: 2 pixels
- missile: 8x8 pixels
- separation from the explosion sprite frames: 2 pixels
- sizes, in order, of the explosion animation sprite frames: 13x13, 14x14, 29x27, 30x28, 27x27, 21x22 pixels respectively