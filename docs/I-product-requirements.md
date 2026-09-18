<!-- Discovery deliverable I. Source of truth: Colophon Discovery Pack (CO·DISC / 2026), converted from the .docx. Where docs/PRD.md disagrees with this file, this file wins. -->

# Product Requirements Brief.

*What Colophon is, who it serves, and what has to be true before the first version counts as working.*

## 01 — The problem

*There is no registry of who holds the film and television rights to a children’s book. The people who need to know ask around until somebody remembers.*

Copyright ownership is partially public. Adaptation rights are not. A publishing agreement may or may not include dramatic rights; an option may have lapsed a decade ago with no record of it; an author may have died and left a chain of title across four grandchildren. The result is that a producer who wants a specific book spends weeks on provenance, and — more consequentially — never learns about the thousand books that are quietly available because nobody thought to ask.

Two statutory cohorts are arriving at once. Grants executed from 1978 through the early 1990s are entering their § 203 windows now. Works whose copyright was secured between 1968 and 1977 are entering their § 304(c) windows across this decade. Between them they cover most of the modern picture-book canon. The recapture clock is not the whole opportunity, but it is the part that can be calendared years in advance.

## 02 — Users & jobs

**01 · The operator — primary**  Works the pipeline directly. Needs a ranked queue of books worth pursuing, the evidence behind each rights position, and a record of who has been contacted and what they said. Every screen answers one question: what do I do next with this book.

**02 · Producers, studios, and agents — secondary**  Buy the intelligence rather than the property. Need availability alerts by theme, age band, or author, and a defensible provenance trail they can hand to business affairs.

**03 · Authors, illustrators, and estates — separated**  Benefit from knowing a window is open, but cannot be advised by a party that may want to buy from them. Anything facing this group runs through independent counsel and behind the wall described in VI.

## 03 — Core workflows

**i · Assemble & resolve**  Ingest bibliographic, registration, and recordation records; cluster editions, reissues, and board-book variants into one canonical work with one original publication date.

**ii · Infer rights position**  Combine recorded transfers, registration claimants, deal announcements, and screen credits into a scored claim about who holds what. Specified in VII.

**iii · Compute availability**  Run all three reversion channels against the work and return a status with dates: available now, terminable on a date, likely reverted, granted and active, or permanently excluded.

**iv · Score adaptability**  Rank surviving candidates on screen potential and demand evidence, calibrated against a hand-scored seed set.

**v · Watch the calendar**  Track notice-service deadlines, window openings and closings, option anniversaries, and public-domain entry. Alert before the actionable date, not on it.

**vi · Run the approach**  Contact records for authors, illustrators, heirs, agents, and estates; stage tracking from research through conversation to deal; evidence packet export.

## 04 — MVP definition

The first version covers United States trade children’s books — picture books and middle grade — published 1960 to 1998, with a seed corpus of roughly 5,000 titles weighted toward the 1968–1992 grant band. It computes all three channels, produces tiered ownership claims with visible evidence, ranks candidates, and holds the outreach record. It is a single-operator tool with no public surface.

### Explicitly out of scope for v1

- Notice drafting, service, or recordation — that work belongs to a rightsholder’s own counsel.

- Non-US territories and non-US originated works, other than flagging where territory is unsettled.

- Young adult, graphic novels, licensed-character and packaged series titles, which are largely work made for hire and fail the first filter anyway.

- Any subscriber-facing product, until the corpus is proven against real outcomes.

## 05 — Success criteria

| **Measure** | **Target** | **Why it is the right measure** |
|---|---|---|
| Corpus resolution | ≥ 95% | Share of seed titles resolved to a canonical work with a verified original publication date. Everything downstream depends on this date. |
| Channel precision | ≥ 90% | Availability calls that survive manual audit on a 100-title sample. Precision over recall: a false positive costs an outreach cycle. |
| Claim coverage | ≥ 60% | Share of corpus with a rights claim at tier 3 or better. Below this the ranked list is guesswork. |
| Qualified targets | 50 | Books with an available or soon-available rights position, a reachable counterparty, and a real adaptation case. |
| First conversation | 1 | One author, illustrator, estate, or agent in live discussion about a property surfaced by the system and not already known. |

### The bar

A working version produces fifty books you could plausibly acquire, each with the evidence attached and a name to call. Everything else in this pack exists to make that list true.
