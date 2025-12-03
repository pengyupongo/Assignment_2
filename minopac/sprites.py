"""Sprite loading/tinting helpers cached for fast rendering."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, Tuple

import pygame

from .constants import ASSETS_DIR, TILE_SIZE


Color = Tuple[int, int, int]
DirectionKey = Tuple[int, int]


def _resolve(path: str | Path) -> Path:
    """Resolve a relative asset path against the package asset directory.

    Args:
        path (str | Path): Relative path inside ``ASSETS_DIR``.

    Returns:
        Path: Absolute path pointing to the requested asset.
    """
    return ASSETS_DIR / path


@lru_cache(maxsize=128)
def load_sprite(path: str, size: int | Tuple[int, int] | None = TILE_SIZE) -> pygame.Surface:
    """Load an asset, optionally scale it, and cache the resulting surface.

    Args:
        path (str): Relative asset path inside ``ASSETS_DIR``.
        size (int | Tuple[int, int] | None): Optional size override. Provide an
            integer for square scaling, a ``(w, h)`` tuple for explicit scaling,
            or ``None`` to keep the original size.

    Returns:
        pygame.Surface: Converted and optionally scaled sprite surface.
    """
    full_path = _resolve(path)
    surface = pygame.image.load(full_path).convert_alpha()
    if size is None:
        return surface
    if isinstance(size, int):
        size = (size, size)
    if surface.get_size() != size:
        surface = pygame.transform.smoothscale(surface, size)
    return surface


def tint_surface(surface: pygame.Surface, color: Color) -> pygame.Surface:
    """Apply a multiplicative tint and return the tinted surface.

    Args:
        surface (pygame.Surface): Source sprite to tint.
        color (Color): RGB tuple used as the tint color.

    Returns:
        pygame.Surface: New surface with the tint applied.
    """
    tinted = surface.copy()
    r, g, b = color
    tint = pygame.Surface(tinted.get_size())
    tint.fill((r, g, b))
    tinted.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted


PLAYER_DIRECTION_ASSETS: Dict[DirectionKey, str] = {
    (1, 0): "robot_robolike/east.png",
    (-1, 0): "robot_robolike/west.png",
    (0, -1): "robot_robolike/north.png",
    (0, 1): "robot_robolike/south.png",
}

PLAYER_CACHE: Dict[DirectionKey, pygame.Surface] = {}
GHOST_COLOR_CACHE: Dict[Tuple[str, Color], pygame.Surface] = {}
FRIGHTENED_CACHE: pygame.Surface | None = None


def get_player_sprite(direction: DirectionKey) -> pygame.Surface:
    """Fetch the cached player sprite for a direction.

    Args:
        direction (DirectionKey): Requested facing direction.

    Returns:
        pygame.Surface: Sprite oriented toward ``direction``.
    """
    key = direction if direction in PLAYER_DIRECTION_ASSETS else (1, 0)
    if key not in PLAYER_CACHE:
        PLAYER_CACHE[key] = load_sprite(PLAYER_DIRECTION_ASSETS[key], TILE_SIZE)
    return PLAYER_CACHE[key]


def get_ghost_sprite(color: Color | None = None) -> pygame.Surface:
    """Get the base ghost sprite, optionally tinted to a color.

    Args:
        color (Color | None): Tint color or ``None`` for the default palette.

    Returns:
        pygame.Surface: Sprite already tinted and cached.
    """
    if color not in GHOST_COLOR_CACHE:
        base = load_sprite("ghost/regular.png", TILE_SIZE)
        if color is not None:
            GHOST_COLOR_CACHE[color] = tint_surface(base, color)
        else:
            GHOST_COLOR_CACHE[color] = base
    return GHOST_COLOR_CACHE[color]


def get_frightened_sprite() -> pygame.Surface:
    """Return the fright-mode ghost sprite, loading it lazily once.

    Returns:
        pygame.Surface: Cached frightened-state sprite.
    """
    global FRIGHTENED_CACHE
    if FRIGHTENED_CACHE is None:
        FRIGHTENED_CACHE = load_sprite("ghost/frightened.png", TILE_SIZE)
    return FRIGHTENED_CACHE

def get_eaten_sprite() -> pygame.Surface:
    """Return the sprite used after a frightened ghost is eaten by the player.

    Returns:
        pygame.Surface: Cached eaten-state sprite.
    """
    return load_sprite("ghost/eaten.png", TILE_SIZE)