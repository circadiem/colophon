"""Assertions and replay (CLAUDE.md I4; docs/IV §03).

``assertions_from`` turns channel results into provenance-bearing assertion records stamped with
RULE_VERSION and an injected ``asserted_at``. ``supersede`` compares a previous build's
assertions with the current build's: old records are returned marked ``superseded_by`` (as new
objects; the inputs are never mutated), current records are returned as-is, and the diff between
the two versions is returned as data and can be rendered for review. Nothing is rewritten.

Predicates used here: ``status``, ``terminable_on`` (the last serviceable date), ``undetermined``.
docs/IV §03 lists held_by | terminable_on | reverted | adapted_by; ``status`` and ``undetermined``
are additions this module needs and are flagged for a doc edit.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace
from datetime import datetime

from .model import Contribution, Evidence, Section, Tier
from .results import Channel, ChannelResult, StatusResult, Undetermined


@dataclass(frozen=True)
class Subject:
    work_id: str
    grant_id: str | None
    channel: Channel
    section: Section | None
    territory: str | None = None  # the caller's; channels/ never branches on it
    contribution: Contribution | None = None  # labels a split result; see docs/backlog.md

    def key(self) -> str:
        return "|".join([self.work_id, self.grant_id or "-", self.channel.name,
                         self.section.name if self.section else "-", self.territory or "-",
                         self.contribution.value if self.contribution else "-"])


@dataclass(frozen=True)
class Assertion:
    assertion_id: str
    subject: Subject
    predicate: str
    object: str
    tier: Tier | None
    evidence: tuple[Evidence, ...]
    rule_version: str
    asserted_at: datetime
    superseded_by: str | None = None


def _assertion_id(subject: Subject, predicate: str, obj: str, rule_version: str, asserted_at: datetime) -> str:
    raw = "\x1f".join([subject.key(), predicate, obj, rule_version, asserted_at.isoformat()])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _make(subject: Subject, predicate: str, obj: str, result: ChannelResult, asserted_at: datetime) -> Assertion:
    return Assertion(
        assertion_id=_assertion_id(subject, predicate, obj, result.rule_version, asserted_at),
        subject=subject, predicate=predicate, object=obj, tier=result.tier, evidence=result.evidence,
        rule_version=result.rule_version, asserted_at=asserted_at,
    )


def assertions_from(results: tuple[ChannelResult, ...], work_id: str, asserted_at: datetime,
                    territory: str | None = None) -> tuple[Assertion, ...]:
    out: list[Assertion] = []
    for r in results:
        subject = Subject(work_id=work_id, grant_id=r.grant_id, channel=r.channel, section=r.section, territory=territory,
                          contribution=r.contribution)
        if isinstance(r, StatusResult):
            out.append(_make(subject, "status", r.status.name, r, asserted_at))
            if r.window is not None:
                out.append(_make(subject, "terminable_on", r.window.last_serviceable_date.display(), r, asserted_at))
        elif isinstance(r, Undetermined):
            out.append(_make(subject, "undetermined", r.reason.name, r, asserted_at))
    return tuple(out)


@dataclass(frozen=True)
class Change:
    kind: str  # "unchanged" | "changed" | "added" | "removed"
    subject: Subject
    predicate: str
    old: str | None
    new: str | None
    old_version: str | None
    new_version: str | None


@dataclass(frozen=True)
class Replay:
    retained: tuple[Assertion, ...]  # previous assertions, marked superseded_by; new objects
    current: tuple[Assertion, ...]
    diff: tuple[Change, ...]


def supersede(previous: tuple[Assertion, ...], current: tuple[Assertion, ...]) -> Replay:
    """Pure. Returns marked copies of ``previous``; never mutates either input."""
    by_key_prev = {(a.subject.key(), a.predicate): a for a in previous}
    by_key_cur = {(a.subject.key(), a.predicate): a for a in current}
    retained: list[Assertion] = []
    diff: list[Change] = []
    for key, old in by_key_prev.items():
        new = by_key_cur.get(key)
        if new is None:
            retained.append(replace(old, superseded_by="removed"))
            diff.append(Change("removed", old.subject, old.predicate, old.object, None, old.rule_version, None))
            continue
        retained.append(replace(old, superseded_by=new.assertion_id))
        kind = "unchanged" if old.object == new.object else "changed"
        diff.append(Change(kind, old.subject, old.predicate, old.object, new.object, old.rule_version, new.rule_version))
    for key, new in by_key_cur.items():
        if key not in by_key_prev:
            diff.append(Change("added", new.subject, new.predicate, None, new.object, None, new.rule_version))
    return Replay(retained=tuple(retained), current=tuple(current), diff=tuple(diff))


def render_diff(replay: Replay) -> str:
    """A reviewable text diff between rule versions. A product output, not a log line."""
    versions_old = sorted({c.old_version for c in replay.diff if c.old_version})
    versions_new = sorted({c.new_version for c in replay.diff if c.new_version})
    lines = [f"rule_version {', '.join(versions_old) or '-'} -> {', '.join(versions_new) or '-'}"]
    marks = {"unchanged": "=", "changed": "~", "added": "+", "removed": "-"}
    for c in replay.diff:
        mark = marks[c.kind]
        if c.kind == "changed":
            body = f"{c.old} -> {c.new}"
        else:
            body = c.new if c.new is not None else c.old
        lines.append(f"{mark} {c.subject.key()} {c.predicate}: {body}")
    return "\n".join(lines)
