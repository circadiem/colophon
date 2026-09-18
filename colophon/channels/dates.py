"""Calendar arithmetic for statutory clocks.

This is the code most likely to be quietly wrong, so the conventions are stated here and tested in
tests/test_dates.py (CLAUDE.md §4; Step 0 answer 2.2).

Conventions
-----------
- A date input carries explicit precision: DAY, MONTH or YEAR (``PartialDate``). A MONTH date
  means "some day in that month"; a YEAR date means "some day in that year". It is never coerced
  to a day.
- Every computed date is a ``DateRange``: the closed interval of the values the true date could
  take. A DAY input yields a range whose ends coincide.
- ``add_years`` preserves month and day. 29 February plus N years, landing in a non-leap year,
  becomes 28 February. There is no timedelta arithmetic on years anywhere in channels/.
- Adding years to a range moves both ends. Taking the minimum of two ranges is elementwise:
  the minimum of two uncertain values lies between the minimum of the lower bounds and the
  minimum of the upper bounds. Likewise the maximum, used for the §304(c) 1978 floor.
- A window is half-open, ``[start, start + 5y)``: the last effective date is the day before
  ``window_end``. ``last_serviceable_date = window_end - 2y`` follows docs/II §02 literally.
- No clock reads. ``as_of`` is injected by the caller and is always a ``datetime.date``.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from enum import Enum


class Precision(Enum):
    DAY = "day"
    MONTH = "month"
    YEAR = "year"


def add_years(d: date, years: int) -> date:
    """Calendar-year addition. Keeps month and day; 29 Feb -> 28 Feb when the target year is not
    a leap year. Negative ``years`` subtracts."""
    year = d.year + years
    last_day = calendar.monthrange(year, d.month)[1]
    return date(year, d.month, min(d.day, last_day))


@dataclass(frozen=True)
class PartialDate:
    """A date at DAY, MONTH or YEAR precision. ``month`` and ``day`` are None below the
    stated precision. A day without a month is not a date."""

    year: int
    month: int | None = None
    day: int | None = None

    def __post_init__(self) -> None:
        if self.day is not None and self.month is None:
            raise ValueError("a day requires a month")
        if self.month is not None and not 1 <= self.month <= 12:
            raise ValueError(f"month out of range: {self.month}")
        if self.day is not None:
            last = calendar.monthrange(self.year, self.month)[1]  # type: ignore[arg-type]
            if not 1 <= self.day <= last:
                raise ValueError(f"day out of range: {self.day}")

    @classmethod
    def parse(cls, text: str) -> "PartialDate":
        """'1987-09-14' -> DAY, '1987-09' -> MONTH, '1987' -> YEAR."""
        parts = [int(p) for p in text.strip().split("-")]
        if not 1 <= len(parts) <= 3:
            raise ValueError(f"not a partial date: {text!r}")
        return cls(*parts)

    @property
    def precision(self) -> Precision:
        if self.day is not None:
            return Precision.DAY
        if self.month is not None:
            return Precision.MONTH
        return Precision.YEAR

    @property
    def earliest(self) -> date:
        return date(self.year, self.month or 1, self.day or 1)

    @property
    def latest(self) -> date:
        month = self.month or 12
        day = self.day or calendar.monthrange(self.year, month)[1]
        return date(self.year, month, day)

    def __str__(self) -> str:
        if self.day is not None:
            return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
        if self.month is not None:
            return f"{self.year:04d}-{self.month:02d}"
        return f"{self.year:04d}"


@dataclass(frozen=True)
class DateRange:
    """Closed interval [earliest, latest] of the values a date could take."""

    earliest: date
    latest: date

    def __post_init__(self) -> None:
        if self.earliest > self.latest:
            raise ValueError(f"range is inverted: {self.earliest} > {self.latest}")

    @classmethod
    def of(cls, p: PartialDate) -> "DateRange":
        return cls(p.earliest, p.latest)

    @classmethod
    def exact(cls, d: date) -> "DateRange":
        return cls(d, d)

    @classmethod
    def min_of(cls, a: "DateRange", b: "DateRange") -> "DateRange":
        return cls(min(a.earliest, b.earliest), min(a.latest, b.latest))

    @classmethod
    def max_of(cls, a: "DateRange", b: "DateRange") -> "DateRange":
        return cls(max(a.earliest, b.earliest), max(a.latest, b.latest))

    def add_years(self, years: int) -> "DateRange":
        return DateRange(add_years(self.earliest, years), add_years(self.latest, years))

    @property
    def is_exact(self) -> bool:
        return self.earliest == self.latest

    def entirely_before(self, d: date) -> bool:
        """Every possible value precedes ``d``."""
        return self.latest < d

    def entirely_after(self, d: date) -> bool:
        """Every possible value follows ``d``."""
        return self.earliest > d

    def contains(self, d: date) -> bool:
        return self.earliest <= d <= self.latest

    def display(self) -> str:
        """'2025-09-17' for a day, '2025-09' for exactly a calendar month, '2025' for exactly a
        calendar year, otherwise 'earliest..latest'."""
        e, l = self.earliest, self.latest
        if e == l:
            return e.isoformat()
        if e.day == 1 and l.day == calendar.monthrange(l.year, l.month)[1]:
            if (e.year, e.month) == (l.year, l.month):
                return f"{e.year:04d}-{e.month:02d}"
            if e.month == 1 and l.month == 12 and e.year == l.year:
                return f"{e.year:04d}"
        return f"{e.isoformat()}..{l.isoformat()}"
