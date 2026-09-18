# DeviceMark

The device at its working sizes, alone and locked up with the wordmark. The mark is the colophon block knocked out of a solid vermilion square; the ornament is the same block between two rules, in ink, for use inside a document.

## Rules

- The device is the only solid `stamp` field in the system and the only drawn element in it. Everything else is type and hairlines.
- 16px minimum. It was drawn square and knocked out precisely so it survives a browser tab and an avatar, which no outlined version of it does.
- Lockup is horizontal only, `space-4` between device and wordmark, device left. No stacked form exists and none should be drawn.
- The ornament never appears beside the wordmark. It sits alone in running text, at a section break or at the end of a document, the way a printer's ornament does.
- Never rounded, tinted, outlined, animated, or used as an icon for anything. It marks the document; it does not label a feature.

## What the consumer provides

Nothing. Both forms ship as single-path SVGs in the Device asset group, each with one `fill` attribute. Recolour by swapping that value against the table in that group's notes; never `currentColor`, never a CSS filter.
