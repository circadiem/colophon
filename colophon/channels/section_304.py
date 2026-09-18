"""17 U.S.C. § 304(c) and § 304(d) — termination of pre-1978 grants.

Governing text: docs/II §02 "§ 304(c) and § 304(d)", CLAUDE.md §4, Step 0 answers 2.4, 2.8-2.10.

    304(c): window = max(copyright_secured + 56y, 1978-01-01) … +5y
    304(d): only if the 304(c) window had expired by 1998-10-27 and was not exercised
            → window = copyright_secured + 75y … +5y

The notice rule is the same as § 203: not less than two nor more than ten years before the
effective date, so last_serviceable_date = window_end - 2y applies here too (answer 2.9).
The heir exclusion is § 203-only: § 304(c) reaches grants by the author or by the persons
entitled to the renewal (answer 2.8).
"""

from __future__ import annotations

from datetime import date

from .dates import DateRange
from .model import Fact, Grant, Grantor, NoticeSearch, Section, Work
from .reading import Reading, status_in_window
from .results import Channel, ChannelResult, StatusResult, StatutoryWindow, Undetermined
from .section_203 import WFH_CONFIRMING_ACTION, notice_summary, required_signatories
from .status import Reason, Status
from .version import RULE_VERSION

EFFECTIVE_DATE_OF_1976_ACT = date(1978, 1, 1)
SONNY_BONO_ACT_DATE = date(1998, 10, 27)  # § 304(d): "on the effective date of the Sonny Bono Copyright Term Extension Act"

IN_SCOPE_304 = (Grantor.AUTHOR, Grantor.STATUTORY_SUCCESSOR)


def evaluate_304(work: Work, grant: Grant, as_of: date,
                 notice_search: NoticeSearch | None = None) -> tuple[ChannelResult, ...]:
    """Returns the § 304(c) result and, where a second window exists or its existence cannot be
    settled, a § 304(d) result. A § 304(d) window that is definitely unavailable produces no
    result: the § 304(c) result carries the served notice or the late expiry that rules it out."""
    read = Reading()

    def common(section: Section) -> dict:
        return dict(channel=Channel.C, section=section, grant_id=grant.grant_id, as_of=as_of, rule_version=RULE_VERSION)

    def undetermined(section: Section, reason: Reason, detail: str = "", action: str | None = None) -> Undetermined:
        return Undetermined(**common(section), tier=read.tier, evidence=read.evidence, estimated=False, window=None,
                            required_signatories=None, notice=None, reason=reason, detail=detail, confirming_action=action)

    # 1. § 304(c): "other than a copyright in a work made for hire".
    if grant.work_made_for_hire is not None and read.read(grant.work_made_for_hire):
        return (StatusResult(**common(Section.SECTION_304C), tier=read.tier, evidence=read.evidence, estimated=False,
                             window=None, required_signatories=None, notice=None, status=Status.EXCLUDED_WFH,
                             confirming_action=WFH_CONFIRMING_ACTION),)

    # 2. § 304(c): grants "executed before January 1, 1978, by any of the persons designated by
    #    subsection (a)(1)(C)": the author, or the renewal-entitled successors.
    if read.read(grant.grantor) not in IN_SCOPE_304:
        return (undetermined(Section.SECTION_304C, Reason.GRANTOR_OUT_OF_SCOPE,
                             detail=f"grantor is {grant.grantor.value.name}; § 304(c) reaches the author or a "
                                    "person entitled to the renewal"),)

    # 3. The clock runs from the date copyright was originally secured: its own input, never
    #    derived from the publication date (answer 2.10).
    if work.copyright_secured is None:
        return (undetermined(Section.SECTION_304C, Reason.COPYRIGHT_SECURED_REQUIRED,
                             action="Establish when copyright was secured: registration or first publication with notice."),)
    secured = DateRange.of(read.read(work.copyright_secured))

    # 4. § 304 applies to copyrights subsisting on 1978-01-01. A pre-1978 grant over a copyright
    #    secured later fits neither section as written; manual, carried to counsel (answer 2.4).
    if secured.earliest >= EFFECTIVE_DATE_OF_1976_ACT:
        return (undetermined(Section.SECTION_304C, Reason.GRANT_PREDATES_SECURED_COPYRIGHT,
                             detail=f"grant executed before 1978 over a copyright secured {secured.display()}",
                             action="Route to manual review; the governing section is a counsel question."),)
    if not secured.entirely_before(EFFECTIVE_DATE_OF_1976_ACT):
        return (undetermined(Section.SECTION_304C, Reason.SECTION_AMBIGUOUS,
                             detail=f"copyright secured {secured.display()} straddles 1978-01-01"),)

    # 5. § 304(c)(3): five years beginning at the end of fifty-six years from the date copyright
    #    was originally secured, or beginning on January 1, 1978, whichever is later.
    start_c = DateRange.max_of(secured.add_years(56), DateRange.exact(EFFECTIVE_DATE_OF_1976_ACT))
    window_c = StatutoryWindow.from_start(start_c, as_of)

    signatories = None
    if grant.executing_authors is not None:
        signatories = Fact(value=required_signatories(grant.executing_authors.value),
                           tier=grant.executing_authors.tier, evidence=grant.executing_authors.evidence)

    notice_c = notice_summary(grant, Section.SECTION_304C, notice_search)
    status_c = status_in_window(window_c, as_of)
    if status_c is None:
        result_c: ChannelResult = Undetermined(
            **common(Section.SECTION_304C), tier=read.tier, evidence=read.evidence, estimated=True, window=window_c,
            required_signatories=signatories, notice=notice_c, reason=Reason.STRADDLES_AS_OF,
            detail=f"window_start {window_c.window_start.display()}, last_serviceable "
                   f"{window_c.last_serviceable_date.display()}, as_of {as_of.isoformat()}")
    else:
        result_c = StatusResult(**common(Section.SECTION_304C), tier=read.tier, evidence=read.evidence,
                                estimated=not window_c.is_exact, window=window_c, required_signatories=signatories,
                                notice=notice_c, status=status_c)

    # 6. § 304(d): only where "the termination right provided in subsection (c) has expired by
    #    [1998-10-27]" and "the author or owner of the termination right has not previously
    #    exercised such termination right". Encode the condition; do not assume availability.
    expiry = window_c.window_end  # exclusive bound: the window has expired by X once end <= X
    if expiry.earliest > SONNY_BONO_ACT_DATE:
        return (result_c,)  # 304(c) window still open on 1998-10-27: no second window, ever
    if not (expiry.latest <= SONNY_BONO_ACT_DATE):
        return (result_c, undetermined(Section.SECTION_304D, Reason.SECTION_304D_ELIGIBILITY_AMBIGUOUS,
                                       detail=f"§ 304(c) window end {expiry.display()} straddles 1998-10-27"))

    # 7. "Not exercised" is an absence finding. It needs a recordation search (CLAUDE.md I7).
    if notice_search is None:
        return (result_c, undetermined(Section.SECTION_304D, Reason.TERMINATION_SEARCH_REQUIRED,
                                       action="Search the recordation index for a § 304(c) termination notice on this "
                                              "work and grantee; record the search whether or not it finds one."))
    if notice_c is not None:
        return (result_c,)  # § 304(c) was exercised: no § 304(d) window
    read.note(notice_search.tier, notice_search.evidence)

    # 8. § 304(d)(2): five years beginning at the end of seventy-five years from the date
    #    copyright was originally secured.
    window_d = StatutoryWindow.from_start(secured.add_years(75), as_of)
    status_d = status_in_window(window_d, as_of)
    if status_d is None:
        result_d: ChannelResult = Undetermined(
            **common(Section.SECTION_304D), tier=read.tier, evidence=read.evidence, estimated=True, window=window_d,
            required_signatories=signatories, notice=None, reason=Reason.STRADDLES_AS_OF,
            detail=f"window_start {window_d.window_start.display()}, last_serviceable "
                   f"{window_d.last_serviceable_date.display()}, as_of {as_of.isoformat()}")
    else:
        result_d = StatusResult(**common(Section.SECTION_304D), tier=read.tier, evidence=read.evidence,
                                estimated=not window_d.is_exact, window=window_d, required_signatories=signatories,
                                notice=None, status=status_d)
    return (result_c, result_d)
