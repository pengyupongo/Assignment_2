"""Maze representation, drawing, and tile utility helpers."""

from __future__ import annotations

from collections import deque
from typing import Iterable, List, Sequence, Set

import pygame

from .constants import LEVEL_LAYOUT, TILE_SIZE
from .sprites import load_sprite
from .vector import Vec2


class Maze:
    """Stores the current maze layout plus pellet/maze metadata."""
    def __init__(
        self,
        layout: List[List[str]],
        pellets: Set[tuple[int, int]],
        power_pellets: Set[tuple[int, int]],
        wall_tiles: Set[tuple[int, int]],
        width: int,
        height: int,
        ghost_spawns: List[tuple[int, int]],
        player_spawn: tuple[int, int],
    ) -> None:
        """Initialize maze state with pre-parsed layout and tile collections.

        Args:
            layout (List[List[str]]): 2D grid describing maze tiles.
            pellets (Set[tuple[int, int]]): Coordinates of standard pellets.
            power_pellets (Set[tuple[int, int]]): Coordinates of power pellets.
            wall_tiles (Set[tuple[int, int]]): Coordinates considered walls.
            width (int): Width of the maze in tiles.
            height (int): Height of the maze in tiles.
        """
        self.layout = layout
        self.pellets = pellets
        self.power_pellets = power_pellets
        self.wall_tiles = wall_tiles
        self.width = width
        self.height = height
        self.amount_ghosts_spawned = 0
        self.ghost_spawns = ghost_spawns
        self.player_spawn = player_spawn

    @classmethod
    def from_strings(cls, layout: Sequence[str]) -> "Maze":
        """Construct a maze by parsing a list of string rows.

        Args:
            layout (Sequence[str]): Raw textual layout pulled from constants or files.

        Returns:
            Maze: A maze instance populated with pellet and wall metadata.
        """
        rows = [list(row) for row in layout]
        height = len(rows)
        width = len(rows[0])
        pellets: Set[tuple[int, int]] = set()
        power_pellets: Set[tuple[int, int]] = set()
        wall_tiles: Set[tuple[int, int]] = set()
        ghost_spawns: List[tuple[int, int]] = []
        player_spawn: tuple[int, int] = (0, 0)
        for y, row in enumerate(rows):
            for x, char in enumerate(row):
                if char == "#":
                    wall_tiles.add((x, y))
                elif char == ".":
                    pellets.add((x, y))
                elif char.lower() == "o":
                    power_pellets.add((x, y))
                elif char == "G":
                    ghost_spawns.append((x, y))
                elif char == "P":
                    player_spawn = (x, y)
        return cls(rows, pellets, power_pellets, wall_tiles, width, height, ghost_spawns, player_spawn)

    @property
    def pixel_width(self) -> int:
        """Return the maze width in pixels.

        Returns:
            int: Width measured in screen pixels.
        """
        return self.width * TILE_SIZE

    @property
    def pixel_height(self) -> int:
        """Return the maze height in pixels.

        Returns:
            int: Height measured in screen pixels.
        """
        return self.height * TILE_SIZE

    def is_wall(self, grid: tuple[int, int]) -> bool:
        """Determine whether a target tile is blocked.

        Args:
            grid (tuple[int, int]): Coordinate to inspect.

        Returns:
            bool: ``True`` if the tile is a wall or outside the maze bounds.
        """
        x, y = grid
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return True
        return (x, y) in self.wall_tiles

    def get_cell_in_direction(self, position: tuple[int, int] | Vec2, direction: tuple[int, int] | Vec2) -> tuple[int, int] | None:
        """Get the cell position in the given direction from a starting position.

        Args:
            position (tuple[int, int] | Vec2): Starting grid position.
            direction (tuple[int, int] | Vec2): Direction vector (should be cardinal direction).

        Returns:
            tuple[int, int] | None: The target cell position, or None if out of bounds.
        """
        x = position[0] + direction[0]
        y = position[1] + direction[1]
        
        # Handle horizontal wraparound
        x = (int(x) + self.width) % self.width
        
        # Check vertical bounds
        if y < 0 or y >= self.height:
            return None
        
        return (int(x), int(y))

    def grid_to_pixel(self, grid: tuple[int, int] | Vec2) -> Vec2:
        """Convert a grid coordinate to the pixel center used for sprite placement.

        Args:
            grid (tuple[int, int] | Vec2): Grid coordinate to convert.

        Returns:
            Vec2: Pixel-space center representing ``grid``.
        """
        return ((grid[0] + 0.5) * TILE_SIZE, (grid[1] + 0.5) * TILE_SIZE)

    def interpolate_pixel_position(
        self, start: tuple[int, int] | Vec2, end: tuple[int, int] | Vec2, progress: float
    ) -> Vec2:
        """Interpolate between two grid positions accounting for horizontal wraparound.

        Args:
            start (tuple[int, int] | Vec2): Starting grid position.
            end (tuple[int, int] | Vec2): Ending grid position.
            progress (float): Interpolation progress between 0.0 and 1.0.

        Returns:
            Vec2: Pixel-space position interpolated between start and end.
        """
        from .vector import vec_lerp

        start_pixel = list(self.grid_to_pixel(start))
        end_pixel = list(self.grid_to_pixel(end))
        width = self.pixel_width

        # Handle horizontal wraparound
        start_x = int(start[0])
        end_x = int(end[0])

        if start_x == self.width - 1 and end_x == 0:
            # Wrapping right to left
            end_pixel[0] += width
        elif start_x == 0 and end_x == self.width - 1:
            # Wrapping left to right
            start_pixel[0] += width

        # Interpolate
        pos = vec_lerp(tuple(start_pixel), tuple(end_pixel), progress)

        # Normalize result back to valid pixel range
        if pos[0] < 0:
            return (pos[0] + width, pos[1])
        if pos[0] >= width:
            return (pos[0] - width, pos[1])
        return pos

    def pixel_to_grid(self, pixel: Vec2) -> tuple[int, int]:
        """Convert pixel coordinates back to grid coordinates.

        Args:
            pixel (Vec2): Pixel position to convert.

        Returns:
            tuple[int, int]: Tile location containing ``pixel``.
        """
        return int(pixel[0] // TILE_SIZE), int(pixel[1] // TILE_SIZE)

    def eat_pellet(self, grid: tuple[int, int]) -> str | None:
        """Consume a pellet at the given coordinate.

        Args:
            grid (tuple[int, int]): Tile where the player just moved.

        Returns:
            str | None: ``"."`` for a standard pellet, ``"o"`` for a power pellet,
                or ``None`` if nothing was eaten.
        """
        if grid in self.pellets:
            self.pellets.remove(grid)
            return "."
        if grid in self.power_pellets:
            self.power_pellets.remove(grid)
            return "o"
        return None

    def remaining_pellets(self) -> int:
        """Count how many pellets remain in the level.

        Returns:
            int: Total pellets plus power pellets still uneaten.
        """
        return len(self.pellets) + len(self.power_pellets)

    def neighbors(self, grid: tuple[int, int]) -> Iterable[tuple[int, int]]:
        """Yield walkable neighbor tiles with wraparound.

        Args:
            grid (tuple[int, int]): Origin tile.

        Yields:
            tuple[int, int]: Neighbor coordinates reachable in one move.
        """
        x, y = grid
        for offset in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + offset[0], y + offset[1]
            nx = (nx + self.width) % self.width
            if not self.is_wall((nx, ny)):
                yield nx, ny

    def find_open_tile(self, preferred: tuple[int, int]) -> tuple[int, int]:
        """Return the preferred tile or the nearest non-wall fallback.

        Args:
            preferred (tuple[int, int]): Target tile that may be blocked.

        Returns:
            tuple[int, int]: Either ``preferred`` or a safe alternative.

        Raises:
            ValueError: If the maze contains no open tiles.
        """
        if not self.is_wall(preferred):
            return preferred
        visited = {preferred}
        queue: deque[tuple[int, int]] = deque([preferred])
        while queue:
            x, y = queue.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= self.width or ny >= self.height:
                    continue
                if (nx, ny) in visited:
                    continue
                if not self.is_wall((nx, ny)):
                    return nx, ny
                visited.add((nx, ny))
                queue.append((nx, ny))
        raise ValueError("Maze contains no open tiles")

    def find_shortest_path(
        self, start: tuple[int, int], end: tuple[int, int]
    ) -> list[tuple[int, int]] | None:
        """Find the shortest path between two positions using BFS.

        Args:
            start (tuple[int, int]): Starting grid position.
            end (tuple[int, int]): Target grid position.

        Returns:
            list[tuple[int, int]] | None: List of positions from start to end,
                or None if no path exists.
        """
        if self.is_wall(start) or self.is_wall(end):
            return None
        
        if start == end:
            return [start]

        visited = {start}
        queue: deque[tuple[tuple[int, int], list[tuple[int, int]]]] = deque([(start, [start])])
        
        while queue:
            current, path = queue.popleft()
            
            for neighbor in self.neighbors(current):
                if neighbor == end:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None

    def next_ghost_spawn_location(self) -> tuple[int, int]:
        """Return the next spawn location for a ghost, cycling through spawn positions.

        Returns:
            tuple[int, int]: The grid coordinates of the next ghost spawn location.
        """
        location = self.ghost_spawns[self.amount_ghosts_spawned % len(self.ghost_spawns)]
        self.amount_ghosts_spawned += 1
        return location


    def draw(self, surface: pygame.Surface) -> None:
        """Render the maze background, pellets, and power pellets.

        Args:
            surface (pygame.Surface): Target surface (usually the game screen).

        Returns:
            None: Rendering is performed directly to ``surface``.
        """
        path_tile = load_sprite("maze/path_0.png", TILE_SIZE)
        wall_tile = load_sprite("maze/wall_0.png", TILE_SIZE)
        pellet_sprite = load_sprite("maze/pebble.png", TILE_SIZE // 2)
        power_sprite = load_sprite("maze/powerpebble.png", TILE_SIZE)

        surface.fill((0, 0, 0))
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                tile_char = self.layout[y][x]
                if tile_char == "#":
                    surface.blit(wall_tile, rect)
                else:
                    surface.blit(path_tile, rect)

        for (x, y) in self.pellets:
            center = self.grid_to_pixel((x, y))
            rect = pellet_sprite.get_rect(center=center)
            surface.blit(pellet_sprite, rect)

        for (x, y) in self.power_pellets:
            center = self.grid_to_pixel((x, y))
            rect = power_sprite.get_rect(center=center)
            surface.blit(power_sprite, rect)

