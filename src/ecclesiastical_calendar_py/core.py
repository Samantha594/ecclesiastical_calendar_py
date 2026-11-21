"""Core liturgical date arithmetic for the western church.

The library deliberately returns plain :class:`datetime.date` objects rather
than a bespoke calendar type.  Dates are what callers compare, store and print;
wrapping them would only add a layer that leaks anyway as soon as someone calls
``isoformat()``.  The :class:`Calendar` class exists to hold the one piece of
configuration that actually varies between uses: the liturgical season
boundaries that depend on the date of Easter.
"""

from __future__ import annotations

import datetime
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple

__all__ = [
    "Calendar",
    "easter_sunday",
    "advent_sunday",
    "ash_wednesday",
    "pentecost",
]

Date = datetime.date


def _check_year(year: int) -> int:
    """Reject years outside the range where the Gregorian computus is valid.

    The Gregorian reform took effect in 1582; the algorithm is defined for
    years after that.  We accept 1583 onward so that ``easter_sunday(1583)``
    is the first legitimate answer and anything earlier raises instead of
    silently returning a Julian date.
    """
    if not isinstance(year, int):
        raise TypeError("year must be an int")
    if year < 1583:
        raise ValueError("year must be 1583 or later (Gregorian calendar)")
    return year


def easter_sunday(year: int) -> Date:
    """Return the date of Easter Sunday for *year*.

    Uses the anonymous Gregorian computus, which is exact for every year in
    the accepted range.  The intermediate values are deliberately kept as
    integers: the algorithm is a set of integer congruences and introducing
    floats would invite off-by-one errors at month boundaries.
    """
    _check_year(year)
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return Date(year, month, day)


def advent_sunday(year: int) -> Date:
    """Return the first Sunday of Advent for *year*.

    Advent begins on the fourth Sunday before Christmas, i.e. the Sunday
    falling on or after 27 November.  We compute the weekday of 27 November
    and advance to the next Sunday, which handles the fact that 27 November
    itself may already be a Sunday.
    """
    _check_year(year)
    start = Date(year, 11, 27)
    # Monday == 0 ... Sunday == 6 in datetime.weekday().
    days_until_sunday = (6 - start.weekday()) % 7
    return start + datetime.timedelta(days=days_until_sunday)


def ash_wednesday(year: int) -> Date:
    """Return Ash Wednesday, 46 days before Easter Sunday."""
    return easter_sunday(year) - datetime.timedelta(days=46)


def pentecost(year: int) -> Date:
    """Return Pentecost, 49 days after Easter Sunday."""
    return easter_sunday(year) + datetime.timedelta(days=49)


class Calendar:
    """A view over one liturgical year.

    The class is intentionally thin.  It exists so that callers who need many
    dates for the same year do not repeatedly recompute Easter, and so that
    the season boundaries are named in one place rather than scattered as
    magic offsets across application code.
    """

    def __init__(self, year: int) -> None:
        _check_year(year)
        self.year = year
        self._easter = easter_sunday(year)

    @property
    def easter(self) -> Date:
        """Easter Sunday for this calendar's year."""
        return self._easter

    @property
    def ash_wednesday(self) -> Date:
        """Ash Wednesday, the start of Lent."""
        return self._easter - datetime.timedelta(days=46)

    @property
    def pentecost(self) -> Date:
        """Pentecost, the end of the Easter season."""
        return self._easter + datetime.timedelta(days=49)

    @property
    def advent_sunday(self) -> Date:
        """First Sunday of Advent, the start of the next liturgical year."""
        return advent_sunday(self.year)

    def season(self, day: Date) -> str:
        """Return the liturgical season containing *day*.

        The seasons are the ones defined by the post-Vatican II Roman
        calendar.  The mapping is deliberately coarse: it names the season,
        not the specific observance, because observances vary by locale and
        order.  Days outside the year of this calendar are still classified;
        the arithmetic is purely relative to this year's Easter and Advent.
        """
        if not isinstance(day, Date):
            raise TypeError("day must be a datetime.date")

        easter = self._easter
        ash = easter - datetime.timedelta(days=46)
        pent = easter + datetime.timedelta(days=49)
        advent = self.advent_sunday
        christmas = Date(self.year, 12, 25)

        if day < ash:
            # Before Lent: either the Christmas season that began last year
            # or Ordinary Time.  We treat everything from 1 January up to
            # Ash Wednesday as Ordinary Time and leave the Christmas season
            # to the previous calendar's responsibility.
            return "ordinary"
        if day < easter:
            return "lent"
        if day <= pent:
            return "easter"
        if day < advent:
            return "ordinary"
        if day < christmas:
            return "advent"
        return "christmas"

    def feasts(self) -> List[Tuple[str, Date]]:
        """Return the principal movable feasts for this year, in order.

        Only movable feasts are included; fixed feasts such as Christmas are
        not, because they do not depend on the computus and listing them here
        would suggest the library knows more about local calendars than it
        does.
        """
        return [
            ("Ash Wednesday", self.ash_wednesday),
            ("Easter Sunday", self.easter),
            ("Pentecost", self.pentecost),
            ("Advent Sunday", self.advent_sunday),
        ]

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"Calendar(year={self.year!r})"
