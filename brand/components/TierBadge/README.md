# TierBadge

Confidence as a count of filled squares, not a colour and not a word. Four squares, filled from the left: tier 1 fills all four, tier 4 fills one. It reads as a ledger notation rather than a rating, which is the point — VII's ladder is an operating budget, and a badge that looked like a star rating would invite people to read tier 4 as bad rather than as cheap.

## Rules

- Tier is never coloured. Colour in this system means status, and only status. The badge is `ink` for filled and `rule-strong` for empty, in both themes.
- The numeral is always shown beside the squares in `datum`. The squares are the glance; the numeral is the record.
- Always paired with the as-of date, `space-1` apart. VII's `confidence_decay` means a tier without a date is a claim that will eventually lie.
- Tier 4 is not a warning. It is rule R4 — no recorded grant, no adaptation, no deal trace — which VII calls the cheapest deals in the corpus. Nothing in the styling should make it look like a problem.
- Never abbreviated to T1–T4 in any surface a counterparty sees.

## What the consumer provides

The integer tier and the as-of date, already formatted ISO. The component does not compute decay; it renders what the claim record holds.
