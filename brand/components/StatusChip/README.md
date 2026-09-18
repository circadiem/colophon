# StatusChip

The status enum from II, rendered so it reads identically on a screen, in an export, and aloud to a lawyer. This is the most-repeated object in the system and the one that carries the most legal weight, so it is deliberately plain: a hairline square, mono caps, one colour that means something.

## Rules

- The label is the enum verbatim — uppercase, interpunct-joined, never spaced, hyphenated, title-cased or abbreviated. `EXCLUDED·WFH`, never "Excluded (WFH)".
- Never wraps. If it does not fit, the container is wrong.
- Colour comes from the five status tokens, mapped in the brand book. Three actionable statuses share `status-open` on purpose: the operator's question is *do I act on this*, and the word carries the rest.
- A chip never appears alone. It travels with a `TierBadge` and an as-of date, because a status without evidence is a guess (II) and the interface must show the difference.
- No animation, no pulse, no "new" state, no countdown on `TERMINABLE·FUTURE`. The date is the message.
- `radius-sm` and a 1px border in the status colour. No fill — a filled chip reads as a notification, and nothing here is a notification.

## What the consumer provides

The status string and its tier. The component does no mapping of its own beyond enum → colour, so an unrecognised enum renders in `status-closed` rather than guessing.
