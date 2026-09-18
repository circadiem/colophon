"""§304(c) and §304(d) (docs/II §02, CLAUDE.md §4, Step 0 answers 2.4, 2.8, 2.9, 2.10)."""

from datetime import date

from colophon.channels import (
    Grantor,
    Reason,
    Section,
    Status,
    StatusResult,
    Undetermined,
    compute,
)

from .fixtures.statutory_cases import (
    CASE_304D_AVAILABLE,
    CASE_304D_EXERCISED,
    CASE_304D_TOO_LATE,
    CASE_PREDATES_SECURED,
    CASE_SUCCESSOR_304C,
    SEARCH_FOUND_NOTHING,
    _grant,
    _work,
)


def _run(case, **overrides):
    kwargs = dict(work=case["work"], grants=(case["grant"],), as_of=case["as_of"], notice_search=case.get("notice_search"))
    kwargs.update(overrides)
    return compute(**kwargs)


def _by_section(results):
    return {r.section: r for r in results}


def test_304d_returns_no_second_window_because_304c_was_exercised():
    results = _run(CASE_304D_EXERCISED)
    assert tuple(r.section for r in results) == CASE_304D_EXERCISED["expected_sections"]
    c = _by_section(results)[Section.SECTION_304C]
    exp = CASE_304D_EXERCISED["expected_304c"]
    assert c.window.window_start.display() == exp["window_start"]
    assert c.window.window_end.display() == exp["window_end"]
    assert c.window.last_serviceable_date.display() == exp["last_serviceable_date"]
    assert c.status is Status.LAPSED_WINDOW
    # The served notice is surfaced on the result, not turned into a status (answer 2.12).
    assert c.notice is not None
    assert c.notice.served_on.display() == "1992-05-01"
    assert c.notice.incumbent == "publisher"
    assert c.notice.terminating_parties == ("author",)


def test_304d_available_when_304c_expired_before_1998_10_27_unexercised():
    results = _run(CASE_304D_AVAILABLE)
    assert tuple(r.section for r in results) == CASE_304D_AVAILABLE["expected_sections"]
    d = _by_section(results)[Section.SECTION_304D]
    exp = CASE_304D_AVAILABLE["expected_304d"]
    assert isinstance(d, StatusResult)
    assert d.window.window_start.display() == exp["window_start"]
    assert d.window.window_end.display() == exp["window_end"]
    assert d.window.last_serviceable_date.display() == exp["last_serviceable_date"]
    assert d.status is Status.LAPSED_WINDOW
    # The absence finding is evidence the §304(d) result relies on (I7).
    assert any("absence" in e.citation_span for e in d.evidence)


def test_304d_not_available_when_304c_window_ran_past_1998_10_27():
    results = _run(CASE_304D_TOO_LATE)
    assert tuple(r.section for r in results) == (Section.SECTION_304C,)


def test_304d_needs_a_notice_search_before_it_can_say_unexercised():
    """Absence is a finding (I7): without a search, exercise is unknown, not presumed."""
    results = _run(CASE_304D_AVAILABLE, notice_search=None)
    d = _by_section(results)[Section.SECTION_304D]
    assert isinstance(d, Undetermined)
    assert d.reason is Reason.TERMINATION_SEARCH_REQUIRED
    assert d.window is None


def test_304c_reaches_a_statutory_successors_grant():
    """Heir exclusion is §203-only (answer 2.8)."""
    results = _run(CASE_SUCCESSOR_304C)
    c = _by_section(results)[Section.SECTION_304C]
    exp = CASE_SUCCESSOR_304C["expected_304c"]
    assert isinstance(c, StatusResult)
    assert c.window.window_start.display() == exp["window_start"]
    assert c.window.window_end.display() == exp["window_end"]
    assert c.window.last_serviceable_date.display() == exp["last_serviceable_date"]
    assert c.status is Status.TERMINABLE_NOW


def test_304c_rejects_a_grantor_outside_the_renewal_class():
    case = CASE_SUCCESSOR_304C
    g = _grant("other/grant", "1972-03", grantor=Grantor.OTHER, conveys=True, published="1970-06")
    results = _run(case, grants=(g,))
    assert len(results) == 1
    assert isinstance(results[0], Undetermined)
    assert results[0].reason is Reason.GRANTOR_OUT_OF_SCOPE


def test_304c_applies_the_1978_floor():
    """Window starts at the later of secured + 56y and 1978-01-01 (answer 2.9)."""
    w = _work("floor", published="1920-05", secured="1920-05")
    g = _grant("floor/grant", "1921-01", conveys=True, published="1920-05")
    results = compute(work=w, grants=(g,), as_of=date(2026, 9, 17), notice_search=SEARCH_FOUND_NOTHING)
    c = _by_section(results)[Section.SECTION_304C]
    assert c.window.window_start.display() == "1978-01-01"
    assert c.window.window_end.display() == "1983-01-01"
    assert c.window.last_serviceable_date.display() == "1981-01-01"
    assert c.window.notice_servable_from.display() == "1968-01-01"


def test_304_requires_copyright_secured_as_its_own_input():
    """Never derived from original_publication_date (answer 2.10)."""
    w = _work("nosecured", published="1970-06", secured=None)
    g = _grant("nosecured/grant", "1972-03", conveys=True, published="1970-06")
    results = compute(work=w, grants=(g,), as_of=date(2026, 9, 17))
    assert len(results) == 1
    assert isinstance(results[0], Undetermined)
    assert results[0].reason is Reason.COPYRIGHT_SECURED_REQUIRED


def test_pre_1978_grant_over_post_1978_copyright_fits_neither_section():
    results = _run(CASE_PREDATES_SECURED)
    assert len(results) == 1
    r = results[0]
    assert isinstance(r, Undetermined)
    assert r.reason is Reason.GRANT_PREDATES_SECURED_COPYRIGHT
    assert r.window is None


def test_304c_wfh_is_excluded():
    w = _work("wfh", published="1970-06", secured="1970-06")
    g = _grant("wfh/grant", "1969-01", conveys=True, published="1970-06", wfh=True, tier=2)
    results = compute(work=w, grants=(g,), as_of=date(2026, 9, 17))
    assert len(results) == 1
    assert results[0].status is Status.EXCLUDED_WFH
