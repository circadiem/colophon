# Colophon

**Brand identity — CO·DISC deliverable VIII.**

Deliverables I–VII specify what Colophon computes. This one specifies how it presents itself: to the operator working the queue, to a producer reading an evidence packet, and to an author who has never heard of it and is opening a letter.

---

## 01 · The name

A colophon is the statement of making at the back of a book — who printed it, where, when, in what type, on what press. It is the one part of a book that is only about its own provenance, and it is often the only part that survives an otherwise broken chain of custody.

The company reads that statement forward. The imprint page says who made the book. Colophon works out who holds it now.

The name does three things an invented name would not:

- **It is an artifact of record, not a claim of ownership.** The standing rule in VI — leads, dates and evidence, never an opinion about someone's rights — is already inside the word.
- **It is legible to the room that matters first.** Rights directors, subrights agents and estates know the word. Film-side buyers may not, which is a cost worth paying: the publishing-side counterparties are the ones who have to trust this before anyone else does.
- **It outlasts the corpus boundary.** Nothing in it says *children's*, *picture book*, or *§ 203*. The name survives corpus expansion, the intel product, and any widening past US trade.

**Setting.** *Colophon* — one word, roman, initial cap. Never all-caps in running text, never abbreviated, no article: "Colophon computes," not "the Colophon." In display it takes letterspaced caps at `section-label` tracking or wider.

**Open:** trademark clearance has not been run. The word is in live use by small presses and at least one design practice, so the mark is likely weak standing alone and will need a distinguishing element. See the Architecture section.

## 02 · Positioning

> **The record of who holds the book.**

For the operator working the pipeline, Colophon is a provenance engine for children's-book adaptation rights that turns the scattered public record into ranked, evidence-backed leads. Unlike precedent-and-rolodex research, it computes across the whole population rather than the one book you already thought of.

What it promises: a name to call, a date, and the evidence behind both.
What it never promises: clear title.

## 03 · The constraint that shapes everything

From VI: *Colophon discovers that an author can get their rights back, and Colophon may want to buy those rights.*

That is a brand problem before it is a legal one. The same system, described two degrees differently, is either a registry or a fund circling elderly estates. Language and layout carry as much of that distinction as the disclosure language does.

Three consequences, binding on every surface:

**i. Registerial, not promotional.** The reference objects are the accession stamp, the catalogue card, the imprint page and the certified search — not the dashboard and not the pitch deck. Urgency is never expressed as urgency. The recapture clock is real and is displayed as a date, never as a countdown, a pulse, or a badge reading *closing soon*.

**ii. Evidence is the hero, not the answer.** II is explicit: a status without evidence is not a status, it is a guess, and the interface must show the difference. Tier and as-of date travel with every claim at every size, exports included. A claim rendered without its tier is a bug, not a density choice.

**iii. Nothing addresses a rightsholder in the second person about their own rights.** No screen, letter or export says *you could get these back*. The system states what the record shows and names the confirming action. Advice comes from the reader's own counsel, and the letter says so before it says anything else.

## 04 · Voice, in brief

1. **State the record, not the conclusion.** "Recorded transfer to Harper & Row, 1989-04" — not "Harper owns it."
2. **Dates beat adjectives.** Every assertion carries an as-of. The `confidence_decay` field in VII is a brand principle as much as a schema field: a claim that never ages will eventually lie.
3. **Uncertainty is a number, not a hedge.** Tier 3, not "possibly." Hedging words are banned precisely because the tier already does that work.
4. **Name the next step.** VII's `confirming_action` turns every uncertain record into a task rather than a shrug. Every uncertain statement in the interface ends in one.

Full lexicon and worked rewrites follow in the Lexicon and Voice sections.

## 05 · Visual foundations

### Color

Paper and ink, with one stamp. A warm uncoated ground (`surface-page`), a warm near-black (`ink`), and a single oxidized vermilion (`stamp`) that behaves like a date stamp rather than a brand colour — sparse, and always meaning something.

**The rule: colour carries meaning, never mood.** No hue in this system has a decorative use. Five status tokens cover the eight statuses in II:

| Status (II) | Token |
| --- | --- |
| `TERMINABLE·NOW`, `REVERTED·LIKELY`, `NEVER·GRANTED` | `status-open` |
| `TERMINABLE·FUTURE` | `status-scheduled` |
| `PUBLIC·DOMAIN` | `status-clear` |
| `EXCLUDED·WFH`, `LAPSED·WINDOW` | `status-closed` |
| `GRANTED·ACTIVE` | `status-held` |

Three actionable statuses share one token deliberately. The operator's question is *do I act on this*; the distinction between the three is carried by the word, not the hue.

### Type

Three families, each with a job.

- **Spectral** (`serif`) — the deliverable voice. Display, prose, and the letterspaced section rules that run through the CO·DISC pack.
- **IBM Plex Sans** (`sans`) — the interface. Tables, labels, controls. Never prose.
- **IBM Plex Mono** (`mono`) — the record. Statuses, statutory blocks, dates, identifiers, tier badges, citation spans. Anything the system *computed* rather than *wrote*.

That third assignment is load-bearing. Mono is not a stylistic gesture here; it is the visible boundary between what Colophon asserts and what Colophon quotes. A computed date set in Spectral is a formatting error.

### The interpunct

`·` is the house separator, already at work across the pack: `CO·DISC`, `TERMINABLE·NOW`.

- Status enums: caps, mono, interpunct, no spaces — `EXCLUDED·WFH`.
- Document marks: spaced — `COLOPHON · VIII · BRAND IDENTITY`.
- Never in prose, never as decoration, never in place of a bullet.

### Rules and edges

Hairlines, not shadows. Squares, not cards. `radius-none` is the default and `radius-sm` is the only exception, on inputs and the status chip. Elevation is not part of this system — separation is a `rule` hairline or a `surface-sunken` field. Nothing in the operator surface floats, and nothing in it is round.

### Iconography

There is none, and that is the decision rather than an omission. Status is a word, tier is a count of filled squares, evidence is a source name. An icon set would compress exactly the distinctions the product exists to keep visible. If one later becomes necessary it is hairline, square-terminal, at `rule-strong` weight, and it never replaces a status word.

### The device

One drawn element, and the only one. The device is a colophon as it sets on a page — a centred block of type at the end of a book, lines tapering to a point — knocked out of a solid vermilion square. A printer's device in the literal sense: ink pressed into paper. It is the single place `stamp` takes a solid fill, and it holds at 16px, which is why it was drawn square and reversed rather than outlined.

A second form, the ornament, sets the same block between two rules in `ink` for use inside a document, where a solid vermilion block is too loud. It never appears beside the wordmark.

Both ship as single-path SVGs in the Device asset group. Full rules, ink table and clear space are in that group's notes.

## 06 · Usage rules

- Prose sets in `serif` / `body` on `surface-page` in `ink`. Prose never sets in `sans`.
- Any computed value — a date, a status, a tier, a work id, a citation span — sets in `mono`.
- `stamp` is reserved for three things: the mark, the active status, and one primary action per screen. It is never a background field larger than `space-6`, and never a hover state.
- Every claim rendered anywhere shows its tier and its as-of. `TierBadge` and the date are not optional affordances.
- Exports carry the research label from VI verbatim, in `caption`, above the fold — never in a footer.
- Never a progress bar, a countdown, a percentage of "opportunity," or a trend arrow on a rights position.
