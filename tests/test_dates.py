"""Calendar arithmetic (CLAUDE.md §4, Step 0 answer 2.2).

Year addition preserves month and day; 29 Feb -> 28 Feb. A month-precision date is the range from
the 1st to the last day of the month. A year-precision date is the whole year. No timedelta on years.
"""

from datetime import date

import pytest

from colophon.channels import DateRange, PartialDate, Precision, add_years


def test_add_years_keeps_month_and_day():
    assert add_years(date(1987, 9, 14), 35) == date(2022, 9, 14)
    assert add_years(date(2031, 11, 30), -2) == date(2029, 11, 30)


def test_add_years_feb_29_becomes_feb_28():
    assert add_years(date(1988, 2, 29), 35) == date(2023, 2, 28)
    assert add_years(date(1988, 2, 29), 4) == date(1992, 2, 29)


def test_add_years_zero_is_identity():
    assert add_years(date(1999, 12, 31), 0) == date(1999, 12, 31)


def test_partial_date_precision_and_bounds():
    day = PartialDate.parse("1987-09-14")
    month = PartialDate.parse("1987-09")
    year = PartialDate.parse("1987")
    assert (day.precision, month.precision, year.precision) == (Precision.DAY, Precision.MONTH, Precision.YEAR)
    assert (day.earliest, day.latest) == (date(1987, 9, 14), date(1987, 9, 14))
    assert (month.earliest, month.latest) == (date(1987, 9, 1), date(1987, 9, 30))
    assert (year.earliest, year.latest) == (date(1987, 1, 1), date(1987, 12, 31))
    assert PartialDate.parse("1988-02").latest == date(1988, 2, 29)


def test_partial_date_rejects_day_without_month():
    with pytest.raises(ValueError):
        PartialDate(1987, None, 14)


def test_range_add_years_moves_both_ends():
    r = DateRange.of(PartialDate.parse("1987-09")).add_years(35)
    assert (r.earliest, r.latest) == (date(2022, 9, 1), date(2022, 9, 30))
    assert r.display() == "2022-09"


def test_range_display_forms():
    assert DateRange.of(PartialDate.parse("2025-09-17")).display() == "2025-09-17"
    assert DateRange.of(PartialDate.parse("2025-09")).display() == "2025-09"
    assert DateRange.of(PartialDate.parse("2025")).display() == "2025"
    assert DateRange(date(2025, 3, 2), date(2025, 9, 17)).display() == "2025-03-02..2025-09-17"


def test_min_of_ranges_is_elementwise():
    a = DateRange.of(PartialDate.parse("2022-09"))
    b = DateRange.of(PartialDate.parse("2026-04"))
    assert DateRange.min_of(a, b) == a
    # Overlapping ranges: min of the true values lies between the elementwise mins.
    c = DateRange(date(2022, 9, 15), date(2022, 10, 15))
    assert DateRange.min_of(a, c) == DateRange(date(2022, 9, 1), date(2022, 9, 30))


def test_max_of_ranges_applies_a_floor():
    r = DateRange.of(PartialDate.parse("1920-05")).add_years(56)
    assert DateRange.max_of(r, DateRange.exact(date(1978, 1, 1))) == DateRange.exact(date(1978, 1, 1))


def test_range_comparisons_against_a_day():
    r = DateRange(date(2025, 9, 1), date(2025, 9, 30))
    assert r.entirely_before(date(2025, 10, 1))
    assert not r.entirely_before(date(2025, 9, 30))
    assert r.entirely_after(date(2025, 8, 31))
    assert r.contains(date(2025, 9, 17))
    assert not r.is_exact
    assert DateRange.exact(date(2025, 9, 17)).is_exact
