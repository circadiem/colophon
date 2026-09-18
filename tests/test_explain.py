"""explain(): a result readable by eye. Straddles name their candidate statuses."""

from datetime import date

from colophon.channels import Grant, Grantor, RightType, Status, Work, compute, explain, possible_statuses

from tests.fixtures.helpers import AS_OF, fact, pd
from tests.fixtures.statutory_cases import CASE_304D_EXERCISED
from tests.fixtures.worked_examples import EXAMPLE_A


def test_explain_a_status_result():
    r = compute(work=EXAMPLE_A.work, grants=EXAMPLE_A.grants, as_of=AS_OF)[0]
    text = explain(r)
    assert "LAPSED·WINDOW" in text and "tier 2" in text and "estimated" in text
    assert "2022-09 .. 2027-09" in text
    assert "last serviceable  2025-08-31..2025-09-29" in text
    assert "gives LAPSED·WINDOW for every value" in text
    assert "Grant executed April 1986" in text
    assert "rule 0.2.0" in text


def test_explain_a_straddle_names_both_candidates():
    g = Grant(grant_id="g", right_types=(RightType.DRAMATIC,), grantor=fact(Grantor.AUTHOR, 2, "a"),
              executed_on=fact(pd("1989"), 2, "x"), conveys_publication=fact(True, 2, "c"),
              publication_under_grant=fact(pd("1991"), 2, "p"), executing_authors=None, work_made_for_hire=None)
    w = Work(work_id="w", original_publication_date=None, copyright_secured=None)
    r = compute(work=w, grants=(g,), as_of=AS_OF)[0]
    assert possible_statuses(r.window, AS_OF) == (Status.TERMINABLE_FUTURE, Status.TERMINABLE_NOW)
    text = explain(r)
    assert "STRADDLES_AS_OF" in text
    assert "TERMINABLE·FUTURE or TERMINABLE·NOW" in text
    assert "do not pick a status" in text


def test_explain_makes_a_served_notice_loud():
    case = CASE_304D_EXERCISED
    r = compute(work=case["work"], grants=(case["grant"],), as_of=case["as_of"], notice_search=case["notice_search"])[0]
    text = explain(r)
    assert "NOTICE SERVED     1992-05-01 under 17 U.S.C. § 304(c), effective 1994-05-01, by author; incumbent publisher" in text


def test_explain_an_undetermined_without_a_window():
    g = Grant(grant_id="g", right_types=(RightType.DRAMATIC,), grantor=fact(Grantor.AUTHOR, 2, "a"), executed_on=None,
              conveys_publication=None, publication_under_grant=None, executing_authors=None, work_made_for_hire=None)
    w = Work(work_id="w", original_publication_date=None, copyright_secured=None)
    text = explain(compute(work=w, grants=(g,), as_of=date(2026, 9, 17))[0])
    assert "EXECUTION_DATE_REQUIRED" in text and "confirming action" in text and "evidence (0)" in text
