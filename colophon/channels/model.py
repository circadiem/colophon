"""Inputs to the channel engine: a work, its grants, notice searches and contractual signals.

Every input that a rule reads is a ``Fact``: a value with the tier and evidence set it came from
(CLAUDE.md I3, I5). The engine propagates the weakest tier it actually read and the union of the
evidence it actually read (Step 0 answer 2.5). Nothing here has a default value that a rule could
mistake for a finding: an unknown is ``None``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Generic, TypeVar

from .dates import PartialDate

T = TypeVar("T")

Tier = int  # 1 document-verified … 4 estimated (CLAUDE.md §3)


@dataclass(frozen=True)
class Evidence:
    """One citation. The I3 fields that describe origin; tier and rule_version sit on the fact
    and the assertion respectively."""

    source_id: str
    url: str
    capture_date: date
    citation_span: str

    def __post_init__(self) -> None:
        if not self.citation_span:
            raise ValueError("no span, no record (CLAUDE.md I2)")


@dataclass(frozen=True)
class Fact(Generic[T]):
    value: T
    tier: Tier
    evidence: tuple[Evidence, ...]

    def __post_init__(self) -> None:
        if not 1 <= self.tier <= 4:
            raise ValueError(f"tier out of range: {self.tier}")
        if not self.evidence:
            raise ValueError("a fact without evidence does not enter the engine (CLAUDE.md I3)")


class RightType(Enum):
    """docs/PRD 'Domain model'. The engine does not branch on right type; it is carried."""

    PUBLICATION = "publication"
    DRAMATIC = "dramatic"
    AUDIO = "audio"
    MERCHANDISE = "merchandise"
    OTHER = "other"


class Grantor(Enum):
    """Who executed the grant. §203 reaches AUTHOR only. §304(c) reaches AUTHOR and
    STATUTORY_SUCCESSOR (Step 0 answer 2.8). OTHER is outside both."""

    AUTHOR = "author"
    STATUTORY_SUCCESSOR = "person entitled to the renewal: widow or widower, children, executor or next of kin"
    OTHER = "anyone else, including an heir or estate outside the renewal class"


class Contribution(Enum):
    """Which contribution a grant covers. Text and art sit in separate chains; a picture book
    with separate agreements is two grants, one per contribution. Does not change the
    arithmetic; it is how a split status is labelled (Manual Research Protocol §D)."""

    TEXT = "text"
    ILLUSTRATION = "illustration"
    BOTH = "both"


class Section(Enum):
    SECTION_203 = "17 U.S.C. § 203"
    SECTION_304C = "17 U.S.C. § 304(c)"
    SECTION_304D = "17 U.S.C. § 304(d)"


@dataclass(frozen=True)
class Grant:
    """One transfer of rights (a graph edge). One book routinely carries several."""

    grant_id: str
    right_types: tuple[RightType, ...]
    grantor: Fact[Grantor]
    executed_on: Fact[PartialDate] | None
    conveys_publication: Fact[bool] | None
    publication_under_grant: Fact[PartialDate] | None  # publication *under this grant* (answer 2.11)
    executing_authors: Fact[int] | None  # joint authors who executed this grant
    work_made_for_hire: Fact[bool] | None
    grantee: str | None = None
    contribution: Contribution | None = None


@dataclass(frozen=True)
class Work:
    work_id: str
    original_publication_date: Fact[PartialDate] | None
    copyright_secured: Fact[PartialDate] | None  # its own input, never derived (answer 2.10)


@dataclass(frozen=True)
class TerminationNotice:
    """A recorded termination notice: a termination under way, by whom, effective when."""

    grant_id: str
    section: Section
    served_on: Fact[PartialDate]
    effective_on: Fact[PartialDate] | None
    terminating_parties: tuple[str, ...]


@dataclass(frozen=True)
class NoticeSearch:
    """A search of the recordation index for termination notices. An empty ``found`` with the
    search parameters and date is a finding, not a null (CLAUDE.md I7)."""

    found: tuple[TerminationNotice, ...]
    parameters: str
    searched_on: date
    tier: Tier
    evidence: tuple[Evidence, ...]

    def __post_init__(self) -> None:
        if not self.evidence:
            raise ValueError("a search result without evidence is not a finding (CLAUDE.md I7)")

    def for_grant(self, grant_id: str, section: Section) -> tuple[TerminationNotice, ...]:
        return tuple(n for n in self.found if n.grant_id == grant_id and n.section is section)


@dataclass(frozen=True)
class OutOfPrintSignals:
    """Channel A, out-of-print archetype (docs/II §03), as pre-evaluated observations.

    The reprint threshold ("no reprint recorded in the last several years") is unresolved in
    docs/II §03 and has no default here; the caller evaluates ``no_reprint_within_threshold``
    against whatever docs/II eventually states (Step 0 answer 2.7).
    """

    no_edition_in_print: Fact[bool]
    no_ebook_or_audio: Fact[bool]
    no_reprint_within_threshold: Fact[bool]
