# Colophon

Colophon finds children's books whose film and television adaptation rights are available — or
about to be — and routes them toward film and television. It is an inference engine over public
proxies. It produces **evidence-backed leads with confidence tiers**. It never asserts clear title
and never advises a rightsholder.

The specification lives in `/docs`. It is not background reading: it is the contract. Read the
relevant deliverable before writing code in the corresponding area, and cite it in the PR.

| Area of code | Governing doc |
| --- | --- |
| Scope, MVP boundary, success criteria | `docs/I-product-requirements.md` |
| Status model, channel rules, all date math | `docs/II-rights-availability-logic.md` |
| Harvesters, source terms, what each source proves | `docs/III-data-sources.md` |
| Pipeline shape, storage, provenance contract | `docs/IV-technical-architecture.md` |
| Build order and milestones | `docs/V-roadmap.md` |
| Compliance constraints that are code, not policy | `docs/VI-risk-and-compliance.md` |
| Evidence taxonomy, combination rules, claim record | `docs/VII-ownership-inference.md` |

---

## 1. Invariants

These are numbered so they can be cited by number in review. A change to any of them is a
specification change and needs a doc edit first, in the same PR.

**I1 — Extraction proposes, deterministic rules dispose.**
A language model may read a document and emit typed evidence. A model may never emit a status, a
claim, a tier, or a date used in a statutory computation. If a model output reaches
`claims` or `status` without passing through a versioned rule in `rules/`, that is a bug of the
highest severity in this codebase.

**I2 — No span, no record.**
Every extracted fact carries a verbatim citation span from its source document. An extraction that
cannot point at its own sentence is discarded, not stored with a null. This is enforced at the
schema level (`NOT NULL`), not in review.

**I3 — Every asserted fact carries its origin.**
`source_id`, `url`, `capture_date`, `citation_span`, `tier`, `rule_version`, `asserted_at`. A fact
without provenance does not enter the graph. See the assertion record in
`docs/IV-technical-architecture.md` §03.

**I4 — History is additive.**
Nothing is overwritten. Raw snapshots are immutable. Superseded graph edges and assertions are
retained and marked `superseded_by`. Corrected rules produce *new* assertions at a new
`rule_version`; they do not rewrite old ones. The diff between rule versions is a product output,
not an implementation detail. No `UPDATE` on `assertions`, `claims`, or graph edges — ever.

**I5 — A status without evidence is not a status.**
Status is always returned with its confidence tier and its evidence set attached. Any API, view, or
export that can return a status without them is wrong. The interface must show the difference
between a claim and a guess.

**I6 — Rules are pure, versioned, and exhaustively tested.**
All statutory date math lives in `rules/`, is pure (no I/O, no network, no model, no clock reads
except an injected `as_of`), and is covered by fixtures. Every rule module exports its
`RULE_VERSION`, and that version is stamped on every assertion it produces.

**I7 — Absence is a finding, not a null.**
"Searched the recordation index for this work and party, found nothing" is evidence and is stored
as such, with the search parameters and date. This matters most for recorded termination notices,
where recordation is mandatory and absence is therefore meaningful.

**I8 — Nothing leaves the system asserting clear title.**
Exports are evidence packets carrying tiers, dates, and a research label. They are wrong sometimes
by design, which is survivable only if the labelling is honest.

---

## 2. Prohibitions

Each of these is something a competent coding agent will otherwise build because it seems helpful.
Do not build them. If a task appears to require one, stop and raise it.

- **No notice generator.** Colophon computes dates and shows evidence. It does not draft, assemble,
  serve, or record termination notices, and it does not produce documents intended for filing.
  Document assembly for a statutory filing is the line between a research tool and unauthorized
  practice of law. No templating of §203 or §304 notices, not even as a "preview."
- **No personalized recommendation.** The system never tells an author whether to terminate, never
  scores a rightsholder's odds, and never produces prose advising a named person about their own
  rights. Generalized calculation over public records is fine; applying law to a particular
  person's circumstances is not.
- **No auto-crawler for gated trade sources.** Licensed feeds or manual capture only, with terms
  recorded next to the source. No scraper against a source whose terms prohibit bulk access, no
  matter how easy it would be.
- **No harvester without its terms registered first.** A source row in `sources` — including its
  licence terms, non-commercial restrictions, attribution requirements, per-seat limits, and
  anti-scraping clauses — is a precondition for writing its harvester, enforced by a test.
- **No purchased personal data.** Heir and estate research uses public records only: probate
  filings, obituaries, agency listings. No contact aggregation, no household or relative graphs, no
  data brokers.
- **No feature implying a termination right can be optioned, bought, waived, or pre-assigned in
  advance of its effective date.** Termination rights are inalienable. Before the effective date,
  the pipeline models *relationship* stages, not contract stages.
- **No model-written status.** Restating I1 because it is the one most likely to be violated under
  time pressure.

---

## 3. Vocabulary that must not drift

Renaming any of these is a breaking change.

- **work** — the canonical intellectual work, one per cluster of editions. Carries exactly one
  verified `original_publication_date`. Every clock hangs off it.
- **edition** — a physical or digital manifestation. Board-book reissues, anniversary editions, and
  format variants are editions, never works.
- **grant** — a transfer of rights from author to another party. One book can carry several.
- **right_type** — what was granted. Dramatic/motion-picture rights are distinct from publishing
  rights and have separate clocks.
- **territory** — modelled as a **flagged variable, never a settled value**, pending the Supreme
  Court petition on worldwide recapture reach. Never price or score on an assumed territory.
- **claim** — a scored, contestable assertion about who holds a right. Fields in
  `docs/VII-ownership-inference.md` §04.
- **assertion** — the provenance-bearing unit in the graph. Fields in
  `docs/IV-technical-architecture.md` §03.
- **tier** — 1 (document-verified) … 4 (estimated). Tier is an operating budget as well as a
  data-quality label: tier-1 confirmation costs real money and is spent only on targets already in
  conversation.
- **channel** — A (contractual reversion), B (option lapse), C (statutory termination). All three
  are computed for every work. A single-channel product discards good books wrongly; see the worked
  example in `docs/II-rights-availability-logic.md` §05.

### The unit of computation

The triple **`(work, right_type, territory)`**. Not the book. One book routinely resolves to
several triples with different statuses — a picture book whose text is terminable and whose art is
work made for hire is the normal case, not the edge case.

### Status enum — exactly these eight, no additions

Display forms in the docs use an interpunct; code uses underscores. Keep both in one place and
never let a ninth value in without a doc change.

```
EXCLUDED_WFH        work made for hire — no termination right exists, ever
PUBLIC_DOMAIN       term expired or renewal not made — no acquisition needed
NEVER_GRANTED       no evidence the right ever left the author
REVERTED_LIKELY     out-of-print or lapsed-option signals
TERMINABLE_NOW      window open, notice can still be served in time
TERMINABLE_FUTURE   window computed, notice service opens on a date
LAPSED_WINDOW       window passed or notice deadline missed — permanently closed
GRANTED_ACTIVE      held and exploited — monitor only
```

### Combination rules — exactly these five

`R1`…`R5` as specified in `docs/VII-ownership-inference.md` §03. `R5` (any two rules conflict →
contradiction queue, **no status emitted**) is not optional and is not a warning. Conflicting
evidence produces no status.

---

## 4. Date math

The most consequential and most silently-wrong part of the system.

- `last_serviceable_date = window_end − 2y` is the **primary date surfaced to the operator**. The
  end of the window is context. Notice must precede the effective date by at least two years and be
  recorded before it, so the end of the window is never the real deadline.
- §203 window start uses the dual clock where the grant conveys the right of publication:
  `min(publication_date + 35y, execution_date + 40y)`. Most book publishing agreements do, so the
  dual clock governs the majority of the corpus — but *whether it conveys publication* is a fact
  with its own evidence and tier, not a default.
- §304(d) is only available where the §304(c) window expired before 1998-10-27 and was not
  exercised. Encode the condition; do not assume availability.
- Grants executed by **heirs** rather than by the author are outside §203 entirely. This is a hard
  exclusion, not a penalty.
- Precision: publication and execution dates are frequently month-precision or year-only. Carry
  precision explicitly (`date_value` + `date_precision`) rather than coercing to a day and losing
  the fact that it was a guess. Year-only inputs produce ranged outputs, not false certainty.
- No naive timedelta arithmetic on years. Use explicit calendar-year addition with documented
  behaviour at month boundaries, and test it.

Every worked example in `docs/II-rights-availability-logic.md` §05 must exist as a fixture and pass
before any channel-engine change merges.

---

## 5. Open questions — stop, do not guess

These are specification gaps, currently unresolved. If a task requires one, **stop and ask rather
than choosing a default**. A silent default here corrupts the corpus and is very hard to detect
afterwards.

1. **Execution-date presumption.** §203 requires an execution date. Recordation is voluntary, so
   for most of the corpus there is none. There is currently no stated rule for computing a window
   from publication date alone. Needed: the presumed interval, the resulting tier, and the flag that
   marks the output as estimated.
2. **Adaptability rubric.** The ranked queue depends on adaptability scoring calibrated against a
   250-title hand-scored seed set. The scoring dimensions have not been specified anywhere.
3. **`confidence_decay`.** Named in the claim record, never defined. Needed: the curve or half-life,
   and whether it degrades tier or only a continuous score.
4. **Territory enumeration.** Values and flag semantics undefined.
5. **Entity-resolution thresholds.** Fuzzy title-author matching with illustrator tiebreak is
   specified in prose only — no thresholds, no blocking strategy. Also needed: a seeded
   imprint-lineage table for children's publishing M&A, which is hand-curatable once and otherwise
   guessed forever.
6. **Work-vs-edition clustering for reissues.** Open Library clustering needs correction for
   board-book reissues; the correction rule is not written.

---

## 6. Business structure — affects the code

Positioning is **intel-first**: the primary entity sells rights-availability intelligence. Rights
acquisition sits in a **separate fund entity** whose sole purpose is purchasing rights.

Consequences that land in the codebase:

- The wall between the two is architectural, not a policy page. Any surface that lets a subscriber's
  activity inform the fund's targeting, or the reverse, needs to be designed deliberately or not
  built.
- Independent counsel is structural. Any rightsholder contact carries written notice, at first
  contact, to take their own legal advice. This belongs in the outreach templates and cannot be
  disabled per-target.
- Evidence packet quality is now a customer-facing surface, not an internal convenience. Tier
  labelling, source attribution, and the research disclaimer are product, not polish.

**Flagged tension, unresolved.** `docs/IV` says no multi-tenant layer in v1 and `docs/V` places the
intel subscription *after* the first acquisitions, on the grounds that it arms competitors. An
intel-first posture pulls against both. The likely reconciliation is that v1 remains a
single-operator tool and "intel-first" describes the entity and the eventual product rather than
the build order — but that should be stated explicitly in `docs/V` rather than inferred here. Do
not add multi-tenancy on the strength of this section alone.

---

## 7. Shape of the system

```
harvest → raw store        immutable, source-dated snapshots; nothing parsed in place
normalize → entity store   Postgres; typed rows; original identifiers preserved
resolve → canonical works  ISBN/LCCN joins, then fuzzy match; one trustworthy pub date
assert → rights graph      edges not columns; additive; evidence set per edge
infer → claims and status  deterministic rules over the graph
serve → operator surface   queue, work view, window calendar, outreach record
```

Stack, as specified: Python with scheduled jobs for ingest; versioned object storage for raw;
Postgres with pgvector; batch LLM with structured output for extraction; plain versioned code for
rules; PWA front end. One database until it genuinely breaks. No streaming, no queue broker,
no multi-tenant layer in v1.

Graph edge types: `grant`, `assignment`, `option`, `termination_notice`, `reversion`, `adaptation`.

---

## 8. Cost posture

Cost scales with **documents processed**, not users active.

- Batch everything latency-insensitive. Interactive extraction is reserved for the single record an
  operator is actively looking at.
- **Budget three to five complete reprocessing passes over the corpus in the first quarter**, not
  one. Extraction logic will change several times. Design for re-runs: idempotent harvesters,
  replayable extraction, additive assertions.
- Paid sources are introduced only when a specific tier promotion depends on them, never
  speculatively.
- Storage is immaterial. Keep everything forever; that is cheaper than deciding what to delete.

---

## 9. Definition of done

A change merges when:

- [ ] Fixtures pass, including every worked example from `docs/II` §05
- [ ] Any new or changed rule exports a bumped `RULE_VERSION` and is stamped on its assertions
- [ ] No new path lets a model output reach a status, tier, claim, or statutory date (I1)
- [ ] Every new stored fact carries source, url, capture_date, citation_span (I2, I3)
- [ ] No `UPDATE` or `DELETE` added against `assertions`, `claims`, or graph edges (I4)
- [ ] Any new source has a `sources` row with its licence terms, written before the harvester
- [ ] Any new status, rule, or vocabulary term has a corresponding edit in `/docs` in the same PR
- [ ] Negative search results are stored, not dropped (I7)

---

## 10. Working style

- Ask before inventing a rule that belongs in `/docs`. A wrong guess here is expensive and quiet.
- Prefer precision over recall throughout. A false positive costs an outreach cycle; a false
  negative costs one lead out of thousands.
- When a step is tedious to do by hand, say so — the manual research pass is generating the build
  backlog, and friction is signal.
- Small, reviewable changes. The rules layer especially should be readable line by line by someone
  holding the statute.
