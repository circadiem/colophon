"""I4: a corrected rule produces new assertions at a new RULE_VERSION that supersede the old ones.
Nothing is rewritten; the diff between versions is a product output."""

from dataclasses import replace
from datetime import datetime, timezone

from colophon.channels import (
    RULE_VERSION,
    Assertion,
    assertions_from,
    compute,
    render_diff,
    supersede,
)

from .fixtures.worked_examples import EXAMPLE_A, EXAMPLE_B

ASSERTED_AT = datetime(2026, 9, 18, 9, 0, tzinfo=timezone.utc)


def _current(example):
    results = compute(work=example.work, grants=example.grants, as_of=example.as_of,
                      contractual_signals=example.contractual_signals)
    return assertions_from(results, work_id=example.work.work_id, asserted_at=ASSERTED_AT)


def test_assertions_carry_provenance_and_rule_version():
    """I3: every asserted fact carries source, url, capture_date, span, tier, rule_version, asserted_at."""
    for a in _current(EXAMPLE_B):
        assert a.rule_version == RULE_VERSION
        assert a.asserted_at == ASSERTED_AT
        assert a.tier is None or 1 <= a.tier <= 4
        assert a.evidence
        for e in a.evidence:
            assert e.source_id and e.url and e.capture_date and e.citation_span
        assert a.superseded_by is None


def test_bumped_rule_version_supersedes_rather_than_rewrites():
    previous = _current(EXAMPLE_A)
    # Simulate the prior rule build: an earlier version that computed the same facts.
    previous = tuple(replace(a, rule_version="0.0.1", assertion_id=a.assertion_id + "-old") for a in previous)
    current = _current(EXAMPLE_A)

    replay = supersede(previous, current)

    # Old records are retained and marked, never mutated in place.
    assert all(p.superseded_by is None for p in previous)
    assert len(replay.retained) == len(previous)
    assert all(r.superseded_by is not None for r in replay.retained)
    assert {r.assertion_id for r in replay.retained} == {p.assertion_id for p in previous}
    # New records are new.
    assert {a.assertion_id for a in replay.current}.isdisjoint({p.assertion_id for p in previous})
    assert all(a.rule_version == RULE_VERSION for a in replay.current)
    # Same facts under the new version: the diff says so, and it is reviewable.
    assert all(c.kind == "unchanged" for c in replay.diff)
    text = render_diff(replay)
    assert "0.0.1" in text and RULE_VERSION in text


def test_corrected_rule_produces_a_reviewable_diff():
    current = _current(EXAMPLE_A)
    # A prior, wrong build: naive 365-day arithmetic put last_serviceable a few days early.
    previous = tuple(
        replace(a, rule_version="0.0.1", assertion_id=a.assertion_id + "-old",
                object="2025-08-24" if a.predicate == "terminable_on" else a.object)
        for a in current
    )
    replay = supersede(previous, current)
    changed = [c for c in replay.diff if c.kind == "changed"]
    assert len(changed) == 1
    assert changed[0].predicate == "terminable_on"
    assert (changed[0].old, changed[0].new) == ("2025-08-24", "2025-09")
    text = render_diff(replay)
    assert "terminable_on" in text and "2025-08-24" in text and "2025-09" in text


def test_added_and_removed_assertions_appear_in_the_diff():
    previous = tuple(replace(a, rule_version="0.0.1", assertion_id=a.assertion_id + "-old") for a in _current(EXAMPLE_A))
    current = _current(EXAMPLE_A)
    dropped = previous[:-1]
    extra = current + (replace(current[0], assertion_id="extra", predicate="held_by", object="somebody"),)
    replay = supersede(dropped, extra)
    kinds = sorted(c.kind for c in replay.diff)
    assert "added" in kinds and "removed" in kinds


def test_assertion_ids_are_deterministic():
    assert [a.assertion_id for a in _current(EXAMPLE_A)] == [a.assertion_id for a in _current(EXAMPLE_A)]
    assert all(isinstance(a, Assertion) for a in _current(EXAMPLE_A))
