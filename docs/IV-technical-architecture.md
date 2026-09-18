<!-- Discovery deliverable IV. Source of truth: Colophon Discovery Pack (CO·DISC / 2026), converted from the .docx. Where docs/PRD.md disagrees with this file, this file wins. -->

# Technical Architecture.

*A provenance-first pipeline: immutable source snapshots, a canonical work layer, a rights graph, and an inference pass that can be re-run without losing the record of what was believed and why.*

## 01 — Shape of the system

**01 · Harvest → raw store**  One harvester per source writing immutable, source-dated snapshots to object storage. Nothing is parsed in place and nothing is overwritten, so every downstream claim can be replayed against the bytes it came from.

**02 · Normalize → entity store**  Postgres. Source records become typed rows: registrations, recordations, editions, screen titles, announcements, persons, organizations. Original identifiers are preserved alongside internal ones.

**03 · Resolve → canonical works**  Cluster editions to one work via ISBN and LCCN joins, then fuzzy title-author matching with an illustrator tiebreak. This layer’s job is a single trustworthy original publication date, because every clock in II hangs off it.

**04 · Assert → rights graph**  Edges, not columns: grant, assignment, option, termination notice, reversion, adaptation. Each edge carries parties, dates, right type, territory, tier, and its evidence set. History is additive; superseded edges are retained.

**05 · Infer → claims and status**  Deterministic channel rules from II run over the graph; language-model extraction feeds the graph but never writes status directly. Claim construction is specified in VII.

**06 · Serve → operator surface**  A queue, a work view with the evidence chain visible, a window calendar, and an outreach record. Single tenant, no public endpoints in v1.

## 02 — Stack

| **Layer** | **Recommendation** | **Rationale** |
|---|---|---|
| Ingest | Python + scheduled jobs | Sources are bulk files and periodic APIs. Nothing here needs streaming or a queue broker. |
| Raw store | object storage, versioned | Cheap, immutable, and the audit trail regulators and business-affairs teams expect. |
| Database | Postgres + pgvector | Relational for the graph, vectors for title and name matching. One system until it genuinely breaks. |
| Extraction | batch LLM, structured output | Announcements, registration notes, probate text, rights guides. Every extraction returns a citation span or it is discarded. |
| Rules | plain code, versioned | Date math must be deterministic, testable, and explainable line by line. No model touches a statutory computation. |
| Surface | PWA front end | Matches existing tooling, works on a phone at a book fair, no app-store dependency. |

## 03 — The provenance contract

Every asserted fact carries its origin. This is the difference between a lead worth acting on and a plausible sentence.

```
assertion {
  subject     work_id · right_type · territory
  predicate   held_by | terminable_on | reverted | adapted_by
  object      party_id | date | enum
  tier        1 document-verified … 4 estimated
  evidence[]  source_id · url · capture_date · citation_span
  rule_version which logic build produced it
  asserted_at · superseded_by
}
```

Because rule_version is stored, a corrected rule does not quietly rewrite history — it produces new assertions that supersede the old ones, and the diff is reviewable. That diff is also the product’s own quality signal over time.

## 04 — Cost model

Cost is driven by documents processed, not by users active. A single operator working a 5,000-title corpus and a fifty-seat subscription over the same corpus cost nearly the same to run, which is what makes the intel product attractive later.

**i · Corpus passes**  Batch processing for all latency-insensitive work. Interactive extraction is reserved for the single record an operator is actively looking at.

**ii · Reprocessing**  The real budget variable. Extraction logic will change several times in the first quarter and each change implies a full re-run. Budget three to five complete passes over the corpus, not one.

**iii · Paid sources**  Seat-priced subscriptions and licensed feeds, introduced only when a specific tier promotion depends on them.

**iv · Storage**  Immaterial. Raw snapshots of bibliographic and registration data are small; keeping everything forever is cheaper than deciding what to delete.

## 05 — What not to build

- No notice generator. Document assembly for a statutory filing is the line that separates a research tool from unauthorized practice. See VI.

- No auto-crawler for gated trade sources. Licensed feeds or manual capture, with the terms recorded next to the source.

- No model-written status. Extraction proposes; deterministic rules dispose. A status an operator cannot trace to a statute and a date is unusable in a negotiation.

- No multi-tenant layer in v1. Adding it later costs a week; carrying it early distorts every schema decision.
