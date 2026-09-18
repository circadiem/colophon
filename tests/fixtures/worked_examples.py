"""The three worked examples from docs/II-rights-availability-logic.md §05, verbatim.

Example C did not carry the facts its arithmetic needs; the missing facts come from the Step 0
answers (1.1) and are quoted there. All three evaluate at as_of 2026-09-17 (answer 1.2).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from colophon.channels import Grant, Grantor, OutOfPrintSignals, RightType, Status, Work

from .helpers import AS_OF, fact, pd


@dataclass(frozen=True)
class WorkedExample:
    name: str
    quote: str
    work: Work
    grants: tuple[Grant, ...]
    as_of: date
    expected: dict
    contractual_signals: OutOfPrintSignals | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)


# --- A · The missed window --------------------------------------------------------------------

A_QUOTE = (
    "Grant executed April 1986, book published September 1987, publication right conveyed. "
    "Window start is the earlier of 2022-09 and 2026-04, so 2022-09; window ends 2027-09; last "
    "serviceable notice date was 2025-09. Status: LAPSED·WINDOW. The § 203 route is closed "
    "forever — but Channel A remains fully open, which is exactly why a single-channel product "
    "would have discarded this book wrongly."
)

EXAMPLE_A = WorkedExample(
    name="A · The missed window",
    quote=A_QUOTE,
    work=Work(
        work_id="II-05-A",
        original_publication_date=fact(pd("1987-09"), 2, "book published September 1987"),
        copyright_secured=None,
    ),
    grants=(
        Grant(
            grant_id="II-05-A/publishing-agreement",
            right_types=(RightType.PUBLICATION, RightType.DRAMATIC),
            grantor=fact(Grantor.AUTHOR, 2, "Grant executed April 1986"),
            executed_on=fact(pd("1986-04"), 2, "Grant executed April 1986"),
            conveys_publication=fact(True, 2, "publication right conveyed"),
            publication_under_grant=fact(pd("1987-09"), 2, "book published September 1987"),
            executing_authors=fact(1, 2, "Grant executed April 1986"),
            work_made_for_hire=None,
            grantee="publisher-A",
        ),
    ),
    # Channel A is "fully open": the out-of-print signals are supplied pre-evaluated
    # (Step 0 answer 2.7). The reprint threshold itself is unresolved and has no default.
    contractual_signals=OutOfPrintSignals(
        no_edition_in_print=fact(True, 3, "Channel A remains fully open"),
        no_ebook_or_audio=fact(True, 3, "Channel A remains fully open"),
        no_reprint_within_threshold=fact(True, 3, "Channel A remains fully open"),
    ),
    as_of=AS_OF,
    expected={
        "window_start": "2022-09",
        "window_end": "2027-09",
        "last_serviceable_date": "2025-09",
        "status": Status.LAPSED_WINDOW,
        "channel_a_status": Status.REVERTED_LIKELY,
        # Companion assertion (answer 1.2): the clock is injected, not read.
        "status_at_2024_01_01": Status.TERMINABLE_NOW,
    },
)


# --- B · The plannable one --------------------------------------------------------------------

B_QUOTE = (
    "Grant executed June 1991, published March 1992. Window runs 2027-03 to 2032-03; notice may "
    "be served now for effective dates from 2028. Status: TERMINABLE·FUTURE, notice window open. "
    "Eighteen months of relationship-building before anything has to happen — the case the "
    "calendar exists for."
)

EXAMPLE_B = WorkedExample(
    name="B · The plannable one",
    quote=B_QUOTE,
    work=Work(
        work_id="II-05-B",
        original_publication_date=fact(pd("1992-03"), 2, "published March 1992"),
        copyright_secured=None,
    ),
    grants=(
        Grant(
            grant_id="II-05-B/publishing-agreement",
            right_types=(RightType.PUBLICATION, RightType.DRAMATIC),
            grantor=fact(Grantor.AUTHOR, 2, "Grant executed June 1991"),
            executed_on=fact(pd("1991-06"), 2, "Grant executed June 1991"),
            # The example does not say so in words; the stated window (2027-03 = 1992-03 + 35y)
            # is only reachable on the dual-clock branch, so conveyance is what the example asserts.
            conveys_publication=fact(True, 2, "Window runs 2027-03 to 2032-03"),
            publication_under_grant=fact(pd("1992-03"), 2, "published March 1992"),
            executing_authors=fact(1, 2, "Grant executed June 1991"),
            work_made_for_hire=None,
            grantee="publisher-B",
        ),
    ),
    as_of=AS_OF,
    expected={
        "window_start": "2027-03",
        "window_end": "2032-03",
        "last_serviceable_date": "2030-03",
        "status": Status.TERMINABLE_FUTURE,
        # "notice may be served now": notice service opened ten years before the window.
        "notice_servable_from": "2017-03",
        # "for effective dates from 2028": served at as_of, the earliest effective date is
        # max(window_start, as_of + 2y) = 2028-09-17.
        "earliest_effective_if_served_at_as_of": "2028-09-17",
    },
)


# --- C · The two-chain picture book ----------------------------------------------------------

C_QUOTE = (
    "Author and illustrator signed separate agreements with the same publisher in 1989. Two "
    "grants, two clocks, two terminating parties, and an illustrator agreement that may carry a "
    "work-made-for-hire recital as a supplementary work. Status: split — text TERMINABLE·FUTURE, "
    "art EXCLUDED·WFH pending document review. The film asset is usually the look, so a split "
    "status is a downgrade, not a partial win."
)

C_ANSWER = (
    "Text grant: executed April 1989, published November 1991, conveys the right of publication. "
    "Art grant: executed April 1989, separate agreement, same publisher, carries a "
    "work-made-for-hire recital as a supplementary work. Recital present, not verified against "
    "the document. ... The art grant is EXCLUDED_WFH at tier 2 — VII rates a WFH flag as T2 — "
    "with confirming_action = obtain the illustrator agreement. \"Pending document review\" means "
    "tier 2, not a separate state."
)

EXAMPLE_C = WorkedExample(
    name="C · The two-chain picture book",
    quote=C_QUOTE,
    work=Work(
        work_id="II-05-C",
        original_publication_date=fact(pd("1991-11"), 2, "published November 1991", source_id="step-0-answers.md"),
        copyright_secured=None,
    ),
    grants=(
        Grant(
            grant_id="II-05-C/text",
            right_types=(RightType.PUBLICATION, RightType.DRAMATIC),
            grantor=fact(Grantor.AUTHOR, 2, "Author and illustrator signed separate agreements"),
            executed_on=fact(pd("1989-04"), 2, "Text grant: executed April 1989", source_id="step-0-answers.md"),
            conveys_publication=fact(True, 2, "conveys the right of publication", source_id="step-0-answers.md"),
            publication_under_grant=fact(pd("1991-11"), 2, "published November 1991", source_id="step-0-answers.md"),
            executing_authors=fact(1, 2, "separate agreements"),
            work_made_for_hire=None,
            grantee="publisher-C",
        ),
        Grant(
            grant_id="II-05-C/art",
            right_types=(RightType.PUBLICATION, RightType.DRAMATIC),
            grantor=fact(Grantor.AUTHOR, 2, "Author and illustrator signed separate agreements"),
            executed_on=fact(pd("1989-04"), 2, "Art grant: executed April 1989", source_id="step-0-answers.md"),
            conveys_publication=None,
            publication_under_grant=None,
            executing_authors=fact(1, 2, "separate agreements"),
            # "Recital present, not verified against the document": a WFH flag is tier-2
            # evidence (docs/VII §02). Tier carries "pending document review"; there is no
            # separate state.
            work_made_for_hire=fact(
                True, 2, "carries a work-made-for-hire recital as a supplementary work",
                source_id="step-0-answers.md",
            ),
            grantee="publisher-C",
        ),
    ),
    as_of=AS_OF,
    expected={
        "text": {
            "window_start": "2026-11",
            "window_end": "2031-11",
            "last_serviceable_date": "2029-11",
            "status": Status.TERMINABLE_FUTURE,
            # Companion assertion (answer 1.1): the window opens two months after as_of.
            "status_at_2026_12_01": Status.TERMINABLE_NOW,
        },
        "art": {
            "status": Status.EXCLUDED_WFH,
            "tier": 2,
            "confirming_action_mentions": "agreement",
        },
    },
    notes=(C_ANSWER,),
)

WORKED_EXAMPLES = (EXAMPLE_A, EXAMPLE_B, EXAMPLE_C)
