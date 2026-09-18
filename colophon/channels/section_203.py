"""17 U.S.C. § 203 — termination of grants executed by the author on or after 1978-01-01.

Governing text: docs/II §02 "§ 203", CLAUDE.md §4, Step 0 answers 2.1-2.5, 2.11-2.13.

    window_start = if grant conveys the right of publication:
                     min( publication_date + 35y , execution_date + 40y )
                   else execution_date + 35y
    window_end   = window_start + 5y                       (exclusive)
    last_serviceable_date = window_end - 2y                (the real deadline)
    notice_servable_from  = window_start - 10y

Read this top to bottom with the statute open. Each numbered step is one condition.
"""

from __future__ import annotations

from datetime import date

from .dates import DateRange
from .model import Fact, Grant, Grantor, NoticeSearch, Section
from .reading import Reading, status_in_window
from .results import Channel, ChannelResult, NoticeSummary, StatusResult, StatutoryWindow, Undetermined
from .status import Reason, Status
from .version import RULE_VERSION

WFH_CONFIRMING_ACTION = (
    "Obtain the executed agreement and verify the work-made-for-hire recital against the document."
)


def required_signatories(executing_authors: int) -> int:
    """§203(a)(1): for a joint work, a majority of the authors who executed the grant.
    Two signatories need both; three need two (docs/II §02 'Who holds the right')."""
    if executing_authors < 1:
        raise ValueError("a grant has at least one executing author")
    return executing_authors // 2 + 1


def notice_summary(grant: Grant, section: Section, search: NoticeSearch | None) -> NoticeSummary | None:
    """A served notice is surfaced, not turned into a status (answer 2.12). The window math does
    not read it, so it does not enter the status tier; it carries its own."""
    if search is None:
        return None
    notices = search.for_grant(grant.grant_id, section)
    if not notices:
        return None
    n = min(notices, key=lambda n: n.served_on.value.earliest)
    return NoticeSummary(
        section=section,
        served_on=DateRange.of(n.served_on.value),
        effective_on=None if n.effective_on is None else DateRange.of(n.effective_on.value),
        terminating_parties=n.terminating_parties,
        incumbent=grant.grantee,
        tier=n.served_on.tier,
        evidence=n.served_on.evidence,
    )


def evaluate_203(grant: Grant, as_of: date, notice_search: NoticeSearch | None = None) -> ChannelResult:
    read = Reading()
    common = dict(channel=Channel.C, section=Section.SECTION_203, grant_id=grant.grant_id, as_of=as_of,
                  rule_version=RULE_VERSION)

    def undetermined(reason: Reason, detail: str = "", window: StatutoryWindow | None = None,
                     action: str | None = None) -> Undetermined:
        return Undetermined(**common, tier=read.tier, evidence=read.evidence, estimated=False, window=window,
                            required_signatories=None, notice=notice_summary(grant, Section.SECTION_203, notice_search),
                            reason=reason, detail=detail, confirming_action=action)

    # 1. § 203(a): "other than a copyright in a work made for hire". No termination right exists.
    if grant.work_made_for_hire is not None and read.read(grant.work_made_for_hire):
        return StatusResult(**common, tier=read.tier, evidence=read.evidence, estimated=False, window=None,
                            required_signatories=None, notice=None, status=Status.EXCLUDED_WFH,
                            confirming_action=WFH_CONFIRMING_ACTION)

    # 2. § 203(a): "executed by the author". Grants by heirs or an estate are outside § 203
    #    entirely (docs/II §02). Hard exclusion, not a penalty (CLAUDE.md §4).
    if read.read(grant.grantor) is not Grantor.AUTHOR:
        return undetermined(Reason.GRANTOR_OUT_OF_SCOPE,
                            detail=f"grantor is {grant.grantor.value.name}; § 203 reaches grants executed by the author")

    # 3. The clock needs an execution date. No presumption rule exists (CLAUDE.md §5.1).
    if grant.executed_on is None:
        return undetermined(Reason.EXECUTION_DATE_REQUIRED,
                            action="Locate the execution date: a recorded transfer, the registration's transfer "
                                   "statement, or the agreement.")
    executed = DateRange.of(read.read(grant.executed_on))

    # 4. § 203(a)(3): which clock. Whether the grant covers the right of publication is a fact
    #    with its own evidence and tier, not a default (CLAUDE.md §4).
    if grant.conveys_publication is None:
        return undetermined(Reason.CONVEYANCE_UNKNOWN,
                            action="Establish whether the grant conveys the right of publication: the recorded "
                                   "transfer's scope or the agreement.")
    if read.read(grant.conveys_publication):
        # 4a. "...thirty-five years from the date of publication of the work under the grant or at
        #      the end of forty years from the date of execution of the grant, whichever term ends
        #      earlier." Publication *under the grant* (answer 2.11).
        if grant.publication_under_grant is None:
            return undetermined(Reason.PUBLICATION_DATE_REQUIRED,
                                action="Establish the date of first publication under this grant.")
        published = DateRange.of(read.read(grant.publication_under_grant))
        start = DateRange.min_of(published.add_years(35), executed.add_years(40))
    else:
        # 4b. "...at the end of thirty-five years from the date of execution of the grant".
        start = executed.add_years(35)

    # 5. § 203(a)(3)-(4): five-year window; notice not less than two nor more than ten years
    #    before the effective date, recorded before it. last_serviceable_date is the deadline.
    window = StatutoryWindow.from_start(start, as_of)

    # 6. § 203(a)(1): majority of the executing authors of a joint work.
    signatories = None
    if grant.executing_authors is not None:
        signatories = Fact(value=required_signatories(grant.executing_authors.value),
                           tier=grant.executing_authors.tier, evidence=grant.executing_authors.evidence)

    # 7. Where as_of sits. A straddle is no status, with the range attached (answer 2.3).
    status = status_in_window(window, as_of)
    notice = notice_summary(grant, Section.SECTION_203, notice_search)
    if status is None:
        return Undetermined(**common, tier=read.tier, evidence=read.evidence, estimated=True, window=window,
                            required_signatories=signatories, notice=notice, reason=Reason.STRADDLES_AS_OF,
                            detail=f"window_start {window.window_start.display()}, last_serviceable "
                                   f"{window.last_serviceable_date.display()}, as_of {as_of.isoformat()}")
    return StatusResult(**common, tier=read.tier, evidence=read.evidence, estimated=not window.is_exact,
                        window=window, required_signatories=signatories, notice=notice, status=status)
