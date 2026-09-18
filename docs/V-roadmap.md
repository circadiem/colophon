<!-- Discovery deliverable V. Source of truth: Colophon Discovery Pack (CO·DISC / 2026), converted from the .docx. Where docs/PRD.md disagrees with this file, this file wins. -->

# Prioritized Feature Roadmap.

*Build order, milestones, and the sequence that gets to a usable target list before anything is polished.*

## 01 — Sequencing principle

*Every phase has to end with a list you could act on that week. A half-built pipeline that produces twenty real names beats a complete one that produces none.*

The order below front-loads the two things that cannot be bought — the resolved corpus and the hand-scored seed set — and defers everything that can be added later without redesign, including the entire subscriber surface.

## 02 — Phase 0 · Discovery · Weeks 1–4

**01 · Corpus boundary and seed list**  Fix the publication band and formats. Assemble roughly 5,000 candidate titles from award lists, library canon lists, and the 1968–1992 grant band.

**02 · Hand-scored calibration set**  250 titles scored manually for adaptability. This is the asset no dataset contains and the thing everything downstream is measured against.

**03 · Channel rules fixed**  Date math, presumption thresholds, and tier definitions locked and unit-tested against known cases.

**04 · Manual end-to-end on twenty books**  Run the whole process by hand before automating any of it. Twenty books, fully researched, is the specification the software is written against.

### Milestone

Twenty books researched by hand, each with a status, an evidence set, and a named counterparty — plus the list of every step that was tedious, which becomes the build backlog.

## 03 — Month 01 · Foundation

- Harvesters for bulk registration, recordation, and renewal data; bibliographic ingest; immutable raw store.

- Canonical work resolution with a verified original publication date and a resolution-confidence score.

- Deterministic channel engine returning status, dates, and the operative last_serviceable_date for every work.

- Work-made-for-hire and public-domain filters applied first, so the corpus that reaches scoring is already clean.

- Flat status board over the full corpus — no ranking yet, just truth about dates.

### Milestone

Status computed for 5,000 works on real data, with a 100-title manual audit at or above ninety percent precision.

## 04 — Month 02 · Inference & ranking

- Ownership inference per VII: evidence taxonomy, combination rules, tiered claims, contradiction handling.

- Batch extraction over announcements, rights guides, and registration notes with citation spans retained.

- Evidence viewer — every claim on screen traceable to its source in one click, because this is what makes the tool usable in a conversation with a lawyer.

- Adaptability scoring calibrated against the seed set; ranked queue replaces the flat board.

- Window calendar with alerts keyed to notice deadlines, option anniversaries, and public-domain entry.

### Milestone

A ranked list of fifty qualified targets, each with a rights claim at tier 3 or better and a reachable counterparty.

## 05 — Month 03 · Operationalize

- Outreach pipeline: contact records for authors, illustrators, heirs, agents and estates, with stage tracking and a conversation log.

- Evidence packet export — a single clean document per target for counsel or a producer.

- Public-domain sweep as a standing feed, including the annual January cohort and unrenewed pre-1964 titles.

- Contradiction queue and tier-promotion workflow for human review.

- Compliance surfaces from VI: disclosure language, the counsel wall, source-terms register.

### Milestone

Production-ready v1: the system runs the pipeline end to end and at least one live conversation is under way on a property it surfaced.

## 06 — After v1

**i · Corpus expansion**  Widen the publication band, add middle-grade backlist at depth, and begin non-US-origin works once the territory question settles.

**ii · Consumer surface**  The read-then-watch mapping runs on the same adaptation graph this system already maintains. One dataset, two products — and the consumer side generates demand signal the rights side cannot buy.

**iii · Intel subscription**  Availability alerts for producers, agents, and publishers. Cheap to serve because cost scales with documents, not seats — but it arms competitors, so it follows the first acquisitions rather than preceding them.

**iv · Author-side service**  Reversion discovery for authors and estates, behind a genuine separation from any acquiring entity. Highest trust value, highest conflict risk; gated on VI.

### The ordering rule

Nothing that serves a future customer gets built before something that finds a real book this month.
