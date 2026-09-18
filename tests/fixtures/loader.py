"""Turn the fixture tables (tests/fixtures/SCHEMA.md) into engine inputs and regression checks.

Row parsing is pure; the only file I/O is ``load_csv``, and it lives here in the test layer, not
in channels/.

Rules applied to every row of every table (Manual Research Protocol §H):
- no span, no record: ``citation_span`` is required
- ``tier`` is 1-4, ``capture_date`` is an ISO date
- one row per fact: two rows for the same fact with the same value corroborate each other and
  are merged (strongest tier, union of evidence); two rows with different values are a
  contradiction. Note the direction: corroboration takes the STRONGEST tier (a weaker agreeing
  source does not dilute a stronger one); computation in channels/ takes the WEAKEST input used
  (Step 0 answer 2.5). Same word, opposite direction.
- termination_interest.<party>.fraction rows on one grant must sum to exactly 1: per-stirpes
  shares always do, so a sum that misses is an incomplete family, which would produce a confident
  majority over the wrong people. A contradicted fact never reaches the engine; it is recorded on the Case for
  the contradiction queue and can be asserted with ``expected = CONTRADICTION:<field>``.
"""

from __future__ import annotations

import csv
from fractions import Fraction
from dataclasses import dataclass, field as dc_field
from datetime import date
from pathlib import Path

from colophon.channels import (
    ChannelResult,
    Contribution,
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
    no_reprint_within_threshold,
)

SECTIONS = {"203": Section.SECTION_203, "304c": Section.SECTION_304C, "304d": Section.SECTION_304D}
GRANTORS = {"author": Grantor.AUTHOR, "statutory_successor": Grantor.STATUTORY_SUCCESSOR, "other": Grantor.OTHER}
CONTRIBUTIONS = {c.value: c for c in Contribution}

WORK_FIELDS = {"original_publication_date", "copyright_secured"}
GRANT_FIELDS = {"right_types", "grantor", "executed_on", "conveys_publication", "publication_under_grant",
                "executing_authors", "work_made_for_hire", "grantee", "contribution"}
SIGNAL_FIELDS = {"signals.no_edition_in_print", "signals.no_ebook_or_audio", "signals.no_reprint_within_threshold",
                 "signals.last_reprint"}
NOTICE_FIELDS = {"section", "served_on", "effective_on", "terminating_parties"}

# counterparty.csv and demand.csv (Protocol §F, §G): validated one-row-per-fact tables. They are
# not engine inputs; they feed inference/ and scoring/ later and are checked here so a malformed
# record is caught on book two, not book twenty. Public records only (CLAUDE.md §2).
COUNTERPARTY_FIELDS = {
    "author.living", "author.death_date", "illustrator.living", "illustrator.death_date",
    "probate.jurisdiction", "probate.executor",
    "termination_interest.clears_majority",  # true/false, computed by hand for now (Protocol §F)
    "agent.name", "agent.handles_dramatic_rights", "agent.route",
    "estate.name", "estate.handles_dramatic_rights", "estate.route",
    "publisher.permissions_desk",
    "counterparty.name", "counterparty.route",
    "search",
}
COUNTERPARTY_PREFIXES = ("heir.", "termination_interest.", "trademark.")  # heir.k.name/relation/branch; termination_interest.<party>.fraction; trademark.k.mark/registrant/status
DEMAND_FIELDS = {
    "derivative_exception_engaged", "in_print.from", "in_print.to", "character_led", "screen_case",
}
DEMAND_PREFIXES = ("adaptation.", "award.", "in_print.gap.", "canon_list.")  # adaptation.k.year/producer/status; award.k; in_print.gap.k; canon_list.k


@dataclass(frozen=True)
class Contradiction:
    case_id: str
    grant_id: str | None
    field: str
    values: tuple[str, ...]
    rows: tuple[dict, ...]


@dataclass(frozen=True)
class Case:
    case_id: str
    work: Work
    grants: tuple[Grant, ...]
    notice_search: NoticeSearch | None
    signals: OutOfPrintSignals | None
    contradictions: tuple[Contradiction, ...] = dc_field(default_factory=tuple)

    def run(self, as_of: date) -> tuple[ChannelResult, ...]:
        return compute(work=self.work, grants=self.grants, as_of=as_of, notice_search=self.notice_search,
                       contractual_signals=self.signals)


class LoadError(ValueError):
    pass


def _bool(v: str) -> bool:
    if v.strip().lower() in ("true", "yes", "1"):
        return True
    if v.strip().lower() in ("false", "no", "0"):
        return False
    raise LoadError(f"not a boolean: {v!r}")


def validate_row(row: dict, table: str) -> None:
    where = f"{table} {row.get('case_id', '?')}/{row.get('field', '?')}"
    if not row.get("citation_span", "").strip():
        raise LoadError(f"{where}: no span, no record (CLAUDE.md I2)")
    try:
        tier = int(row.get("tier", ""))
    except ValueError:
        raise LoadError(f"{where}: tier must be 1-4, got {row.get('tier')!r}") from None
    if not 1 <= tier <= 4:
        raise LoadError(f"{where}: tier must be 1-4, got {tier}")
    try:
        date.fromisoformat(row.get("capture_date", ""))
    except ValueError:
        raise LoadError(f"{where}: capture_date must be an ISO date, got {row.get('capture_date')!r}") from None
    if not row.get("source_id", "").strip():
        raise LoadError(f"{where}: source_id is required (CLAUDE.md I3)")


def _evidence(row: dict) -> Evidence:
    return Evidence(source_id=row["source_id"], url=row.get("url", ""), capture_date=date.fromisoformat(row["capture_date"]),
                    citation_span=row["citation_span"])


def _fact(rows: tuple[dict, ...], value) -> Fact:
    """Corroborating rows merge: the strongest (lowest-numbered) tier, every citation kept."""
    return Fact(value=value, tier=min(int(r["tier"]) for r in rows), evidence=tuple(_evidence(r) for r in rows))


def load_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_cases(rows: list[dict]) -> dict[str, Case]:
    by_case: dict[str, list[dict]] = {}
    for r in rows:
        validate_row(r, "cases.csv")
        by_case.setdefault(r["case_id"], []).append(r)
    return {cid: _build_case(cid, rs) for cid, rs in by_case.items()}


def _group_facts(case_id: str, rows: list[dict]) -> tuple[dict[tuple[str | None, str], tuple[dict, ...]], list[Contradiction]]:
    """Group rows by (grant_id, field). Same value -> corroboration; different -> contradiction."""
    grouped: dict[tuple[str | None, str], list[dict]] = {}
    for r in rows:
        grouped.setdefault((r["grant_id"].strip() or None, r["field"].strip()), []).append(r)
    facts: dict[tuple[str | None, str], tuple[dict, ...]] = {}
    contradictions: list[Contradiction] = []
    for key, rs in grouped.items():
        values = tuple(dict.fromkeys(r["value"].strip() for r in rs))
        if len(values) == 1:
            facts[key] = tuple(rs)
        else:
            contradictions.append(Contradiction(case_id=case_id, grant_id=key[0], field=key[1], values=values, rows=tuple(rs)))
    return facts, contradictions


def _build_case(case_id: str, rows: list[dict]) -> Case:
    work_ids = {r["work_id"] for r in rows}
    if len(work_ids) != 1:
        raise LoadError(f"{case_id}: one work per case, got {sorted(work_ids)}")
    facts, contradictions = _group_facts(case_id, rows)

    work_fields: dict[str, Fact] = {}
    grant_fields: dict[str, dict[str, object]] = {}
    notice_fields: dict[tuple[str, str], dict[str, tuple[tuple[dict, ...], str]]] = {}
    signal_fields: dict[str, object] = {}
    search_rows: tuple[dict, ...] | None = None

    for (gid, field), rs in facts.items():
        value = rs[0]["value"].strip()
        if field in WORK_FIELDS:
            if gid is not None:
                raise LoadError(f"{case_id}: {field} is work-level; leave grant_id blank")
            work_fields[field] = _fact(rs, PartialDate.parse(value))
        elif field in SIGNAL_FIELDS:
            name = field.removeprefix("signals.")
            if name == "last_reprint":
                signal_fields[name] = (rs, None if value.lower() == "never" else PartialDate.parse(value))
            else:
                signal_fields[name] = _fact(rs, _bool(value))
        elif field == "search":
            search_rows = rs
        elif field.startswith("notice."):
            _, k, name = field.split(".", 2)
            if name not in NOTICE_FIELDS or gid is None:
                raise LoadError(f"{case_id}: bad notice field {field!r} (needs grant_id and one of {sorted(NOTICE_FIELDS)})")
            notice_fields.setdefault((gid, k), {})[name] = (rs, value)
        elif field in GRANT_FIELDS:
            if gid is None:
                raise LoadError(f"{case_id}: {field} is grant-level; grant_id is required")
            g = grant_fields.setdefault(gid, {})
            if field == "right_types":
                g[field] = tuple(RightType(v.strip()) for v in value.split(";") if v.strip())
            elif field == "grantee":
                g[field] = value
            elif field == "contribution":
                g[field] = CONTRIBUTIONS[value.lower()]
            elif field == "grantor":
                g[field] = _fact(rs, GRANTORS[value.lower()])
            elif field in ("executed_on", "publication_under_grant"):
                g[field] = _fact(rs, PartialDate.parse(value))
            elif field in ("conveys_publication", "work_made_for_hire"):
                g[field] = _fact(rs, _bool(value))
            elif field == "executing_authors":
                g[field] = _fact(rs, int(value))
        else:
            raise LoadError(f"{case_id}: unknown field {field!r}")

    # A contradicted grant still exists as a grant; the contested field is absent from it.
    for c in contradictions:
        if c.grant_id is not None and c.field in GRANT_FIELDS:
            grant_fields.setdefault(c.grant_id, {})
        if c.field == "search" or c.field.startswith("notice."):
            raise LoadError(f"{case_id}: contradictory {c.field} rows; a search or notice needs one value per row set")

    contested_grantor = {c.grant_id for c in contradictions if c.field == "grantor"}
    for gid, g in grant_fields.items():
        if "grantor" not in g and gid not in contested_grantor:
            raise LoadError(f"{case_id}/{gid}: grantor is required (decides whether § 203 applies at all)")

    work = Work(work_id=next(iter(work_ids)), original_publication_date=work_fields.get("original_publication_date"),
                copyright_secured=work_fields.get("copyright_secured"))
    # A grant whose grantor is contested cannot be built at all: it is recorded on the Case and
    # produces no engine result until the contradiction is settled.
    grants = tuple(
        Grant(grant_id=gid, right_types=g.get("right_types", ()), grantor=g["grantor"],
              executed_on=g.get("executed_on"), conveys_publication=g.get("conveys_publication"),
              publication_under_grant=g.get("publication_under_grant"), executing_authors=g.get("executing_authors"),
              work_made_for_hire=g.get("work_made_for_hire"), grantee=g.get("grantee"), contribution=g.get("contribution"))
        for gid, g in grant_fields.items() if gid not in contested_grantor
    )

    notices = []
    for (gid, _k), fields in notice_fields.items():
        if "section" not in fields or "served_on" not in fields:
            raise LoadError(f"{case_id}/{gid}: a notice needs section and served_on")
        section = SECTIONS[fields["section"][1].lower()]
        served_rows, served = fields["served_on"]
        eff = fields.get("effective_on")
        parties = fields.get("terminating_parties")
        notices.append(TerminationNotice(
            grant_id=gid, section=section, served_on=_fact(served_rows, PartialDate.parse(served)),
            effective_on=None if eff is None else _fact(eff[0], PartialDate.parse(eff[1])),
            terminating_parties=tuple(p.strip() for p in parties[1].split(";")) if parties else (),
        ))
    search = None
    if search_rows is not None:
        r = search_rows[0]
        search = NoticeSearch(found=tuple(notices), parameters=r["value"], searched_on=date.fromisoformat(r["capture_date"]),
                              tier=min(int(x["tier"]) for x in search_rows), evidence=tuple(_evidence(x) for x in search_rows))
    elif notices:
        raise LoadError(f"{case_id}: notices without a 'search' row; a notice comes from a search (I7)")

    signals = _signals(case_id, signal_fields)
    return Case(case_id=case_id, work=work, grants=grants, notice_search=search, signals=signals,
                contradictions=tuple(contradictions))


def _signals(case_id: str, fields: dict[str, object]) -> OutOfPrintSignals | None:
    if not fields:
        return None
    reprint = fields.get("no_reprint_within_threshold")
    if reprint is None and "last_reprint" in fields:
        rows, last = fields["last_reprint"]
        # Fails loudly until docs/II states the threshold (Step 1 answer, check). The date row is
        # kept as the durable fact; the boolean is derived, never recorded.
        as_of = date.fromisoformat(rows[0]["capture_date"])
        reprint = Fact(value=no_reprint_within_threshold(last, as_of), tier=min(int(r["tier"]) for r in rows),
                       evidence=tuple(_evidence(r) for r in rows))
    missing = [n for n, v in (("no_edition_in_print", fields.get("no_edition_in_print")),
                              ("no_ebook_or_audio", fields.get("no_ebook_or_audio")),
                              ("no_reprint_within_threshold or last_reprint", reprint)) if v is None]
    if missing:
        raise LoadError(f"{case_id}: Channel A signals incomplete, missing {missing}")
    return OutOfPrintSignals(no_edition_in_print=fields["no_edition_in_print"], no_ebook_or_audio=fields["no_ebook_or_audio"],
                             no_reprint_within_threshold=reprint)


def validate_fact_table(rows: list[dict], table: str, fields: set[str], prefixes: tuple[str, ...]) -> list[Contradiction]:
    """counterparty.csv / demand.csv: shape checks plus contradiction detection. Returns the
    contradictions found; raises LoadError on a malformed row or an unknown field."""
    by_case: dict[str, list[dict]] = {}
    for r in rows:
        validate_row(r, table)
        f = r["field"].strip()
        if f not in fields and not f.startswith(prefixes):
            raise LoadError(f"{table} {r['case_id']}: unknown field {f!r}")
        by_case.setdefault(r["case_id"], []).append(r)
    out: list[Contradiction] = []
    for cid, rs in by_case.items():
        if table == "counterparty.csv":
            if not any(r["field"].strip() == "search" for r in rs):
                raise LoadError(f"{table} {cid}: a search row is required (public indexes consulted, even when empty)")
            _check_fraction_sums(table, cid, rs)
        out.extend(_group_facts(cid, rs)[1])
    return out


def _check_fraction_sums(table: str, case_id: str, rows: list[dict]) -> None:
    sums: dict[str | None, Fraction] = {}
    for r in rows:
        f = r["field"].strip()
        if f.startswith("termination_interest.") and f.endswith(".fraction"):
            try:
                share = Fraction(r["value"].strip())
            except (ValueError, ZeroDivisionError):
                raise LoadError(f"{table} {case_id}/{f}: fraction must be a number like 1/4 or 0.25, got {r['value']!r}") from None
            gid = r["grant_id"].strip() or None
            sums[gid] = sums.get(gid, Fraction(0)) + share
    for gid, total in sums.items():
        if total != 1:
            raise LoadError(f"{table} {case_id}/{gid or '-'}: termination-interest fractions sum to {total}, not 1; "
                            "the family is incomplete or a share is wrong")


def check_expectation(cases: dict[str, Case], row: dict) -> list[str]:
    """Run one expectation row. Returns a list of mismatches; empty means it passed."""
    case = cases[row["case_id"]]
    gid = row["grant_id"].strip() or None
    expected = row["expected"].strip()
    if expected.startswith("CONTRADICTION:"):
        field = expected.split(":", 1)[1]
        if any(c.grant_id == gid and c.field == field for c in case.contradictions):
            return []
        return [f"{row['case_id']}/{gid}: expected a contradiction on {field}, found none"]
    results = case.run(date.fromisoformat(row["as_of"]))
    section = SECTIONS[row["section"].strip().lower()] if row.get("section", "").strip() else None
    matches = [r for r in results if r.channel.name == row["channel"].strip() and r.grant_id == gid
               and (section is None or r.section is section)]
    if len(matches) != 1:
        return [f"{row['case_id']}/{gid}: expected one result, found {len(matches)}"]
    r = matches[0]
    problems = []
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
