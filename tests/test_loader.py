"""The fixture tables (tests/fixtures/SCHEMA.md) carry everything the hand-built fixtures do."""

from datetime import date
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


# --- Protocol §H and §D send-backs ------------------------------------------------------------

from colophon.channels import Contribution, Reason  # noqa: E402

from tests.fixtures.loader import LoadError, validate_fact_table, COUNTERPARTY_FIELDS, COUNTERPARTY_PREFIXES, DEMAND_FIELDS, DEMAND_PREFIXES  # noqa: E402


def _row(**over):
    base = {"case_id": "II-05-A", "work_id": "II-05-A", "grant_id": "II-05-A/publishing-agreement", "field": "executed_on",
            "value": "1986-04", "tier": "2", "source_id": "second-source", "url": "x", "capture_date": "2026-09-18",
            "citation_span": "a second document agreeing"}
    base.update(over)
    return base


def test_duplicate_field_rows_with_different_values_are_a_contradiction_not_an_error():
    rows = load_csv(HERE / "cases.csv") + [_row(value="1986-05", citation_span="a second document disagreeing")]
    case = build_cases(rows)["II-05-A"]
    assert [c.field for c in case.contradictions] == ["executed_on"]
    assert case.contradictions[0].values == ("1986-04", "1986-05")
    # The contested fact never reaches the engine.
    grant = next(g for g in case.grants if g.grant_id == "II-05-A/publishing-agreement")
    assert grant.executed_on is None
    r = case.run(date.fromisoformat("2026-09-17"))[0]
    assert isinstance(r, Undetermined) and r.reason is Reason.EXECUTION_DATE_REQUIRED
    # And it can be asserted as such.
    ok = check_expectation({"II-05-A": case}, {"case_id": "II-05-A", "grant_id": "II-05-A/publishing-agreement",
                                               "expected": "CONTRADICTION:executed_on"})
    assert ok == []
    bad = check_expectation({"II-05-A": case}, {"case_id": "II-05-A", "grant_id": "II-05-A/publishing-agreement",
                                                "expected": "CONTRADICTION:grantor"})
    assert bad and "found none" in bad[0]


def test_duplicate_field_rows_with_the_same_value_corroborate():
    rows = load_csv(HERE / "cases.csv") + [_row(tier="1")]
    case = build_cases(rows)["II-05-A"]
    assert case.contradictions == ()
    grant = next(g for g in case.grants if g.grant_id == "II-05-A/publishing-agreement")
    assert grant.executed_on.tier == 1  # strongest tier wins
    assert len(grant.executed_on.evidence) == 2  # every citation kept


def test_contested_grantor_drops_the_grant_from_engine_input_but_keeps_the_contradiction():
    rows = load_csv(HERE / "cases.csv") + [_row(field="grantor", value="other", citation_span="estate signed")]
    case = build_cases(rows)["II-05-A"]
    assert [c.field for c in case.contradictions] == ["grantor"]
    assert case.grants == ()


def test_contribution_loads_and_is_carried_on_results():
    case = build_cases(load_csv(HERE / "cases.csv"))["II-05-C"]
    by_id = {g.grant_id: g for g in case.grants}
    assert by_id["II-05-C/text"].contribution is Contribution.TEXT
    assert by_id["II-05-C/art"].contribution is Contribution.ILLUSTRATION
    results = {r.grant_id: r for r in case.run(date.fromisoformat("2026-09-17"))}
    assert results["II-05-C/text"].contribution is Contribution.TEXT
    assert results["II-05-C/art"].contribution is Contribution.ILLUSTRATION


def test_last_reprint_as_a_date_fails_loudly_until_the_threshold_exists():
    import pytest

    rows = [r for r in load_csv(HERE / "cases.csv") if r["field"] != "signals.no_reprint_within_threshold"]
    rows.append(_row(grant_id="", field="signals.last_reprint", value="2011", tier="3", citation_span="last reprint 2011"))
    with pytest.raises(NotImplementedError, match="docs/II"):
        build_cases(rows)


def test_every_row_needs_a_span_a_tier_and_a_capture_date():
    import pytest

    for broken, msg in ((dict(citation_span=""), "no span"), (dict(tier="5"), "tier"), (dict(capture_date="yesterday"), "capture_date")):
        with pytest.raises(LoadError, match=msg):
            build_cases(load_csv(HERE / "cases.csv") + [_row(field="grantee", **broken)])


def test_counterparty_and_demand_tables_validate_and_surface_contradictions():
    import pytest

    header_only_cp = load_csv(HERE / "counterparty.csv")
    header_only_d = load_csv(HERE / "demand.csv")
    assert validate_fact_table(header_only_cp, "counterparty.csv", COUNTERPARTY_FIELDS, COUNTERPARTY_PREFIXES) == []
    assert validate_fact_table(header_only_d, "demand.csv", DEMAND_FIELDS, DEMAND_PREFIXES) == []

    cp = [_row(grant_id="", field="search", value="SSDI + probate index, county X", tier="2", citation_span="no entry found"),
          _row(grant_id="", field="author.living", value="false", tier="2", citation_span="obituary"),
          _row(grant_id="", field="author.living", value="true", tier="3", citation_span="agency page lists as client")]
    found = validate_fact_table(cp, "counterparty.csv", COUNTERPARTY_FIELDS, COUNTERPARTY_PREFIXES)
    assert [c.field for c in found] == ["author.living"]

    with pytest.raises(LoadError, match="search row is required"):
        validate_fact_table(cp[1:], "counterparty.csv", COUNTERPARTY_FIELDS, COUNTERPARTY_PREFIXES)
    with pytest.raises(LoadError, match="unknown field"):
        validate_fact_table([_row(grant_id="", field="author.phone", value="x")], "counterparty.csv", COUNTERPARTY_FIELDS, COUNTERPARTY_PREFIXES)
    ok = [_row(grant_id="", field="adaptation.1.year", value="1994", citation_span="released 1994"),
          _row(grant_id="", field="screen_case", value="Three sentences.", source_id="researcher", citation_span="Three sentences.")]
    assert validate_fact_table(ok, "demand.csv", DEMAND_FIELDS, DEMAND_PREFIXES) == []


def test_termination_interest_fractions_must_sum_to_one():
    import pytest

    base = [_row(grant_id="", field="search", value="probate index", tier="2", citation_span="searched")]
    half = _row(grant_id="g", field="termination_interest.widow.fraction", value="1/2", citation_span="probate")
    quarter = _row(grant_id="g", field="termination_interest.child-a.fraction", value="1/4", citation_span="probate")
    quarter_b = _row(grant_id="g", field="termination_interest.child-b.fraction", value="0.25", citation_span="probate")
    assert validate_fact_table(base + [half, quarter, quarter_b], "counterparty.csv", COUNTERPARTY_FIELDS, COUNTERPARTY_PREFIXES) == []
    with pytest.raises(LoadError, match="sum to 3/4"):
        validate_fact_table(base + [half, quarter], "counterparty.csv", COUNTERPARTY_FIELDS, COUNTERPARTY_PREFIXES)
    with pytest.raises(LoadError, match="fraction must be a number"):
        validate_fact_table(base + [_row(grant_id="g", field="termination_interest.x.fraction", value="half", citation_span="p")],
                            "counterparty.csv", COUNTERPARTY_FIELDS, COUNTERPARTY_PREFIXES)
