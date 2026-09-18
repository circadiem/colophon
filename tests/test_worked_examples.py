"""Every worked example in docs/II §05 must exist as a fixture and pass (CLAUDE.md §4, §9)."""

from datetime import date

import pytest

from colophon.channels import (
    RULE_VERSION,
    Channel,
    Section,
    Status,
    StatusResult,
    compute,
)

from .fixtures.worked_examples import EXAMPLE_A, EXAMPLE_B, EXAMPLE_C, WORKED_EXAMPLES


def _channel_c(results, grant_id):
    found = [r for r in results if r.channel is Channel.C and r.grant_id == grant_id]
    assert len(found) == 1, found
    return found[0]


def _run(example, as_of=None):
    return compute(
        work=example.work,
        grants=example.grants,
        as_of=as_of or example.as_of,
        contractual_signals=example.contractual_signals,
    )


@pytest.mark.parametrize("example", WORKED_EXAMPLES, ids=[e.name for e in WORKED_EXAMPLES])
def test_every_result_is_stamped_and_evidenced(example):
    """I5: status with tier and evidence. I6: RULE_VERSION on every result."""
    for r in _run(example):
        assert r.rule_version == RULE_VERSION
        assert r.as_of == example.as_of
        if isinstance(r, StatusResult):
            assert 1 <= r.tier <= 4
            assert r.evidence, "a status without evidence is not a status"


# --- A ---------------------------------------------------------------------------------------


def test_example_a_missed_window():
    r = _channel_c(_run(EXAMPLE_A), EXAMPLE_A.grants[0].grant_id)
    exp = EXAMPLE_A.expected
    assert isinstance(r, StatusResult)
    assert r.section is Section.SECTION_203
    assert r.window.window_start.display() == exp["window_start"]
    assert r.window.window_end.display() == exp["window_end"]
    assert r.window.last_serviceable_date.display() == exp["last_serviceable_date"]
    assert r.status is exp["status"]
    assert r.estimated is True  # month-precision inputs: a range, not a false day
    assert r.tier == 2


def test_example_a_channel_a_remains_open_alongside_the_lapsed_window():
    """One channel's result never suppresses another (docs/II §05 A, CLAUDE.md §3 'channel')."""
    results = _run(EXAMPLE_A)
    c = _channel_c(results, EXAMPLE_A.grants[0].grant_id)
    a = [r for r in results if r.channel is Channel.A]
    assert c.status is Status.LAPSED_WINDOW
    assert len(a) == 1 and isinstance(a[0], StatusResult)
    assert a[0].status is EXAMPLE_A.expected["channel_a_status"]
    assert a[0].tier == 3


def test_example_a_clock_is_injected_not_read():
    r = _channel_c(_run(EXAMPLE_A, as_of=date(2024, 1, 1)), EXAMPLE_A.grants[0].grant_id)
    assert r.status is EXAMPLE_A.expected["status_at_2024_01_01"]


# --- B ---------------------------------------------------------------------------------------


def test_example_b_plannable():
    r = _channel_c(_run(EXAMPLE_B), EXAMPLE_B.grants[0].grant_id)
    exp = EXAMPLE_B.expected
    assert isinstance(r, StatusResult)
    assert r.window.window_start.display() == exp["window_start"]
    assert r.window.window_end.display() == exp["window_end"]
    assert r.window.last_serviceable_date.display() == exp["last_serviceable_date"]
    assert r.status is exp["status"]


def test_example_b_notice_window_is_a_field_not_a_status():
    """'notice may be served now for effective dates from 2028' (Step 0 answer 2.1)."""
    r = _channel_c(_run(EXAMPLE_B), EXAMPLE_B.grants[0].grant_id)
    exp = EXAMPLE_B.expected
    assert r.window.notice_servable_from.display() == exp["notice_servable_from"]
    assert r.window.notice_servable_from.entirely_before(EXAMPLE_B.as_of)
    assert r.window.earliest_effective_if_served_at_as_of.display() == exp["earliest_effective_if_served_at_as_of"]


# --- C ---------------------------------------------------------------------------------------


def test_example_c_text_chain_terminable_future():
    text, _ = EXAMPLE_C.grants
    r = _channel_c(_run(EXAMPLE_C), text.grant_id)
    exp = EXAMPLE_C.expected["text"]
    assert isinstance(r, StatusResult)
    assert r.window.window_start.display() == exp["window_start"]
    assert r.window.window_end.display() == exp["window_end"]
    assert r.window.last_serviceable_date.display() == exp["last_serviceable_date"]
    assert r.status is exp["status"]
    assert r.required_signatories.value == 1


def test_example_c_text_chain_opens_two_months_later():
    text, _ = EXAMPLE_C.grants
    r = _channel_c(_run(EXAMPLE_C, as_of=date(2026, 12, 1)), text.grant_id)
    assert r.status is EXAMPLE_C.expected["text"]["status_at_2026_12_01"]


def test_example_c_art_chain_excluded_wfh_at_tier_two():
    _, art = EXAMPLE_C.grants
    r = _channel_c(_run(EXAMPLE_C), art.grant_id)
    exp = EXAMPLE_C.expected["art"]
    assert isinstance(r, StatusResult)
    assert r.status is exp["status"]
    assert r.tier == exp["tier"]
    assert r.window is None
    assert exp["confirming_action_mentions"] in r.confirming_action


def test_example_c_is_a_split_result_of_two_channel_c_results():
    """Split is a property of the pair of triples, not a ninth status."""
    results = [r for r in _run(EXAMPLE_C) if r.channel is Channel.C]
    assert sorted(r.status.name for r in results) == ["EXCLUDED_WFH", "TERMINABLE_FUTURE"]
