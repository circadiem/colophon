"""Render a channel result for a human auditor.

The 100-title manual audit is a standing job (docs/PRD 'Acceptance criteria and tests'), so a
result has to be readable by eye. Straddles come first: they are the results that need a person.
Pure: text in, text out, no clock.
"""

from __future__ import annotations

from datetime import date

from .results import ChannelResult, StatusResult, StatutoryWindow, Undetermined
from .status import Reason, Status


def possible_statuses(window: StatutoryWindow, as_of: date) -> tuple[Status, ...]:
    """Every status some value inside the input ranges would give. One entry means settled."""
    start, last = window.window_start, window.last_serviceable_date
    out: list[Status] = []
    if as_of < start.latest:
        out.append(Status.TERMINABLE_FUTURE)
    if start.earliest <= as_of <= last.latest:
        out.append(Status.TERMINABLE_NOW)
    if as_of > last.earliest:
        out.append(Status.LAPSED_WINDOW)
    return tuple(out)


def _window_lines(window: StatutoryWindow, as_of: date) -> list[str]:
    lines = [
        f"  window            {window.window_start.display()} .. {window.window_end.display()} (end exclusive)",
        f"  last serviceable  {window.last_serviceable_date.display()}   <- the real deadline",
        f"  notice servable   from {window.notice_servable_from.display()}",
        f"  served at as_of   effective no earlier than {window.earliest_effective_if_served_at_as_of.display()}",
    ]
    candidates = possible_statuses(window, as_of)
    if len(candidates) == 1:
        lines.append(f"  as_of {as_of.isoformat()} gives {candidates[0].display} for every value in the ranges")
    else:
        names = " or ".join(c.display for c in candidates)
        lines.append(f"  as_of {as_of.isoformat()} sits inside a boundary range: {names} depending on the true date")
        if Status.TERMINABLE_FUTURE in candidates and Status.TERMINABLE_NOW in candidates:
            lines.append(f"    window_start could be any day {window.window_start.display()}; "
                         f"FUTURE if it falls after as_of, NOW if on or before")
        if Status.TERMINABLE_NOW in candidates and Status.LAPSED_WINDOW in candidates:
            lines.append(f"    last serviceable could be any day {window.last_serviceable_date.display()}; "
                         f"NOW if it falls on or after as_of, LAPSED if before")
        lines.append("    resolve by narrowing the input precision; do not pick a status")
    return lines


def explain(result: ChannelResult) -> str:
    section = result.section.value if result.section else "section not determined"
    grant = result.grant_id or "no grant"
    lines = [f"Channel {result.channel.name} · {section} · {grant} · as of {result.as_of.isoformat()} · rule {result.rule_version}"]

    if isinstance(result, StatusResult):
        tier = f"tier {result.tier}"
        est = " · estimated (ranged inputs)" if result.estimated else ""
        lines.append(f"  status            {result.status.display} · {tier}{est}")
        lines.append(f"                    {result.status.gloss}")
    elif isinstance(result, Undetermined):
        tier = f"tier {result.tier}" if result.tier is not None else "no tier"
        lines.append(f"  no status         {result.reason.name} · {tier}")
        lines.append(f"                    {result.reason.value}")
        if result.detail:
            lines.append(f"                    {result.detail}")

    if result.window is not None:
        lines.extend(_window_lines(result.window, result.as_of))

    if result.required_signatories is not None:
        s = result.required_signatories
        lines.append(f"  signatories       {s.value} required (majority of executing authors) · tier {s.tier}")

    if result.notice is not None:
        n = result.notice
        eff = f", effective {n.effective_on.display()}" if n.effective_on else ""
        who = ", ".join(n.terminating_parties) or "unnamed parties"
        inc = f"; incumbent {n.incumbent}" if n.incumbent else ""
        lines.append(f"  NOTICE SERVED     {n.served_on.display()} under {n.section.value}{eff}, by {who}{inc} · tier {n.tier}")

    action = getattr(result, "confirming_action", None)
    if action:
        lines.append(f"  confirming action {action}")

    lines.append(f"  evidence ({len(result.evidence)})")
    for e in result.evidence:
        span = e.citation_span if len(e.citation_span) <= 80 else e.citation_span[:77] + "..."
        lines.append(f"    {e.source_id} · captured {e.capture_date.isoformat()} · \"{span}\"")
    return "\n".join(lines)
