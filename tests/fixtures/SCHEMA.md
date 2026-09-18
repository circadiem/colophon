# Fixture table schema

The twenty-book manual pass (Manual Research Protocol) records facts in this shape, and
`tests/fixtures/loader.py` turns the tables into engine inputs and regression checks. One row per
fact, because every fact carries its own tier and citation (CLAUDE.md I2, I3). Four fact tables
share one column set; one expectations table closes the loop.

## Common columns — every fact table

| Column | Meaning |
| --- | --- |
| `case_id` | Groups the rows of one work across every file. Free text, stable. |
| `work_id` | The canonical work. Same for every row of a case. |
| `grant_id` | The grant this fact belongs to. Blank for work-level, search, signal, counterparty and demand rows. |
| `field` | Which fact. See each table's field list. |
| `value` | The fact. Dates as `YYYY`, `YYYY-MM` or `YYYY-MM-DD` at the precision actually known. Booleans `true`/`false`. Lists separated by `;`. |
| `tier` | 1–4 by the docs/VII §02 taxonomy, not by how sure you feel. Required on every row. |
| `source_id` | The source the citation came from. Required. Your own prose cites `researcher`. |
| `url` | Where it was captured. |
| `capture_date` | `YYYY-MM-DD`. Required on every row. For `search` rows this is the date the search ran. |
| `citation_span` | Verbatim text from the source. Required; no span, no record. |

### Rules the loader enforces

- A row without a span, a tier in 1–4, a source or an ISO capture date is rejected.
- Two rows for the same `(grant_id, field)` with the **same** value corroborate: the fact takes
  the strongest tier and keeps every citation.
- Two rows for the same `(grant_id, field)` with **different** values are a **contradiction**.
  The loader does not error and does not pick one. The contested fact never reaches the engine,
  the contradiction is recorded on the case, and it can be asserted in `expectations.csv` with
  `CONTRADICTION:<field>`. A contested `grantor` withholds the whole grant from the engine.
- A notice row requires a `search` row. A notice comes from a search (CLAUDE.md I7).

## `cases.csv` — engine inputs

**Work-level** (blank `grant_id`): `original_publication_date` · `copyright_secured` (a separate
fact, never derived from publication).

**Grant-level:** `right_types` (`publication;dramatic;audio;merchandise;other`) · `grantor`
(`author` / `statutory_successor` / `other`) · `executed_on` · `conveys_publication` ·
`publication_under_grant` · `executing_authors` (integer) · `work_made_for_hire` · `grantee` ·
`contribution` (`text` / `illustration` / `both`). Separate text and art agreements are two
grants with two `grant_id`s; `contribution` labels which is which and does not change the
arithmetic.

**Recordation search** (blank `grant_id`, one per case): `search`. `value` is the parameters as
run; `capture_date` is when it ran; `tier` and the citation describe the index consulted. A search
that found nothing is still a row.

**Recorded termination notices** (`grant_id` set; `k` numbers notices on the grant):
`notice.k.section` (`203` / `304c` / `304d`) · `notice.k.served_on` · `notice.k.effective_on` ·
`notice.k.terminating_parties` (`;`-separated).

**Channel A signals** (blank `grant_id`): `signals.no_edition_in_print` · `signals.no_ebook_or_audio`
· and either `signals.last_reprint` (a date, or `never`; the durable fact) or
`signals.no_reprint_within_threshold` (a boolean you evaluated yourself, with the basis in the
span). Prefer the date. The reprint threshold is unset in docs/II §03, so a case that carries only
the date fails loudly at load until the number lands; that is the intended behaviour.

## `expectations.csv` — one row per expected result

| Column | Meaning |
| --- | --- |
| `case_id`, `grant_id` | As above. `grant_id` blank for a Channel A expectation. |
| `as_of` | `YYYY-MM-DD`. Injected; never today. Primary rows use 2026-09-17; add a second row wherever the status flips within about two years. |
| `channel` | `A` / `B` / `C`. |
| `section` | `203` / `304c` / `304d`, blank for Channel A. |
| `expected` | A status name (`LAPSED_WINDOW`), `UNDETERMINED:<REASON>` (`UNDETERMINED:EXECUTION_DATE_REQUIRED`), or `CONTRADICTION:<field>`. |
| `window_start` / `window_end` / `last_serviceable_date` | Optional. `DateRange.display()` form: `2022-09`, `2025-08-31..2025-09-29`, `2023-01-09`. Checked when present. Compute by hand first. |
| `tier` | Optional. The weakest input the branch actually used. Checked when present. |
| `note` | Free text; the operator's verdict or the source of the expectation. |

## `counterparty.csv` — people and the route to call (Protocol §F)

Validated for shape and contradictions; not an engine input. Public records only (CLAUDE.md §2):
death and survivorship indexes, probate filings, agency and estate pages, the trademark register.
A `search` row per case is required, recording the indexes consulted even when empty.

Fields: `author.living` · `author.death_date` · `illustrator.living` · `illustrator.death_date` ·
`heir.k.name` · `heir.k.relation` · `heir.k.branch` · `probate.jurisdiction` · `probate.executor` ·
`termination_interest.<party>.fraction` · `termination_interest.clears_majority` · `agent.name` ·
`agent.handles_dramatic_rights` · `agent.route` · `estate.name` · `estate.handles_dramatic_rights` ·
`estate.route` · `publisher.permissions_desk` · `trademark.k.mark` · `trademark.k.registrant` ·
`trademark.k.status` · `counterparty.name` · `counterparty.route` · `search`.

The termination-interest fractions are computed by hand for now; per-stirpes math is deferred to
Month 01 (Step 0 answer 2.13).

## `demand.csv` — adaptation and demand evidence (Protocol §G)

Validated for shape and contradictions; feeds R2/R3 in `inference/` and the adaptability rubric
later. Fields: `adaptation.k.year` · `adaptation.k.producer` · `adaptation.k.status` ·
`derivative_exception_engaged` · `award.k` · `in_print.from` · `in_print.to` · `in_print.gap.k` ·
`canon_list.k` · `character_led` · `screen_case` (your three sentences; `source_id` = `researcher`,
the span is the prose itself).
