"""Ecclesiastical calendar computations for western Christian traditions.

Only the western (Latin) computus is implemented.  Eastern (Orthodox)
computations use a different paschal full moon table and are deliberately out
of scope; adding them would require a separate algorithm and would make the
exported API ambiguous.
"""

from .core import (
    Calendar,
    easter_sunday,
    advent_sunday,
    ash_wednesday,
    pentecost,
)

__all__ = [
    "Calendar",
    "easter_sunday",
    "advent_sunday",
    "ash_wednesday",
    "pentecost",
]
