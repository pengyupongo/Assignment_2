"""Ghost entity definitions (behavior to be implemented by students)."""

import pygame

from ..constants import GHOST_FRIGHTENED_SPEED_SCALE, GHOST_MOVE_TIME, TILE_SIZE
from ..maze import Maze
from ..sprites import get_eaten_sprite, get_frightened_sprite, get_ghost_sprite
from ..vector import Vec2, vec_distance, vec_lerp


class Ghost:
    """Placeholder ghost entity; fill in movement, AI, and drawing behavior."""

    pass
    # TODO: Implement the Ghost class