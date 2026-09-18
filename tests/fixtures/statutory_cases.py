"""Required statutory cases beyond the worked examples (docs/PRD 'Acceptance criteria and tests',
CLAUDE.md §4, Step 0 answers 2.8-2.13).

- §304(d) refused because the §304(c) window was exercised
- §304(d) available where §304(c) expired before 1998-10-27 unexercised
- a grant executed by heirs returns no §203 window at all
- a joint work requiring both signatories
- §304(c) reaches a statutory successor's grant (heir exclusion is §203-only)
"""

from __future__ import annotations

from datetime import date

from colophon.channels import (
    Grant,
    Grantor,
    NoticeSearch,
    RightType,
    Section,
    TerminationNotice,
    Work,
)

from tests.fixtures.helpers import ev, fact, pd

DOC_PRD = "docs/PRD.md"
ANSWERS = "step-0-answers.md"


def _grant(grant_id: str, executed: str, grantor: Grantor = Grantor.AUTHOR, *, conveys: bool | None = True,
           published: str | None = None, authors: int = 1, wfh: bool | None = None,
           tier: int = 1, span: str = "recorded transfer") -> Grant:
    return Grant(
        grant_id=grant_id,
        right_types=(RightType.PUBLICATION, RightType.DRAMATIC),
        grantor=fact(grantor, tier, span, source_id=DOC_PRD),
        executed_on=fact(pd(executed), tier, span, source_id=DOC_PRD),
        conveys_publication=None if conveys is None else fact(conveys, tier, span, source_id=DOC_PRD),
        publication_under_grant=None if published is None else fact(pd(published), tier, span, source_id=DOC_PRD),
        executing_authors=fact(authors, tier, span, source_id=DOC_PRD),
        work_made_for_hire=None if wfh is None else fact(wfh, tier, span, source_id=DOC_PRD),
        grantee="publisher",
    )


def _work(work_id: str, published: str | None, secured: str | None) -> Work:
    return Work(
        work_id=work_id,
        original_publication_date=None if published is None else fact(pd(published), 2, "registration", source_id=DOC_PRD),
        copyright_secured=None if secured is None else fact(pd(secured), 2, "registration", source_id=DOC_PRD),
    )


def _search(found: tuple[TerminationNotice, ...], span: str) -> NoticeSearch:
    """A recordation-index search is a finding whether or not it found anything (CLAUDE.md I7)."""
    return NoticeSearch(
        found=found,
        parameters="recordation index: termination notices for this work and grantee",
        searched_on=date(2026, 9, 18),
        tier=1,
        evidence=(ev(span, source_id=DOC_PRD, url="docs/PRD.md#data-layer"),),
    )


# --- §304(d) refused: the §304(c) window was exercised -------------------------------------
# Copyright secured March 1935 -> §304(c) window 1991-03 .. 1996-03, expired before 1998-10-27.
# A §304(c) notice was served in 1992, so no §304(d) window exists.

SECURED_1935 = _work("304d-exercised", published="1935-03", secured="1935-03")
GRANT_1935 = _grant("304d-exercised/grant", "1935-06", conveys=True, published="1935-03")
NOTICE_304C_1992 = TerminationNotice(
    grant_id=GRANT_1935.grant_id,
    section=Section.SECTION_304C,
    served_on=fact(pd("1992-05-01"), 1, "recorded termination notice", source_id=DOC_PRD),
    effective_on=fact(pd("1994-05-01"), 1, "recorded termination notice", source_id=DOC_PRD),
    terminating_parties=("author",),
)
SEARCH_FOUND_304C = _search((NOTICE_304C_1992,), "A termination under way, by whom, effective when")

CASE_304D_EXERCISED = {
    "work": SECURED_1935,
    "grant": GRANT_1935,
    "notice_search": SEARCH_FOUND_304C,
    "as_of": date(2026, 9, 17),
    "expected_304c": {"window_start": "1991-03", "window_end": "1996-03", "last_serviceable_date": "1994-03"},
    "expected_sections": (Section.SECTION_304C,),  # no second window
}

# --- §304(d) available: same clock, index searched, nothing found ----------------------------
SEARCH_FOUND_NOTHING = _search((), "recordation before the effective date is mandatory and absence is therefore meaningful")

CASE_304D_AVAILABLE = {
    "work": SECURED_1935,
    "grant": GRANT_1935,
    "notice_search": SEARCH_FOUND_NOTHING,
    "as_of": date(2026, 9, 17),
    "expected_304d": {"window_start": "2010-03", "window_end": "2015-03", "last_serviceable_date": "2013-03"},
    "expected_sections": (Section.SECTION_304C, Section.SECTION_304D),
}

# --- §304(d) not available: §304(c) window did not expire before 1998-10-27 -------------------
# Secured 1945-01 -> §304(c) 2001-01 .. 2006-01. Only one window, ever.
CASE_304D_TOO_LATE = {
    "work": _work("304d-too-late", published="1945-01", secured="1945-01"),
    "grant": _grant("304d-too-late/grant", "1945-02", conveys=True, published="1945-01"),
    "notice_search": SEARCH_FOUND_NOTHING,
    "as_of": date(2026, 9, 17),
    "expected_sections": (Section.SECTION_304C,),
}

# --- A grant executed by heirs returns no §203 window at all ---------------------------------
# "Grants executed by heirs rather than by the author are outside § 203 entirely" (docs/II §02).
CASE_HEIRS_203 = {
    "work": _work("heirs-203", published="1985-05", secured=None),
    "grant": _grant("heirs-203/estate-grant", "1984-01", grantor=Grantor.OTHER, conveys=True, published="1985-05",
                    span="grant executed by the author's estate"),
    "as_of": date(2026, 9, 17),
}

# --- §304(c) reaches a statutory successor's grant (answer 2.8) ------------------------------
# Secured 1970-06, grant executed 1972 by the widow (renewal-entitled). Window 2026-06 .. 2031-06.
CASE_SUCCESSOR_304C = {
    "work": _work("successor-304c", published="1970-06", secured="1970-06"),
    "grant": _grant("successor-304c/widow-grant", "1972-03", grantor=Grantor.STATUTORY_SUCCESSOR,
                    conveys=True, published="1970-06", span="grant executed by the author's widow"),
    "notice_search": SEARCH_FOUND_NOTHING,
    "as_of": date(2026, 9, 17),
    "expected_304c": {"window_start": "2026-06", "window_end": "2031-06", "last_serviceable_date": "2029-06"},
}

# --- A joint work requiring both signatories -------------------------------------------------
# "A picture book signed jointly by author and illustrator therefore needs both when there are
# two." (docs/II §02)
CASE_JOINT_TWO = {
    "work": _work("joint-two", published="1990-10", secured=None),
    "grant": _grant("joint-two/joint-agreement", "1989-08", conveys=True, published="1990-10", authors=2,
                    span="signed jointly by author and illustrator"),
    "as_of": date(2026, 9, 17),
    "expected_required_signatories": 2,
}

# --- Pre-1978 grant over a copyright secured after 1978 (answer 2.4) --------------------------
# "a 1976 contract for a book published in 1979 ... genuinely fits neither section"
CASE_PREDATES_SECURED = {
    "work": _work("predates", published="1979-04", secured="1979-04"),
    "grant": _grant("predates/contract-1976", "1976-09", conveys=True, published="1979-04"),
    "as_of": date(2026, 9, 17),
}
