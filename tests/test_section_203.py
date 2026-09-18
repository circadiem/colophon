"""§203 rule behaviour beyond the worked examples (docs/II §02, CLAUDE.md §4, Step 0 answers)."""

from datetime import date

from colophon.channels import (
    Channel,
    Grant,
    Grantor,
    Reason,
    RightType,
    Section,
    Status,
    StatusResult,
    Undetermined,
    compute,
)

from tests.fixtures.helpers import AS_OF, fact, pd
from tests.fixtures.statutory_cases import CASE_HEIRS_203, CASE_JOINT_TWO


def _one(results):
    assert len(results) == 1, results
    return results[0]


def _grant(**overrides) -> Grant:
    base = dict(
        grant_id="g",
        right_types=(RightType.PUBLICATION, RightType.DRAMATIC),
        grantor=fact(Grantor.AUTHOR, 1, "author signed"),
        executed_on=fact(pd("1986-04"), 1, "executed"),
        conveys_publication=fact(True, 1, "conveys publication"),
        publication_under_grant=fact(pd("1987-09"), 2, "published"),
        executing_authors=fact(1, 1, "author signed"),
        work_made_for_hire=None,
        grantee="publisher",
    )
    base.update(overrides)
    return Grant(**base)


def _work():
    from colophon.channels import Work

    return Work(work_id="w", original_publication_date=fact(pd("1987-09"), 2, "published"), copyright_secured=None)


def test_heir_executed_grant_returns_no_203_window_at_all():
    case = CASE_HEIRS_203
    r = _one(compute(work=case["work"], grants=(case["grant"],), as_of=case["as_of"]))
    assert isinstance(r, Undetermined)
    assert r.section is Section.SECTION_203
    assert r.reason is Reason.GRANTOR_OUT_OF_SCOPE
    assert r.window is None


def test_joint_work_with_two_executing_authors_requires_both():
    case = CASE_JOINT_TWO
    r = _one(compute(work=case["work"], grants=(case["grant"],), as_of=case["as_of"]))
    assert isinstance(r, StatusResult)
    assert r.required_signatories.value == case["expected_required_signatories"]


def test_majority_of_executing_authors():
    for authors, required in ((1, 1), (2, 2), (3, 2), (4, 3), (5, 3)):
        r = _one(compute(work=_work(), grants=(_grant(executing_authors=fact(authors, 1, "n")),), as_of=AS_OF))
        assert r.required_signatories.value == required, authors


def test_missing_execution_date_is_undetermined_not_defaulted():
    """CLAUDE.md §5.1: no presumption rule exists. Do not invent one."""
    r = _one(compute(work=_work(), grants=(_grant(executed_on=None),), as_of=AS_OF))
    assert isinstance(r, Undetermined)
    assert r.reason is Reason.EXECUTION_DATE_REQUIRED
    assert r.window is None


def test_unknown_conveyance_is_undetermined_not_defaulted():
    """'whether it conveys publication is a fact with its own evidence and tier, not a default'."""
    r = _one(compute(work=_work(), grants=(_grant(conveys_publication=None),), as_of=AS_OF))
    assert isinstance(r, Undetermined)
    assert r.reason is Reason.CONVEYANCE_UNKNOWN


def test_conveying_grant_without_publication_date_is_undetermined():
    r = _one(compute(work=_work(), grants=(_grant(publication_under_grant=None),), as_of=AS_OF))
    assert isinstance(r, Undetermined)
    assert r.reason is Reason.PUBLICATION_DATE_REQUIRED


def test_dual_clock_takes_execution_plus_forty_when_publication_is_late():
    g = _grant(executed_on=fact(pd("1980-01-10"), 1, "x"), publication_under_grant=fact(pd("1990-06-01"), 1, "p"))
    r = _one(compute(work=_work(), grants=(g,), as_of=date(2030, 1, 1)))
    assert r.window.window_start.display() == "2020-01-10"  # 1980-01-10 + 40y < 1990-06-01 + 35y
    assert r.window.window_end.display() == "2025-01-10"
    assert r.window.last_serviceable_date.display() == "2023-01-10"


def test_non_conveying_grant_uses_execution_plus_thirty_five():
    g = _grant(conveys_publication=fact(False, 1, "dramatic rights only"), publication_under_grant=None)
    r = _one(compute(work=_work(), grants=(g,), as_of=AS_OF))
    assert r.window.window_start.display() == "2021-04"
    assert r.window.window_end.display() == "2026-04"
    assert r.window.last_serviceable_date.display() == "2024-04"
    assert r.status is Status.LAPSED_WINDOW


def test_status_boundaries_follow_the_termination_window():
    """Step 0 answer 2.1: FUTURE before start, NOW through last_serviceable, LAPSED after."""
    g = _grant(executed_on=fact(pd("1990-01-10"), 1, "x"), publication_under_grant=fact(pd("1991-03-05"), 1, "p"))
    # window_start = min(1991-03-05 + 35y, 1990-01-10 + 40y) = 2026-03-05; last serviceable 2029-03-05
    expectations = {
        date(2026, 3, 4): Status.TERMINABLE_FUTURE,
        date(2026, 3, 5): Status.TERMINABLE_NOW,
        date(2029, 3, 5): Status.TERMINABLE_NOW,
        date(2029, 3, 6): Status.LAPSED_WINDOW,
        date(2030, 6, 1): Status.LAPSED_WINDOW,  # inside the window, past the deadline
    }
    for as_of, expected in expectations.items():
        r = _one(compute(work=_work(), grants=(g,), as_of=as_of))
        assert r.status is expected, as_of
        assert r.estimated is False


def test_year_only_input_that_straddles_as_of_emits_no_status():
    """Step 0 answer 2.3: a straddle emits no status, with the reason and the range."""
    g = _grant(executed_on=fact(pd("1989"), 2, "x"), publication_under_grant=fact(pd("1991"), 2, "p"))
    # window_start range: 2026-01-01 .. 2026-12-31. as_of 2026-09-17 is inside it.
    r = _one(compute(work=_work(), grants=(g,), as_of=AS_OF))
    assert isinstance(r, Undetermined)
    assert r.reason is Reason.STRADDLES_AS_OF
    assert r.window is not None
    assert r.window.window_start.display() == "2026"
    assert r.window.last_serviceable_date.display() == "2029"


def test_year_only_input_that_does_not_straddle_is_estimated():
    g = _grant(executed_on=fact(pd("1989"), 2, "x"), publication_under_grant=fact(pd("1991"), 2, "p"))
    r = _one(compute(work=_work(), grants=(g,), as_of=date(2025, 6, 1)))
    assert isinstance(r, StatusResult)
    assert r.status is Status.TERMINABLE_FUTURE
    assert r.estimated is True
    r = _one(compute(work=_work(), grants=(g,), as_of=date(2030, 1, 1)))
    assert r.status is Status.LAPSED_WINDOW
    assert r.estimated is True


def test_tier_is_the_weakest_input_actually_used():
    """Step 0 answer 2.5: an unread input must not drag the tier down."""
    # Dual clock reads execution (T1), conveyance (T1) and publication (T4) -> T4.
    g = _grant(publication_under_grant=fact(pd("1987-09"), 4, "estimated"))
    r = _one(compute(work=_work(), grants=(g,), as_of=AS_OF))
    assert r.tier == 4
    # Non-conveying branch never reads the publication date -> T1.
    g = _grant(conveys_publication=fact(False, 1, "x"), publication_under_grant=fact(pd("1987-09"), 4, "estimated"))
    r = _one(compute(work=_work(), grants=(g,), as_of=AS_OF))
    assert r.tier == 1
    spans = {e.citation_span for e in r.evidence}
    assert "estimated" not in spans


def test_wfh_short_circuits_before_any_clock():
    g = _grant(executed_on=None, work_made_for_hire=fact(True, 2, "WFH flag on registration"))
    r = _one(compute(work=_work(), grants=(g,), as_of=AS_OF))
    assert isinstance(r, StatusResult)
    assert r.status is Status.EXCLUDED_WFH
    assert r.tier == 2
    assert r.window is None
    assert r.channel is Channel.C


def test_as_of_must_be_a_date_not_a_datetime():
    import datetime as dt

    import pytest

    with pytest.raises(TypeError):
        compute(work=_work(), grants=(_grant(),), as_of=dt.datetime(2026, 9, 17, 12, 0))
