"""Player movement, interpolation, and rendering logic."""

import pygame

from ..constants import PLAYER_MOVE_TIME, TILE_SIZE
from ..maze import Maze
from ..sprites import get_player_sprite
from ..vector import Vec2

class Player:
    """Encapsulates the controllable hero, including grid movement and drawing."""

    def __init__(self, maze: Maze, movement_speed: float = PLAYER_MOVE_TIME) -> None:
        """Spawn the player inside ``maze``, snapping to a safe tile if needed.

        Args:
            maze (Maze): Maze instance providing layout and helpers.
            movement_speed (float): Seconds needed to traverse one tile.
        """
        self.maze = maze
        self.spawn: tuple[int, int] = maze.player_spawn
        self.grid_pos: tuple[int, int] = self.spawn
        self.target_grid_pos: tuple[int, int] | None = None
        self.pixel_pos: Vec2 = self.maze.grid_to_pixel(self.grid_pos)
        self.facing: tuple[int, int] = (1, 0)
        self.radius = TILE_SIZE // 2 - 2
        self.lives = 3
        self.movement_speed = movement_speed
        self.movement_elapsed = 0.0
        self.current_direction: tuple[int, int] | None = None
        self.next_direction: tuple[int, int] | None = None

    def reset(self) -> None:
        """Return the player to the spawn tile and reset interpolation timers."""
        self.grid_pos = self.spawn
        self.target_grid_pos = None
        self.pixel_pos = self.maze.grid_to_pixel(self.grid_pos)
        self.facing = (1, 0)
        self.movement_elapsed = 0.0
        self.current_direction = None
        self.next_direction = None

    def set_next_direction(self, direction: tuple[int, int]) -> None:
        """Queue a direction for the next available movement opportunity.

        Args:
            direction (tuple[int, int]): Desired movement direction to queue.
        """
        self.next_direction = direction

    def can_move(self, direction: tuple[int, int]) -> bool:
        """Check if a move in ``direction`` is possible.

        Args:
            direction (tuple[int, int]): Desired movement direction.

        Returns:
            bool: ``True`` if the move is possible, ``False`` otherwise.
        """        
        target = self.maze.get_cell_in_direction(self.grid_pos, direction)
        if target is None or self.maze.is_wall(target):
            return False
        
        return True

    def _update_interpolation(self, dt: float) -> None:
        """Update movement interpolation and pixel position.

        Args:
            dt (float): Delta time since the previous frame in seconds.
        """
        if self.target_grid_pos is None:
            return

        self.movement_elapsed = min(self.movement_elapsed + dt, self.movement_speed)
        progress = self.movement_elapsed / self.movement_speed
        self.pixel_pos = self.maze.interpolate_pixel_position(
            self.grid_pos, self.target_grid_pos, progress
        )
        
        if self.movement_elapsed >= self.movement_speed:
            self.grid_pos = self.target_grid_pos
            self.target_grid_pos = None
            self.movement_elapsed = 0.0

    def _try_start_move(self) -> None:
        """Attempt to start a queued or current direction move if ready."""
        if self.next_direction is not None and self.can_move(self.next_direction):
            self.current_direction = self.next_direction
            self.next_direction = None

        if self.current_direction is not None and self.can_move(self.current_direction):
            self.facing = self.current_direction
            self.movement_elapsed = 0.0
            self.target_grid_pos = self.maze.get_cell_in_direction(self.grid_pos, self.current_direction)

    def update(self, dt: float) -> None:
        """Advance movement interpolation and handle queued movement.

        Args:
            dt (float): Delta time since the previous frame in seconds.
        """
        if self.target_grid_pos is None:
            self._try_start_move()

        self._update_interpolation(dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Blit the player sprite centered on the current pixel position.

        Args:
            surface (pygame.Surface): Destination surface to draw onto.
        """
        sprite = get_player_sprite(self.facing)
        rect = sprite.get_rect(center=(int(self.pixel_pos[0]), int(self.pixel_pos[1])))
        surface.blit(sprite, rect)

