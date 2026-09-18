"""Run every channel on a work and return the results side by side.

No channel's result suppresses another's (CLAUDE.md §3 'channel'; docs/II §05 Example A). No
triple-level merge is performed: that rule is a pending doc edit (Step 0 answer 2.6). Territory
is not an input here; the caller forms the (work, right_type, territory) triple (answer 3).
"""

from __future__ import annotations

from datetime import date

from .channel_a import evaluate_out_of_print
from .dates import DateRange
from .model import Grant, NoticeSearch, OutOfPrintSignals, Section, Work
from .reading import Reading
from .results import Channel, ChannelResult, StatusResult, Undetermined
from .section_203 import WFH_CONFIRMING_ACTION, evaluate_203
from .section_304 import EFFECTIVE_DATE_OF_1976_ACT, evaluate_304
from .status import Reason, Status
from .version import RULE_VERSION


def _check_as_of(as_of: date) -> None:
    # datetime is a subclass of date; a statutory clock has no time of day.
    if type(as_of) is not date:
        raise TypeError(f"as_of must be a datetime.date, got {type(as_of).__name__}")


def channel_c(work: Work, grant: Grant, as_of: date, notice_search: NoticeSearch | None = None) -> tuple[ChannelResult, ...]:
    """Choose the section by the grant's execution date and evaluate it."""
    _check_as_of(as_of)
    read = Reading()
    if grant.executed_on is None:
        # Section unknown without an execution date. A WFH flag still settles it.
        if grant.work_made_for_hire is not None and read.read(grant.work_made_for_hire):
            return (StatusResult(channel=Channel.C, section=None, grant_id=grant.grant_id, contribution=grant.contribution, as_of=as_of,
                                 rule_version=RULE_VERSION, tier=read.tier, evidence=read.evidence, estimated=False,
                                 window=None, required_signatories=None, notice=None, status=Status.EXCLUDED_WFH,
                                 confirming_action=WFH_CONFIRMING_ACTION),)
        return (Undetermined(channel=Channel.C, section=None, grant_id=grant.grant_id, contribution=grant.contribution, as_of=as_of,
                             rule_version=RULE_VERSION, tier=None, evidence=(), estimated=False, window=None,
                             required_signatories=None, notice=None, reason=Reason.EXECUTION_DATE_REQUIRED,
                             confirming_action="Locate the execution date: a recorded transfer, the registration's "
                                               "transfer statement, or the agreement."),)
    executed = DateRange.of(grant.executed_on.value)
    if executed.earliest >= EFFECTIVE_DATE_OF_1976_ACT:
        return (evaluate_203(grant, as_of, notice_search),)          # § 203: on or after 1978-01-01
    if executed.entirely_before(EFFECTIVE_DATE_OF_1976_ACT):
        return evaluate_304(work, grant, as_of, notice_search)         # § 304: before 1978-01-01
    read.read(grant.executed_on)
    return (Undetermined(channel=Channel.C, section=None, grant_id=grant.grant_id, contribution=grant.contribution, as_of=as_of,
                         rule_version=RULE_VERSION, tier=read.tier, evidence=read.evidence, estimated=True,
                         window=None, required_signatories=None, notice=None, reason=Reason.SECTION_AMBIGUOUS,
                         detail=f"execution date {executed.display()} straddles 1978-01-01"),)


def compute(work: Work, grants: tuple[Grant, ...], as_of: date, notice_search: NoticeSearch | None = None,
            contractual_signals: OutOfPrintSignals | None = None) -> tuple[ChannelResult, ...]:
    """All channels, every grant, one as_of. Results are per grant and per channel."""
    _check_as_of(as_of)
    results: list[ChannelResult] = []
    for grant in grants:
        results.extend(channel_c(work, grant, as_of, notice_search))
    if contractual_signals is not None:
        results.append(evaluate_out_of_print(contractual_signals, as_of))
    return tuple(results)
