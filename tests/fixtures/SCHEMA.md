# Fixture table schema

The twenty-book manual pass records facts in this shape, and `tests/fixtures/loader.py` turns the
tables into engine inputs and regression checks. One row per fact, because every fact carries its
own tier and citation (CLAUDE.md I2, I3). Two files.

## `cases.csv` — one row per fact

| Column | Meaning |
| --- | --- |
| `case_id` | Groups the rows of one work. Free text, stable. |
| `work_id` | The canonical work. Same for every row of a case. |
| `grant_id` | The grant this fact belongs to. Blank for work-level, search-level and signal rows. |
| `field` | Which fact. See the field list below. |
| `value` | The fact. Dates as `YYYY`, `YYYY-MM` or `YYYY-MM-DD` at the precision actually known. Booleans `true`/`false`. Lists separated by `;`. |
| `tier` | 1–4 per docs/VII §02. |
| `source_id` | The source the citation came from. |
| `url` | Where it was captured. |
| `capture_date` | `YYYY-MM-DD`. For `search` rows this is the date the search was run. |
| `citation_span` | Verbatim text from the source. Required; no span, no record. |

### Work-level fields (blank `grant_id`)

`original_publication_date` · `copyright_secured`

### Grant-level fields

`right_types` (`publication;dramatic;audio;merchandise;other`) · `grantor` (`author` /
`statutory_successor` / `other`) · `executed_on` · `conveys_publication` ·
`publication_under_grant` · `executing_authors` (integer) · `work_made_for_hire` · `grantee`

### Recordation search (blank `grant_id`; at most one per case)

`search` — `value` is the search parameters as run, `capture_date` is when it ran, `tier` and
citation describe the index consulted. A search that found nothing is still a row (CLAUDE.md I7).

### Recorded termination notices (`grant_id` set; `k` numbers notices on the grant)

`notice.k.section` (`203` / `304c` / `304d`) · `notice.k.served_on` · `notice.k.effective_on` ·
`notice.k.terminating_parties` (`;`-separated)

### Channel A signals (blank `grant_id`)

`signals.no_edition_in_print` · `signals.no_ebook_or_audio` · `signals.no_reprint_within_threshold`

## `expectations.csv` — one row per expected result

| Column | Meaning |
| --- | --- |
| `case_id` | As above. |
| `grant_id` | Blank for a Channel A expectation. |
| `as_of` | `YYYY-MM-DD`. Injected; never today. |
| `channel` | `A` / `B` / `C`. |
| `section` | `203` / `304c` / `304d`, blank for Channel A. |
| `expected` | A status name (`LAPSED_WINDOW`) or `UNDETERMINED:<REASON>` (`UNDETERMINED:STRADDLES_AS_OF`). |
| `window_start` / `window_end` / `last_serviceable_date` | Optional. `DateRange.display()` form: `2022-09`, `2025-08-31..2025-09-29`, `2023-01-09`. Checked when present. |
| `tier` | Optional. Checked when present. |
| `note` | Free text; the operator's verdict or source of the expectation. |
