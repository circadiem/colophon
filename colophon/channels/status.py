"""The status enum (docs/II §01, CLAUDE.md §3) and the reasons a result can be undetermined.

Exactly eight statuses. Display forms use the interpunct, code uses underscores, and both live
here and nowhere else. A ninth value needs a doc edit first.

``Reason`` is not a status. An ``Undetermined`` result carries one when no status can be emitted
without guessing (Step 0 answer 2.4; same shape as R5's "no status emitted").
"""

from __future__ import annotations

from enum import Enum


class Status(Enum):
    EXCLUDED_WFH = "work made for hire — no termination right exists, ever"
    PUBLIC_DOMAIN = "term expired or renewal not made — no acquisition needed"
    NEVER_GRANTED = "no evidence the right ever left the author"
    REVERTED_LIKELY = "out-of-print or lapsed-option signals"
    TERMINABLE_NOW = "window open, notice can still be served in time"
    TERMINABLE_FUTURE = "window computed, opens on a date"
    LAPSED_WINDOW = "window passed or notice deadline missed — permanently closed"
    GRANTED_ACTIVE = "held and exploited — monitor only"

    @property
    def display(self) -> str:
        return self.name.replace("_", "·")

    @property
    def gloss(self) -> str:
        return self.value


class Reason(Enum):
    """Why no status was emitted. Enumerated, never free text."""

    EXECUTION_DATE_REQUIRED = "§203 needs an execution date and no presumption rule exists (CLAUDE.md §5.1)"
    PUBLICATION_DATE_REQUIRED = "the grant conveys publication, so the dual clock needs the publication date under the grant"
    CONVEYANCE_UNKNOWN = "whether the grant conveys the right of publication is unknown; it is a fact, not a default"
    COPYRIGHT_SECURED_REQUIRED = "§304 runs from the date copyright was secured, which is its own input"
    GRANTOR_OUT_OF_SCOPE = "the grantor is outside the section: §203 is author-executed only; §304(c) reaches the author or a renewal-entitled successor"
    GRANT_PREDATES_SECURED_COPYRIGHT = "grant executed before 1978 over a copyright secured on or after 1978-01-01; fits neither §203 nor §304 as written — manual, carried to counsel"
    SECTION_AMBIGUOUS = "the execution or secured date range straddles a statutory boundary, so the governing section cannot be chosen"
    STRADDLES_AS_OF = "the input precision leaves as_of inside a status boundary; two statuses are possible"
    TERMINATION_SEARCH_REQUIRED = "§304(d) requires that §304(c) was not exercised; absence is a finding and no recordation search was supplied (CLAUDE.md I7)"
    SECTION_304D_ELIGIBILITY_AMBIGUOUS = "the §304(c) window's expiry range straddles 1998-10-27"
    NO_SIGNAL = "the channel was evaluated and none of its signals fired"
