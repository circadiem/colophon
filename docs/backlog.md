# Build backlog

The manual research pass generates this list (docs/V §02: "the list of every step that was
tedious, which becomes the build backlog"). Items raised in build sessions land here too.

## First-class items

### Matching recorded termination notices to reconstructed grants

Raised in Step 1, confirmed in the Step 1 answers (item 6).

`channels/` matches a notice to a grant by `grant_id` and section. The recordation index carries
no such id, so the real join is fuzzy: work, parties and dates. Termination notices are the one
source where recordation is mandatory and absence is meaningful (docs/III §01, CLAUDE.md I7), so a
bad join does not merely miss a notice. It manufactures a false "no notice has been served", which
is the most expensive wrong answer in the system.

Needs: its own precision target and its own audit sample, separate from the 100-title channel
audit. Owner: the graph and normalize layers, Month 01.

## Delivered from the Step 1 automation asks

- Fixture loader with a documented table schema: `tests/fixtures/SCHEMA.md`, `tests/fixtures/loader.py`.
  The manual research protocol is designed against this schema.
- `explain(result)` in `colophon/channels/explain.py`, straddles first.

## Declined

- Docx-to-markdown converter. `docs/*.md` is canonical; the Word file and PDFs are circulation
  artifacts and are not upstream of the repo.
