<!-- Discovery deliverable VII. Source of truth: Colophon Discovery Pack (CO·DISC / 2026), converted from the .docx. Where docs/PRD.md disagrees with this file, this file wins. -->

# Ownership Inference Spec.

*How scattered public evidence becomes a scored, contestable claim about who holds the adaptation rights to a book — and what would confirm it.*

## 01 — The problem stated properly

*Nobody knows who holds film rights to most children’s books. Not the publisher’s website, not the author’s agent’s successor, sometimes not the author.*

The record is partial by design. Recordation of transfers is voluntary, options lapse silently, side letters are private, and estates fragment without notice. So the target is not certainty. It is a claim: a named holder, a right type, a territory, an as-of date, a confidence tier, the evidence behind it, and the single cheapest action that would raise or refute it.

## 02 — Evidence taxonomy

| **Evidence** | **What it establishes** | **Tier** |
|---|---|---|
| Recorded transfer | Named party held a specified right as of a date. Strongest public artifact available. | T1 |
| Recorded termination notice | Who is terminating what, effective when — and by implication who currently holds it. | T1 |
| Contract in hand | Everything, and the only thing that settles the question. Arrives from a counterparty, never from research. | T1 |
| Registration claimant ≠ author | A transfer occurred at registration; scope unknown, so it says nothing about dramatic rights specifically. | T2 |
| WFH flag on registration | Strong indication no termination right exists in that contribution. Filters before it scores. | T2 |
| Screen credit | Rights were exercised by a named producer at a known date; engages the derivative works exception. | T2 |
| Rights guide listing | The publisher publicly states which rights it controls and which are available. | T2 |
| Probate record | Identifies successors in interest for a deceased author or illustrator. | T2 |
| Deal announcement | An option or purchase was reported. Reliable on the event, unreliable on scope and duration. | T3 |
| Agency or estate listing | Who handles dramatic rights today — often the fastest route to the real counterparty. | T3 |
| Character trademark filing | Who believes they own the brand. A proxy, and a warning about what recapture will not carry. | T3 |
| Absence signals | No adaptation, no recorded grant, long out of print, no deal trace. Weak alone, decisive in combination. | T4 |

## 03 — Combination rules

```
R1  recorded transfer + no later transfer or termination
      → held_by = recorded party  T1
R2  deal announcement + screen credit within 6y
      → held_by = producer, adaptation exists  T2
R3  deal announcement + no credit + ≥5y elapsed + no renewal
      → REVERTED·LIKELY, holder = author or estate  T3
R4  no recorded grant + no adaptation + no deal trace
    + author living or estate identified
      → NEVER·GRANTED·LIKELY  T4  ← cheapest deals in the corpus
R5  any two rules conflict → contradiction queue, no status emitted
```

The null result is the product’s best output. Rule R4 describes a book nobody ever optioned, whose author or estate still holds everything, and which requires no statute, no window, and no incumbent negotiation. It is also the hardest finding to trust, which is why it carries the lowest tier and the most explicit confirmation path.

## 04 — Claim record

```
claim {
  work_id · right_type · territory · as_of
  asserted_holder     party_id | "author or estate" | unknown
  tier                1 – 4
  rule_fired          R1 … R5 · rule_version
  evidence[]          source · url · capture_date · span
  contradicts[]       competing claim ids
  confirming_action   the one next step that would settle it
  confidence_decay    tier degrades as as_of ages
}
```

Two fields do unusual work. confirming_action turns every uncertain record into a task rather than a shrug. confidence_decay encodes that a 2009 deal announcement is weaker evidence in 2026 than it was in 2011 — rights move, and a claim that never ages will eventually lie.

## 05 — Extraction pipeline

**01 · Candidate retrieval**  For each work, gather the source documents plausibly about it — announcements, registration notes, rights-guide entries, probate text — using title, author, and character-name matching.

**02 · Structured extraction**  Batch model pass returning typed events: party, right type, action, date, territory, plus a verbatim citation span. No span, no record — an extraction that cannot point at its sentence is discarded.

**03 · Entity linkage**  Resolve named parties to canonical organizations and persons across imprint changes, studio renames, agency mergers, and estate successions.

**04 · Rule evaluation**  Deterministic combination rules produce claims. The model never emits a claim directly; it only supplies the evidence rules operate on.

**05 · Review queue**  Contradictions, high-value targets, and every proposed promotion to tier 1 go to a human. Review decisions are stored as evidence in their own right.

## 06 — Confirmation ladder

| **From → to** | **Action** | **Cost and latency** |
|---|---|---|
| T4 → T3 | Targeted records search on the specific work and party. | Hours; free. |
| T3 → T2 | Agent, estate, or publisher permissions desk confirms who controls dramatic rights. | Days; a phone call and a plain question. |
| T2 → T1 | Certified Copyright Office search, or the counterparty produces the agreement or a chain-of-title letter. | Weeks; fees. Reserved for targets already in conversation. |

*The ladder is deliberately steep at the top. Tier 1 costs real money and time, so it is spent only on books somebody has already agreed to talk about — which makes the tiering an operating budget, not just a data-quality label.*

### What this deliverable is for

Anyone can compute a statutory date. The defensible asset is knowing, for ten thousand books, who to call and why.
