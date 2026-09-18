"""Small constructors so fixtures read as data, not as boilerplate."""

from __future__ import annotations

from datetime import date

from colophon.channels import Evidence, Fact, PartialDate

# The date every fixture is evaluated at unless it says otherwise (Step 0 answer 1.2).
AS_OF = date(2026, 9, 17)

# Fixture evidence is the deliverable itself. Real evidence is a source document; see CLAUDE.md I3.
DOC_II = "docs/II-rights-availability-logic.md"
CAPTURED = date(2026, 9, 18)


def ev(span: str, source_id: str = DOC_II, url: str = "docs/II-rights-availability-logic.md#05") -> Evidence:
    return Evidence(source_id=source_id, url=url, capture_date=CAPTURED, citation_span=span)


def fact(value, tier: int, span: str, source_id: str = DOC_II) -> Fact:
    return Fact(value=value, tier=tier, evidence=(ev(span, source_id=source_id),))


def pd(text: str) -> PartialDate:
    """'1987-09-01' -> day, '1987-09' -> month, '1987' -> year precision."""
    return PartialDate.parse(text)
