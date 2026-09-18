"""The fixture tables (tests/fixtures/SCHEMA.md) carry everything the hand-built fixtures do."""

from pathlib import Path

from colophon.channels import Undetermined, compute

from tests.fixtures.loader import build_cases, check_expectation, load_csv
from tests.fixtures.worked_examples import WORKED_EXAMPLES

HERE = Path(__file__).parent / "fixtures"


def test_every_expectation_row_passes():
    cases = build_cases(load_csv(HERE / "cases.csv"))
    problems = []
    for row in load_csv(HERE / "expectations.csv"):
        problems.extend(check_expectation(cases, row))
    assert not problems, "\n".join(problems)


def test_table_cases_reproduce_the_hand_built_fixtures():
    cases = build_cases(load_csv(HERE / "cases.csv"))
    for example in WORKED_EXAMPLES:
        from_table = cases[example.work.work_id].run(example.as_of)
        by_hand = compute(work=example.work, grants=example.grants, as_of=example.as_of,
                          contractual_signals=example.contractual_signals)
        assert from_table == by_hand, example.name


def test_a_mismatch_is_reported_not_swallowed():
    cases = build_cases(load_csv(HERE / "cases.csv"))
    row = {"case_id": "II-05-A", "grant_id": "II-05-A/publishing-agreement", "as_of": "2026-09-17", "channel": "C",
           "section": "203", "expected": "TERMINABLE_NOW", "window_start": "2022-10"}
    problems = check_expectation(cases, row)
    assert any("expected TERMINABLE_NOW, got LAPSED_WINDOW" in p for p in problems)
    assert any("window_start: expected 2022-10, got 2022-09" in p for p in problems)


def test_notices_require_a_search_row():
    import pytest

    rows = load_csv(HERE / "cases.csv")
    rows.append({"case_id": "II-05-A", "work_id": "II-05-A", "grant_id": "II-05-A/publishing-agreement",
                 "field": "notice.1.section", "value": "203", "tier": "1", "source_id": "x", "url": "x",
                 "capture_date": "2026-09-18", "citation_span": "x"})
    rows.append({**rows[-1], "field": "notice.1.served_on", "value": "2024-01-01"})
    with pytest.raises(ValueError, match="I7"):
        build_cases(rows)
