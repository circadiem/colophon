"""Run all channels on every work and never let one channel's result suppress another
(docs/PRD 'Channel B', CLAUDE.md §3). Channel A here is the out-of-print archetype only, fed
pre-evaluated signals; its threshold is unresolved (Step 0 answer 2.7)."""

from colophon.channels import (
    OUT_OF_PRINT_REPRINT_THRESHOLD_YEARS,
    Channel,
    OutOfPrintSignals,
    Reason,
    Status,
    StatusResult,
    Undetermined,
    compute,
)

from tests.fixtures.helpers import AS_OF, fact
from tests.fixtures.worked_examples import EXAMPLE_A


def test_reprint_threshold_has_no_default():
    assert OUT_OF_PRINT_REPRINT_THRESHOLD_YEARS is None


def test_lapsed_203_and_open_channel_a_coexist():
    results = compute(
        work=EXAMPLE_A.work, grants=EXAMPLE_A.grants, as_of=AS_OF, contractual_signals=EXAMPLE_A.contractual_signals
    )
    by_channel = {}
    for r in results:
        by_channel.setdefault(r.channel, []).append(r)
    assert by_channel[Channel.C][0].status is Status.LAPSED_WINDOW
    assert by_channel[Channel.A][0].status is Status.REVERTED_LIKELY


def test_channel_a_without_signals_is_an_explicit_no_signal_finding():
    signals = OutOfPrintSignals(
        no_edition_in_print=fact(False, 3, "in print"),
        no_ebook_or_audio=fact(True, 3, "no ebook"),
        no_reprint_within_threshold=fact(True, 3, "no reprint"),
    )
    results = compute(work=EXAMPLE_A.work, grants=(), as_of=AS_OF, contractual_signals=signals)
    assert len(results) == 1
    r = results[0]
    assert r.channel is Channel.A
    assert isinstance(r, Undetermined)
    assert r.reason is Reason.NO_SIGNAL


def test_channel_a_tier_is_capped_by_its_weakest_input():
    signals = OutOfPrintSignals(
        no_edition_in_print=fact(True, 4, "absence"),
        no_ebook_or_audio=fact(True, 3, "no ebook"),
        no_reprint_within_threshold=fact(True, 3, "no reprint"),
    )
    results = compute(work=EXAMPLE_A.work, grants=(), as_of=AS_OF, contractual_signals=signals)
    r = results[0]
    assert isinstance(r, StatusResult)
    assert r.tier == 4
