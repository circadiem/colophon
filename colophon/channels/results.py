"""What the engine returns.

Two result kinds, both stamped with RULE_VERSION and as_of:

- ``StatusResult``: one of the eight statuses, with tier, evidence, the window (if any), the
  estimated flag, the required-signatory count and any served notice.
- ``Undetermined``: no status, with an enumerated ``Reason`` and, where computed, the window
  whose range caused the straddle. It is not a ninth status (Step 0 answer 2.4).

Results are per grant and per channel. There is no triple-level merge: docs/II §01's "exactly
one status per triple" is overstated and the merge rule is a pending doc edit (answer 2.6).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum

from .dates import DateRange, add_years
from .model import Evidence, Fact, Section, Tier
from .status import Reason, Status


class Channel(Enum):
    A = "contractual reversion"
    B = "option lapse"
    C = "statutory termination"


@dataclass(frozen=True)
class StatutoryWindow:
    """The termination window and the notice dates that hang off it.

    ``window_end`` is exclusive: the window is [window_start, window_end).
    ``last_serviceable_date`` is the primary date surfaced to the operator (CLAUDE.md §4).
    ``notice_servable_from`` is when notice service opens: ten years before the window.
    ``earliest_effective_if_served_at_as_of`` answers "served today, when could it take effect":
    the later of window_start and as_of + 2y.
    """

    window_start: DateRange
    window_end: DateRange
    last_serviceable_date: DateRange
    notice_servable_from: DateRange
    earliest_effective_if_served_at_as_of: DateRange

    @classmethod
    def from_start(cls, start: DateRange, as_of: date) -> "StatutoryWindow":
        end = start.add_years(5)
        return cls(
            window_start=start,
            window_end=end,
            last_serviceable_date=end.add_years(-2),
            notice_servable_from=start.add_years(-10),
            earliest_effective_if_served_at_as_of=DateRange.max_of(start, DateRange.exact(add_years(as_of, 2))),
        )

    @property
    def is_exact(self) -> bool:
        return self.window_start.is_exact


@dataclass(frozen=True)
class NoticeSummary:
    """A served notice, surfaced on the result. Not a status; "contested" is a scoring
    attribute (Step 0 answer 2.12)."""

    section: Section
    served_on: DateRange
    effective_on: DateRange | None
    terminating_parties: tuple[str, ...]
    incumbent: str | None
    tier: Tier
    evidence: tuple[Evidence, ...]


@dataclass(frozen=True)
class ChannelResult:
    channel: Channel
    section: Section | None
    grant_id: str | None
    as_of: date
    rule_version: str
    tier: Tier | None
    evidence: tuple[Evidence, ...]
    estimated: bool
    window: StatutoryWindow | None
    required_signatories: Fact[int] | None
    notice: NoticeSummary | None


@dataclass(frozen=True)
class StatusResult(ChannelResult):
    status: Status
    confirming_action: str | None = None

    def __post_init__(self) -> None:
        if self.tier is None or not self.evidence:
            raise ValueError("a status without tier and evidence is not a status (CLAUDE.md I5)")


@dataclass(frozen=True)
class Undetermined(ChannelResult):
    reason: Reason
    detail: str = ""
    confirming_action: str | None = None
