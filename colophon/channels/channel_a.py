"""Channel A — contractual reversion, out-of-print archetype only (docs/II §03).

    Out of print: no edition in print; no ebook or audio edition offered; no reprint recorded in
    the last several years.  -> REVERTED·LIKELY, tier 3

"Several years" is not a number anywhere in docs/II. The threshold below has no default and the
caller supplies ``no_reprint_within_threshold`` already evaluated (Step 0 answer 2.7). The other
three archetypes (availability floor, non-exploitation of subrights, imprint dissolution) and
Channel B are not implemented in this build.

Reversion under these clauses is request-activated. The finding is "this author could likely get
these rights back by asking", a conversation and not a claim (docs/II §03).
"""

from __future__ import annotations

from datetime import date

from .model import OutOfPrintSignals
from .reading import Reading
from .results import Channel, ChannelResult, StatusResult, Undetermined
from .status import Reason, Status
from .version import RULE_VERSION

# TODO(docs/II §03): "no reprint recorded in the last several years" — the number is unresolved.
# Deliverable 00 §03 says presumption thresholds were closed in II; they were not. No default.
OUT_OF_PRINT_REPRINT_THRESHOLD_YEARS: int | None = None

OUT_OF_PRINT_ARCHETYPE_TIER = 3

CONFIRMING_ACTION = "Confirm in-print status and reversion terms with the publisher's permissions desk."


def evaluate_out_of_print(signals: OutOfPrintSignals, as_of: date) -> ChannelResult:
    read = Reading()
    fired = (read.read(signals.no_edition_in_print)
             and read.read(signals.no_ebook_or_audio)
             and read.read(signals.no_reprint_within_threshold))
    common = dict(channel=Channel.A, section=None, grant_id=None, as_of=as_of, rule_version=RULE_VERSION,
                  estimated=False, window=None, required_signatories=None, notice=None)
    if not fired:
        return Undetermined(**common, tier=read.tier, evidence=read.evidence, reason=Reason.NO_SIGNAL,
                            detail="out-of-print archetype: not every signal fired")
    # The archetype is tier 3 at best; weaker inputs make it weaker (answer 2.5).
    tier = max(OUT_OF_PRINT_ARCHETYPE_TIER, read.tier or OUT_OF_PRINT_ARCHETYPE_TIER)
    return StatusResult(**common, tier=tier, evidence=read.evidence, status=Status.REVERTED_LIKELY,
                        confirming_action=CONFIRMING_ACTION)
