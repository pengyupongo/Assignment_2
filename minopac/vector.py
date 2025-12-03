"""Lightweight vector helpers to keep pygame math readable."""

from __future__ import annotations

from typing import Tuple

Vec2 = Tuple[float, float]


def vec_length_sq(vec: Vec2) -> float:
    """Return the squared magnitude of a 2D vector.

    Args:
        vec (Vec2): Vector whose length should be measured.

    Returns:
        float: Squared length of ``vec`` without taking a square root.
    """
    return vec[0] * vec[0] + vec[1] * vec[1]


def vec_distance(a: Vec2, b: Vec2) -> float:
    """Calculate the Euclidean distance between two vectors.

    Args:
        a (Vec2): First endpoint.
        b (Vec2): Second endpoint.

    Returns:
        float: Straight-line distance separating ``a`` and ``b``.
    """
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return (dx * dx + dy * dy) ** 0.5


def vec_lerp(start: Vec2, end: Vec2, t: float) -> Vec2:
    """Linearly interpolate between two vectors.

    Args:
        start (Vec2): Starting point of the interpolation.
        end (Vec2): Ending point of the interpolation.
        t (float): Parameter between 0.0 and 1.0 describing interpolation progress.

    Returns:
        Vec2: A point between ``start`` and ``end`` based on ``t``.
    """
    return (
        start[0] + (end[0] - start[0]) * t,
        start[1] + (end[1] - start[1]) * t,
    )

