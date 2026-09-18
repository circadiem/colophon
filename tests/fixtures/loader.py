"""Turn the fixture tables (tests/fixtures/SCHEMA.md) into engine inputs and regression checks.

Row parsing is pure; the only file I/O is ``load_csv``, and it lives here in the test layer, not
in channels/.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from colophon.channels import (
    ChannelResult,
    Evidence,
    Fact,
    Grant,
    Grantor,
    NoticeSearch,
    OutOfPrintSignals,
    PartialDate,
    RightType,
    Section,
    StatusResult,
    TerminationNotice,
    Undetermined,
    Work,
    compute,
)

SECTIONS = {"203": Section.SECTION_203, "304c": Section.SECTION_304C, "304d": Section.SECTION_304D}
GRANTORS = {"author": Grantor.AUTHOR, "statutory_successor": Grantor.STATUTORY_SUCCESSOR, "other": Grantor.OTHER}


@dataclass(frozen=True)
class Case:
    case_id: str
    work: Work
    grants: tuple[Grant, ...]
    notice_search: NoticeSearch | None
    signals: OutOfPrintSignals | None

    def run(self, as_of: date) -> tuple[ChannelResult, ...]:
        return compute(work=self.work, grants=self.grants, as_of=as_of, notice_search=self.notice_search,
                       contractual_signals=self.signals)


def _bool(v: str) -> bool:
    if v.strip().lower() in ("true", "yes", "1"):
        return True
    if v.strip().lower() in ("false", "no", "0"):
        return False
    raise ValueError(f"not a boolean: {v!r}")


def _fact(row: dict, value) -> Fact:
    ev = Evidence(source_id=row["source_id"], url=row["url"], capture_date=date.fromisoformat(row["capture_date"]),
                  citation_span=row["citation_span"])
    return Fact(value=value, tier=int(row["tier"]), evidence=(ev,))


def load_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_cases(rows: list[dict]) -> dict[str, Case]:
    by_case: dict[str, list[dict]] = {}
    for r in rows:
        by_case.setdefault(r["case_id"], []).append(r)
    return {cid: _build_case(cid, rs) for cid, rs in by_case.items()}


def _build_case(case_id: str, rows: list[dict]) -> Case:
    work_ids = {r["work_id"] for r in rows}
    if len(work_ids) != 1:
        raise ValueError(f"{case_id}: one work per case, got {sorted(work_ids)}")
    work_fields: dict[str, Fact] = {}
    grant_fields: dict[str, dict[str, object]] = {}
    notice_fields: dict[tuple[str, str], dict[str, object]] = {}
    signal_fields: dict[str, Fact] = {}
    search_row: dict | None = None

    for r in rows:
        field, value, gid = r["field"], r["value"], r["grant_id"].strip()
        if field in ("original_publication_date", "copyright_secured"):
            work_fields[field] = _fact(r, PartialDate.parse(value))
        elif field.startswith("signals."):
            signal_fields[field.removeprefix("signals.")] = _fact(r, _bool(value))
        elif field == "search":
            search_row = r
        elif field.startswith("notice."):
            _, k, name = field.split(".", 2)
            notice_fields.setdefault((gid, k), {})[name] = (r, value)
        else:
            g = grant_fields.setdefault(gid, {})
            if field == "right_types":
                g[field] = tuple(RightType(v.strip()) for v in value.split(";") if v.strip())
            elif field == "grantee":
                g[field] = value
            elif field == "grantor":
                g[field] = _fact(r, GRANTORS[value.strip()])
            elif field in ("executed_on", "publication_under_grant"):
                g[field] = _fact(r, PartialDate.parse(value))
            elif field in ("conveys_publication", "work_made_for_hire"):
                g[field] = _fact(r, _bool(value))
            elif field == "executing_authors":
                g[field] = _fact(r, int(value))
            else:
                raise ValueError(f"{case_id}: unknown field {field!r}")

    work = Work(work_id=next(iter(work_ids)), original_publication_date=work_fields.get("original_publication_date"),
                copyright_secured=work_fields.get("copyright_secured"))
    grants = tuple(
        Grant(grant_id=gid, right_types=g.get("right_types", ()), grantor=g["grantor"], executed_on=g.get("executed_on"),
              conveys_publication=g.get("conveys_publication"), publication_under_grant=g.get("publication_under_grant"),
              executing_authors=g.get("executing_authors"), work_made_for_hire=g.get("work_made_for_hire"),
              grantee=g.get("grantee"))
        for gid, g in grant_fields.items()
    )
    notices = []
    for (gid, _k), fields in notice_fields.items():
        row, section = fields["section"]
        served_row, served = fields["served_on"]
        eff = fields.get("effective_on")
        parties = fields.get("terminating_parties")
        notices.append(TerminationNotice(
            grant_id=gid, section=SECTIONS[section.strip()], served_on=_fact(served_row, PartialDate.parse(served)),
            effective_on=None if eff is None else _fact(eff[0], PartialDate.parse(eff[1])),
            terminating_parties=tuple(p.strip() for p in parties[1].split(";")) if parties else (),
        ))
    search = None
    if search_row is not None:
        search = NoticeSearch(found=tuple(notices), parameters=search_row["value"],
                              searched_on=date.fromisoformat(search_row["capture_date"]), tier=int(search_row["tier"]),
                              evidence=(Evidence(source_id=search_row["source_id"], url=search_row["url"],
                                                 capture_date=date.fromisoformat(search_row["capture_date"]),
                                                 citation_span=search_row["citation_span"]),))
    elif notices:
        raise ValueError(f"{case_id}: notices without a 'search' row; a notice comes from a search (I7)")
    signals = OutOfPrintSignals(**signal_fields) if signal_fields else None
    return Case(case_id=case_id, work=work, grants=grants, notice_search=search, signals=signals)


def check_expectation(cases: dict[str, Case], row: dict) -> list[str]:
    """Run one expectation row. Returns a list of mismatches; empty means it passed."""
    case = cases[row["case_id"]]
    results = case.run(date.fromisoformat(row["as_of"]))
    gid = row["grant_id"].strip() or None
    section = SECTIONS[row["section"].strip()] if row.get("section", "").strip() else None
    matches = [r for r in results if r.channel.name == row["channel"].strip() and r.grant_id == gid
               and (section is None or r.section is section)]
    if len(matches) != 1:
        return [f"{row['case_id']}/{gid}: expected one result, found {len(matches)}"]
    r = matches[0]
    problems = []
    expected = row["expected"].strip()
    if expected.startswith("UNDETERMINED:"):
        if not isinstance(r, Undetermined) or r.reason.name != expected.split(":", 1)[1]:
            problems.append(f"expected {expected}, got {_describe(r)}")
    elif not isinstance(r, StatusResult) or r.status.name != expected:
        problems.append(f"expected {expected}, got {_describe(r)}")
    for col in ("window_start", "window_end", "last_serviceable_date"):
        want = row.get(col, "").strip()
        if want:
            got = getattr(r.window, col).display() if r.window else None
            if got != want:
                problems.append(f"{col}: expected {want}, got {got}")
    if row.get("tier", "").strip() and r.tier != int(row["tier"]):
        problems.append(f"tier: expected {row['tier']}, got {r.tier}")
    return [f"{row['case_id']}/{gid}: {p}" for p in problems]


def _describe(r: ChannelResult) -> str:
    return r.status.name if isinstance(r, StatusResult) else f"UNDETERMINED:{r.reason.name}"
