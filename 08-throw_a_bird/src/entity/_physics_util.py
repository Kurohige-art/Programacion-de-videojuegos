"""Keep the physics damping API in one shared helper."""

from gale.physics.body import Body


def set_damping(body: Body, linear_damping: float, angular_damping: float) -> None:
    body.set_damping(linear_damping, angular_damping)
