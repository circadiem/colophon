# Lexicon

The word list is a compliance surface, not a style preference. Most of the ways Colophon could sound predatory are lexical.

## Use

**record · claim · evidence · tier · as-of · holder · chain · window · serviceable · reverted · channel · counterparty · confirming action**

These are the words the pack already runs on. They share one property: each of them is checkable. A reader can ask *what is the evidence* and get an answer.

## Avoid

| Never | Because |
| --- | --- |
| unlock, untapped, hidden gem, sitting on | Frames an author's own property as something being withheld from you. |
| opportunity, upside, undervalued | Investor language pointed at a person. Fine internally about the corpus; never in anything a rightsholder or their counsel reads. |
| orphan, orphaned work | Has a specific and contested statutory meaning. Using it loosely is both wrong and alarming. |
| expiring, running out, last chance, act now | Urgency pointed at someone else's deadline. The date is the message; the pressure is not. |
| grab, snag, lock up, secure the rights | Acquisition as capture. |
| harvest, scrape, mine | Accurate about the pipeline internally. Outside the codebase it describes the source and the person as raw material. |
| we believe, we think, probably, likely (as a hedge) | The tier already carries the uncertainty. A hedge on top of a tier is a hedge on a number, which reads as evasion. |
| own, owns, clear title | The one claim Colophon never makes. VI, verbatim: nothing leaves the system asserting clear title. |

Note that *likely* survives inside the status enums — `REVERTED·LIKELY`, `NEVER·GRANTED` — where it is a defined term with a rule behind it. That is the distinction: a defined term is a value, a hedge is a mood.

## Naming conventions

**Status enums.** Uppercase, mono, interpunct-joined, never spaced or hyphenated: `TERMINABLE·NOW`, `EXCLUDED·WFH`, `PUBLIC·DOMAIN`. They appear identically in the interface, in exports, in the schema and in conversation. One string, everywhere — the operator should be able to read a status aloud to a lawyer and have it mean the same thing.

**Tiers.** Always *tier 1* through *tier 4*, lowercase word plus numeral. Never T1, never "high confidence," never a star rating. The ladder in VII is an operating budget; naming it like a quality score invites people to read tier 4 as bad rather than as cheap.

**Channels.** *Channel A — contractual reversion*, *Channel B — option lapse*, *Channel C — statutory termination*. The letters are load-bearing, because the whole thesis in 00 is that C is the narrowest of the three and the only one anyone watches.

**Dates.** ISO, always: `2026-09-17`. Partial dates truncate rather than guess: `1989-04`, not "April 1989" and never "1989-04-01". A fabricated day of the month is a fabricated fact.

**The document mark.** `COLOPHON · VIII · BRAND IDENTITY` — spaced interpunct, `section-label` tracking, `ink-tertiary`. Runs at the foot of every deliverable beside the preparer's name.
