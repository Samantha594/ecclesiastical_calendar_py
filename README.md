# ecclesiastical_calendar_py

Computes the movable liturgical dates of the western Christian calendar from
the Gregorian computus.

```python
import datetime
from ecclesiastical_calendar_py import (
    Calendar,
    easter_sunday,
    advent_sunday,
    ash_wednesday,
    pentecost,
)

easter_sunday(2025)        # datetime.date(2025, 4, 20)
advent_sunday(2025)         # datetime.date(2025, 11, 30)
ash_wednesday(2025)        # datetime.date(2025, 3, 5)
pentecost(2025)            # datetime.date(2025, 6, 8)

cal = Calendar(2025)
cal.easter                 # datetime.date(2025, 4, 20)
cal.season(datetime.date(2025, 11, 30))   # 'advent'
cal.feasts()               # [('Ash Wednesday', ...), ('Easter Sunday', ...), ...]
```

## Why this exists

Easter is the anchor for most of the movable feasts, and the Gregorian
computus is a set of integer congruences that is easy to get subtly wrong.
This library keeps those congruences in one place and exposes the derived
dates as plain `datetime.date` objects. The trade-off is scope: only the
western (Latin) computus is implemented. The eastern computus uses a
different paschal full moon table, and mixing the two under one API would
make every function's meaning depend on a hidden parameter. If you need the
eastern dates, this library is the wrong tool.

## The awkward edge

The Gregorian reform took effect in 1582, so `easter_sunday(1582)` raises
`ValueError` rather than returning a Julian date. The functions also reject
non-integer years with `TypeError`. `Calendar.season` classifies any
`datetime.date`, including dates outside the calendar's own year, because the
season boundaries are defined relative to that year's Easter and Advent; it
is the caller's responsibility to pass a date that belongs to the year in
question if that is what they want.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

