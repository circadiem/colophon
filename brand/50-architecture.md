# Architecture and open decisions

## Brand architecture

Four things could eventually carry a name. VI's entity-separation requirement decides most of the structure before any design question arrives.

| Thing | Name | Why |
| --- | --- | --- |
| The rights-intelligence engine and operator tool | **Colophon** | The core. Everything in this system describes it. |
| The intel subscription (V, after v1) | **Colophon** | Same brand, same promise, same evidence standard. A subscriber is buying the record. |
| The acquiring entity | **Separate, and separately named** | VI: selling availability intelligence while acquiring from the same population is a conflict a counterparty will eventually name. If the intel product ships, the buyer cannot be called Colophon too. |
| The author-side reversion service (V, gated on VI) | **Separate, and visibly unrelated** | The highest-trust and highest-conflict product in the plan. Shared branding with an acquirer defeats its entire premise. A shared visual system would too. |
| The consumer read-then-watch product | **Its own name** | Different audience, different promise. Colophon is a word for the trade; a parent choosing tonight's film has no use for it. |

The consumer product is the interesting one, because V notes it runs on the same adaptation graph. One dataset, two products — but the brand relationship should be *nothing at all* in public. A children's-viewing app visibly owned by a rights-acquisition company is a story nobody needs written about them.

## Open decisions

**Trademark clearance.** Not run. "Colophon" is a common noun in the book trade and is in live use by presses and design studios, so the word alone is almost certainly unregistrable in the relevant classes. Options, in order of preference:

1. A compound that keeps the word — the distinguishing element carries the registrability.
2. Colophon plus a device mark, registered as a composite.
3. Use it unregistered for the operator-only period, which costs nothing while there is no public surface, and decide before the intel product exists.

This should be closed before anything goes in front of a counterparty on letterhead.

**The device mark.** Settled. The colophon block knocked out of a solid vermilion square, with a rules-and-block ornament as the in-text form; both are in the Device asset group. Two alternates were drawn and dropped: the block inside a hairline square, which had to lose its frame below 20px and so changed shape at the size it gets used most, and a standalone typographic setting, which survives as the ornament. One thing still to check in the wild: the taper is adjacent to the generic document glyph and, inverted, to a signal-strength icon. Look at the 16px form in a real browser tab before it goes on anything printed.

**Territory in the interface.** II models territory as a flagged variable pending the Supreme Court petition. The brand question is how a flagged value looks without looking broken — current answer is `datum` in `ink-tertiary` with the flag as a word, never a warning colour, because an unsettled question of law is not an error state.

**Domain and contact surface.** Not settled. Whatever it is, the first-contact letter's contact line is the only place it appears in v1.

## What this system does not yet contain

Reported honestly so the next pass knows where to start:

- No stacked or vertical lockup, and no alternate device for square crops beyond the primary one. Neither has come up yet; both are easy to add and neither should be drawn speculatively.
- No font binaries. All three families are hosted Google faces, named in `type.families` only. **Spectral is settled as the display and text face**, chosen against Libre Caslon and a mono-display direction; Plex Sans and Plex Mono follow from it and were not separately contested. A licensed display face would replace Spectral here and nothing else in the system would move.
- No components for the queue table, the window calendar, or the outreach pipeline — those wait until V's month 02, when the ranked queue replaces the flat board and the real shapes are known.
- No dark-mode decision for the evidence packet. Exports are paper objects and are currently Paper-only; whether the reader theme applies to a PDF is unresolved.
- The colour tokens were derived from the CO·DISC pack's own typographic register, not sampled from an existing brand file. If one exists, it supersedes this.
