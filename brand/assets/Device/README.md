# Device

Two files, one motif. The shape is a colophon as it sets on a page: a centred block of type at the end of a book, lines tapering to a point. It is built only from rules, which is the single mark-making gesture this system allows.

The taper is irregular on purpose — two full measures, two short, one shorter — because a smooth ramp reads as a generic document glyph or, inverted, as signal strength.

## The files

**`colophon-device.svg`** — the mark. The block knocked out of a solid square, one ink: `stamp` `#9e3520`. This is a printer's device in the literal sense, ink pressed into paper, and it is the only place in the system the vermilion takes a solid fill. Use it on the evidence-packet head, on letterhead, as the favicon and as the avatar. It holds at 16px.

**`colophon-ornament.svg`** — the in-text form. The same block between two rules, one ink: `ink` `#1b1815`. For inside a document, where a solid vermilion block is too loud. It is an ornament, not a logo: it never appears beside the wordmark on a cover or a packet head.

## Ink

Each file carries a single `fill` attribute on a single path. Recolour by changing that one value, never by `currentColor` and never by CSS filters.

| Context | Device | Ornament |
| --- | --- | --- |
| Paper theme | `#9e3520` | `#1b1815` |
| Reader theme | `#d9694c` | `#efe9dc` |
| One-colour print or fax | `#1b1815` | `#1b1815` |

## Rules

- Square at every size. Never rounded, never circular, never on a tinted plate.
- Minimum 16px for the device. The ornament has no minimum below 14px because it stops being readable; use the device instead.
- Clear space is one quarter of the device's width on all sides.
- The device and the wordmark lock up horizontally with a `space-4` gap, device left, optically centred on the cap height. There is no stacked lockup.
- Never outlined, never reversed out of a photograph, never animated, never used as a bullet or a loading state.
