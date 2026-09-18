# Applications

Per I and IV, v1 is single-tenant with no public surface. The brand therefore has exactly three places to exist, and two of them are documents.

## i · The operator surface

A PWA (IV), which has to work on a phone at a book fair. The brand shows up here almost entirely as restraint.

- The queue is a table, not a card grid. `table-head` over `table-cell`, rows separated by `rule` hairlines, `surface-sunken` zebra. No elevation anywhere.
- Every row carries: title, status chip, tier badge, as-of date, counterparty. If a row cannot show its tier at the current width, the tier stays and something else goes.
- One `stamp` action per screen. Everything else is a `rule-strong` outline control.
- The evidence chain is one click from any claim — V calls this the thing that makes the tool usable in a conversation with a lawyer, and it is also the whole brand promise rendered as an interaction.
- No dashboards. No counts of books processed, no completion percentages, no streaks. The measures in I are audit criteria, not a home screen.

## ii · The evidence packet

The highest-value branded object in the business: a single clean document per target, exported for counsel or a producer (V, month 03). It will be forwarded to people who have never seen anything else from Colophon, which makes it the de facto brand.

**Structure:**

1. **Head.** `COLOPHON · EVIDENCE PACKET`, the work id, the export date, the rule version. All `datum`.
2. **The research label**, verbatim from VI, in `caption` on `surface-sunken` — above the fold, never in a footer. It says this is research carrying tiers and dates, that it does not assert clear title, and that it is wrong sometimes by design.
3. **The work.** Canonical title, author, illustrator, original publication date with its resolution-confidence score.
4. **Status**, per triple — work, right type, territory — each with its channel, its dates, and its `last_serviceable_date` where one exists. Territory carries its unsettled flag (II).
5. **The claim.** Asserted holder, tier, the rule that fired, and the rule version.
6. **The evidence table.** One row per item: source, what it establishes, tier, url, capture date, citation span. The span sets on `evidence-span`.
7. **Contradictions**, if any. Shown, never suppressed. A packet that hides its contradiction queue is worth less than one that shows it.
8. **The confirming action**, and what it would cost.

Set in `serif` throughout with every computed value in `mono`. Square corners, hairline rules, one `stamp` element: the head mark. It should look like something produced by an institution, because the reader's first question is going to be who made this and how much of it can I rely on.

## iii · The first-contact letter

Specified in the Voice section. Design notes only:

- One page. `serif` / `body` on `surface-page`, generous margins at `space-7`.
- The mark at the head; nothing else coloured. In particular the disclosure paragraph is not highlighted, boxed, or set in a tint — emphasis on a disclosure reads as a disclaimer, and a disclaimer reads as something being got past you.
- Computed values in `mono` inline, which is the only visual distinction on the page.
- No letterhead flourish, no tagline, no url beyond a plain contact line.

## Later surfaces, and what they inherit

Per V, the intel subscription and the consumer read-then-watch product both come after the first acquisitions. Two notes for when they do:

**The intel product** is the same brand, more compressed. Alerts are dated statements of record, not notifications: `TERMINABLE·FUTURE · notice opens 2028-03 · tier 2`. The temptation will be to make them exciting. Every degree of excitement moves the brand toward the fund and away from the registry.

**The consumer product should not be Colophon.** Different audience, different promise, and VI wants separation on the acquiring side anyway. See the Architecture section.
