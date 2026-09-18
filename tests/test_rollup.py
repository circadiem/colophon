"""The rollup rule (Step 2 answers): grant is the unit of computation, triple the unit of reporting."""

import pytest

from colophon.channels import (
    LADDER,
    TERMINAL,
    Channel,
    Grant,
    Grantor,
    RightType,
    Status,
    StatusResult,
    Undetermined,
    compute,
    grant_position,
    triple_position,
)

from tests.fixtures.helpers import AS_OF, fact, pd
from tests.fixtures.worked_examples import EXAMPLE_A, EXAMPLE_B, EXAMPLE_C


def _run(example, as_of=None):
    return compute(work=example.work, grants=example.grants, as_of=as_of or example.as_of,
                   contractual_signals=example.contractual_signals)


def test_ladder_is_the_stated_precedence_and_terminal_statuses_are_off_it():
    assert [s.name for s in LADDER] == ["NEVER_GRANTED", "REVERTED_LIKELY", "TERMINABLE_NOW",
                                        "TERMINABLE_FUTURE", "GRANTED_ACTIVE", "LAPSED_WINDOW"]
    assert set(TERMINAL) == {Status.EXCLUDED_WFH, Status.PUBLIC_DOMAIN}
    assert set(LADDER) | set(TERMINAL) == set(Status)


def test_example_a_grant_position_is_the_open_channel_a_route():
    """Level 1 is disjunctive: LAPSED_WINDOW on Channel C, REVERTED_LIKELY on Channel A -> the second."""
    results = _run(EXAMPLE_A)
    # Channel A results carry no grant id; the triple attaches them to the grant under test.
    grant_results = tuple(r for r in results if r.grant_id == EXAMPLE_A.grants[0].grant_id)
    channel_a = next(r for r in results if r.channel is Channel.A)
    pos = grant_position(grant_results + (_attach(channel_a, EXAMPLE_A.grants[0].grant_id),))
    assert pos.status is Status.REVERTED_LIKELY
    assert pos.winner.channel is Channel.A
    assert {r.status for r in pos.constituents if isinstance(r, StatusResult)} == {Status.LAPSED_WINDOW, Status.REVERTED_LIKELY}


def test_example_b_rolls_up_to_terminable_future_with_its_constituent_visible():
    triple = triple_position(EXAMPLE_B.work.work_id, RightType.DRAMATIC, EXAMPLE_B.grants, _run(EXAMPLE_B), territory="US")
    assert triple.status is Status.TERMINABLE_FUTURE
    assert triple.territory == "US"
    assert [g.status for g in triple.grants] == [Status.TERMINABLE_FUTURE]


def test_example_c_rolls_up_blocked_because_the_art_is_excluded():
    """Level 3 is conjunctive: text terminable, art excluded, you cannot make the film with half."""
    triple = triple_position(EXAMPLE_C.work.work_id, RightType.DRAMATIC, EXAMPLE_C.grants, _run(EXAMPLE_C))
    assert triple.status is Status.EXCLUDED_WFH
    assert triple.weakest.contribution.value == "illustration"
    assert {c.contribution.value: c.status for c in triple.constituents} == {
        "text": Status.TERMINABLE_FUTURE, "illustration": Status.EXCLUDED_WFH,
    }
    # The constituents are never hidden by the rolled-up position.
    assert sorted(g.status.name for g in triple.grants) == ["EXCLUDED_WFH", "TERMINABLE_FUTURE"]


def test_terminal_beats_any_channel_within_a_grant():
    _, art = EXAMPLE_C.grants
    results = tuple(r for r in _run(EXAMPLE_C) if r.grant_id == art.grant_id)
    fake_open = _attach(next(r for r in _run(EXAMPLE_A) if r.channel is Channel.A), art.grant_id)
    pos = grant_position(results + (fake_open,))
    assert pos.status is Status.EXCLUDED_WFH


def test_level_two_is_disjunctive_across_grants_of_one_contribution():
    lapsed = _grant("g-lapsed", "1985-01", "1986-01")   # window 2021-01..2026-01, lapsed
    future = _grant("g-future", "1992-01", "1993-01")   # window 2028-01..2033-01, future
    results = compute(work=EXAMPLE_B.work, grants=(lapsed, future), as_of=AS_OF)
    triple = triple_position("w", RightType.DRAMATIC, (lapsed, future), results)
    assert triple.status is Status.TERMINABLE_FUTURE
    assert triple.constituents[0].winner.grant_id == "g-future"


def test_all_undetermined_gives_no_position_and_a_known_blocker_dominates_unknown():
    unknown = _grant("g-unknown", None, "1993-01")
    results = compute(work=EXAMPLE_B.work, grants=(unknown,), as_of=AS_OF)
    assert isinstance(results[0], Undetermined)
    triple = triple_position("w", RightType.DRAMATIC, (unknown,), results)
    assert triple.status is None and triple.weakest.status is None

    _, art = EXAMPLE_C.grants
    results = compute(work=EXAMPLE_C.work, grants=(unknown, art), as_of=AS_OF)
    triple = triple_position("w", RightType.DRAMATIC, (unknown, art), results)
    assert triple.status is Status.EXCLUDED_WFH


def test_right_type_selects_the_grants_in_scope():
    pub_only = _grant("g-pub", "1985-01", "1986-01", right_types=(RightType.PUBLICATION,))
    results = compute(work=EXAMPLE_B.work, grants=(pub_only,), as_of=AS_OF)
    triple = triple_position("w", RightType.DRAMATIC, (pub_only,), results)
    assert triple.constituents == () and triple.status is None


def test_level_one_refuses_results_from_two_grants():
    results = _run(EXAMPLE_C)
    with pytest.raises(ValueError, match="one grant"):
        grant_position(tuple(r for r in results if r.channel is Channel.C))


def _attach(result, grant_id):
    from dataclasses import replace

    return replace(result, grant_id=grant_id)


def _grant(grant_id, executed, published, right_types=(RightType.PUBLICATION, RightType.DRAMATIC)):
    from colophon.channels import Contribution

    return Grant(grant_id=grant_id, right_types=right_types, grantor=fact(Grantor.AUTHOR, 2, "signed"),
                 executed_on=None if executed is None else fact(pd(executed), 2, "executed"),
                 conveys_publication=fact(True, 2, "conveys"), publication_under_grant=fact(pd(published), 2, "published"),
                 executing_authors=fact(1, 2, "signed"), work_made_for_hire=None, grantee="p", contribution=Contribution.TEXT)
