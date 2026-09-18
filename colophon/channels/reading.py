"""Helpers shared by the rule modules: what a rule read, and where as_of sits in a window."""

from __future__ import annotations

from datetime import date
from typing import TypeVar

from .model import Evidence, Fact, Tier
from .results import StatutoryWindow
from .status import Status

T = TypeVar("T")


class Reading:
    """Accumulates the facts a rule actually read, so the result carries the weakest tier it
    depended on and the union of that evidence, and nothing it never looked at
    (CLAUDE.md I5; Step 0 answer 2.5)."""

    def __init__(self) -> None:
        self._facts: list[Fact] = []

    def read(self, fact: Fact[T]) -> T:
        self._facts.append(fact)
        return fact.value

    def note(self, tier: Tier, evidence: tuple[Evidence, ...]) -> None:
        """Record a non-Fact input that was read (a notice search)."""
        self._facts.append(Fact(value=None, tier=tier, evidence=evidence))

    @property
    def tier(self) -> Tier | None:
        return max((f.tier for f in self._facts), default=None)

    @property
    def evidence(self) -> tuple[Evidence, ...]:
        seen: list[Evidence] = []
        for f in self._facts:
            for e in f.evidence:
                if e not in seen:
                    seen.append(e)
        return tuple(seen)


def status_in_window(window: StatutoryWindow, as_of: date) -> Status | None:
    """The three statuses describe the termination window, not the notice window
    (Step 0 answer 2.1):

        TERMINABLE_FUTURE   as_of <  window_start
        TERMINABLE_NOW      window_start <= as_of <= last_serviceable_date
        LAPSED_WINDOW       as_of >  last_serviceable_date

    With ranged inputs each boundary is a range. A status is returned only when every possible
    value of the inputs gives the same one; otherwise None, and the caller emits Undetermined
    with STRADDLES_AS_OF (answer 2.3). Precision over recall.
    """
    start, last = window.window_start, window.last_serviceable_date
    if start.entirely_after(as_of):
        return Status.TERMINABLE_FUTURE
    if last.entirely_before(as_of):
        return Status.LAPSED_WINDOW
    if start.latest <= as_of <= last.earliest:
        return Status.TERMINABLE_NOW
    return None
