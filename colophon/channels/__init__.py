"""channels/ — the statutory date engine. Pure functions over a work and its grant edges.

No I/O, no database, no network, no model, no clock reads except an injected ``as_of``
(CLAUDE.md I6). Governing text: docs/II-rights-availability-logic.md and CLAUDE.md §4.
"""

from .channel_a import OUT_OF_PRINT_REPRINT_THRESHOLD_YEARS, evaluate_out_of_print, no_reprint_within_threshold
from .explain import explain, possible_statuses
from .dates import DateRange, PartialDate, Precision, add_years
from .engine import channel_c, compute
from .model import (
    Contribution,
    Evidence,
    Fact,
    Grant,
    Grantor,
    NoticeSearch,
    OutOfPrintSignals,
    RightType,
    Section,
    TerminationNotice,
    Tier,
    Work,
)
from .replay import Assertion, Change, Replay, Subject, assertions_from, render_diff, supersede
from .results import Channel, ChannelResult, NoticeSummary, StatusResult, StatutoryWindow, Undetermined
from .section_203 import evaluate_203, required_signatories
from .section_304 import evaluate_304
from .status import Reason, Status
from .version import RULE_VERSION

__all__ = [
    "RULE_VERSION", "OUT_OF_PRINT_REPRINT_THRESHOLD_YEARS",
    "DateRange", "PartialDate", "Precision", "add_years",
    "Contribution", "Evidence", "Fact", "Grant", "Grantor", "NoticeSearch", "OutOfPrintSignals", "RightType", "Section",
    "TerminationNotice", "Tier", "Work",
    "Channel", "ChannelResult", "NoticeSummary", "StatusResult", "StatutoryWindow", "Undetermined",
    "Reason", "Status",
    "compute", "channel_c", "evaluate_203", "evaluate_304", "evaluate_out_of_print", "required_signatories",
    "no_reprint_within_threshold", "explain", "possible_statuses",
    "Assertion", "Change", "Replay", "Subject", "assertions_from", "render_diff", "supersede",
]
