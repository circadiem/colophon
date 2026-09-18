# channels

The statutory date engine: §203 with the dual clock, §304(c), §304(d), and the out-of-print
archetype of Channel A. Pure functions over a work and its grant edges, returning per-grant,
per-channel results with dates, tier and evidence. No I/O, no database, no network, no model, no
clock reads except an injected `as_of` (CLAUDE.md I6). Governed by
`docs/II-rights-availability-logic.md` and CLAUDE.md §4; the Step 0 answers are binding until the
doc edits they describe land.

| Module | Holds |
| --- | --- |
| `version.py` | `RULE_VERSION`, stamped on every result and assertion |
| `dates.py` | `PartialDate` (day / month / year precision), `DateRange`, `add_years`; the calendar conventions |
| `model.py` | Inputs: `Work`, `Grant`, `Fact` (value + tier + evidence), `NoticeSearch`, `OutOfPrintSignals` |
| `status.py` | The eight-value `Status` enum and the `Reason` enum for undetermined results |
| `results.py` | `StatusResult`, `Undetermined`, `StatutoryWindow`, `NoticeSummary` |
| `section_203.py` | §203, readable top to bottom against the statute |
| `section_304.py` | §304(c) and §304(d), including the 1978 floor and the exercised check |
| `channel_a.py` | Out-of-print archetype; reprint threshold unresolved, no default |
| `engine.py` | `compute()`: every channel, every grant, one `as_of`, no merge |
| `replay.py` | Assertions, `supersede()`, and the reviewable diff between rule versions |
| `rollup.py` | The three-level rollup from per-grant results to a reported triple position; grant is the unit of computation, triple the unit of reporting |
| `explain.py` | `explain(result)`: a result rendered for a human auditor; straddles name their candidate statuses |

Not implemented here: `PUBLIC_DOMAIN`, Channel B, the other Channel A archetypes, per-stirpes
holder shares, and the execution-date presumption
(CLAUDE.md §5.1). Each is either unspecified or out of this build's scope; see the README at the
repo root.
