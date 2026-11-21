import datetime
import unittest

from ecclesiastical_calendar_py import (
    Calendar,
    advent_sunday,
    ash_wednesday,
    easter_sunday,
    pentecost,
)


class EasterSundayTests(unittest.TestCase):
    def test_known_dates(self):
        # Values cross-checked against the standard Gregorian computus table.
        cases = {
            1583: datetime.date(1583, 4, 10),
            2000: datetime.date(2000, 4, 23),
            2024: datetime.date(2024, 3, 31),
            2025: datetime.date(2025, 4, 20),
            2038: datetime.date(2038, 4, 25),
        }
        for year, expected in cases.items():
            with self.subTest(year=year):
                self.assertEqual(easter_sunday(year), expected)

    def test_earliest_and_latest_possible(self):
        # Easter cannot fall before 22 March or after 25 April.
        for year in range(1583, 2200):
            day = easter_sunday(year)
            self.assertGreaterEqual(day, datetime.date(year, 3, 22))
            self.assertLessEqual(day, datetime.date(year, 4, 25))

    def test_rejects_pre_gregorian_years(self):
        with self.assertRaises(ValueError):
            easter_sunday(1582)

    def test_rejects_non_int(self):
        with self.assertRaises(TypeError):
            easter_sunday(2024.0)  # type: ignore[arg-type]


class AdventSundayTests(unittest.TestCase):
    def test_known_dates(self):
        cases = {
            2023: datetime.date(2023, 12, 3),
            2024: datetime.date(2024, 12, 1),
            2025: datetime.date(2025, 11, 30),
            2026: datetime.date(2026, 11, 29),
        }
        for year, expected in cases.items():
            with self.subTest(year=year):
                self.assertEqual(advent_sunday(year), expected)

    def test_is_always_a_sunday(self):
        for year in range(1583, 2200):
            self.assertEqual(advent_sunday(year).weekday(), 6)

    def test_never_before_27_november(self):
        for year in range(1583, 2200):
            self.assertGreaterEqual(advent_sunday(year), datetime.date(year, 11, 27))


class DerivedFeastTests(unittest.TestCase):
    def test_ash_wednesday_offset(self):
        for year in (2024, 2025, 2026):
            self.assertEqual(
                ash_wednesday(year),
                easter_sunday(year) - datetime.timedelta(days=46),
            )

    def test_pentecost_offset(self):
        for year in (2024, 2025, 2026):
            self.assertEqual(
                pentecost(year),
                easter_sunday(year) + datetime.timedelta(days=49),
            )

    def test_ash_wednesday_is_a_wednesday(self):
        for year in range(1583, 2200):
            self.assertEqual(ash_wednesday(year).weekday(), 2)

    def test_pentecost_is_a_sunday(self):
        for year in range(1583, 2200):
            self.assertEqual(pentecost(year).weekday(), 6)


class CalendarTests(unittest.TestCase):
    def test_year_is_stored(self):
        cal = Calendar(2025)
        self.assertEqual(cal.year, 2025)

    def test_easter_property_matches_function(self):
        cal = Calendar(2025)
        self.assertEqual(cal.easter, easter_sunday(2025))

    def test_season_boundaries(self):
        cal = Calendar(2025)
        # 2025: Ash Wednesday 5 March, Easter 20 April, Pentecost 8 June,
        # Advent 30 November.
        self.assertEqual(cal.season(datetime.date(2025, 3, 4)), "ordinary")
        self.assertEqual(cal.season(datetime.date(2025, 3, 5)), "lent")
        self.assertEqual(cal.season(datetime.date(2025, 4, 19)), "lent")
        self.assertEqual(cal.season(datetime.date(2025, 4, 20)), "easter")
        self.assertEqual(cal.season(datetime.date(2025, 6, 8)), "easter")
        self.assertEqual(cal.season(datetime.date(2025, 6, 9)), "ordinary")
        self.assertEqual(cal.season(datetime.date(2025, 11, 29)), "ordinary")
        self.assertEqual(cal.season(datetime.date(2025, 11, 30)), "advent")
        self.assertEqual(cal.season(datetime.date(2025, 12, 24)), "advent")
        self.assertEqual(cal.season(datetime.date(2025, 12, 25)), "christmas")

    def test_season_rejects_non_date(self):
        cal = Calendar(2025)
        with self.assertRaises(TypeError):
            cal.season("2025-03-05")  # type: ignore[arg-type]

    def test_feasts_are_ordered_and_complete(self):
        cal = Calendar(2025)
        names = [name for name, _ in cal.feasts()]
        self.assertEqual(
            names,
            ["Ash Wednesday", "Easter Sunday", "Pentecost", "Advent Sunday"],
        )
        dates = [day for _, day in cal.feasts()]
        self.assertEqual(dates, sorted(dates))

    def test_calendar_rejects_pre_gregorian_year(self):
        with self.assertRaises(ValueError):
            Calendar(1500)


if __name__ == "__main__":
    unittest.main()
