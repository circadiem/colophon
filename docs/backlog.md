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

### Rollup readings the answers do not state

Resolved: the grant is the unit of computation and the triple the unit of reporting; `contribution`
stays an attribute of the grant, not a fourth axis (Step 2 answers). The rollup is implemented in
`colophon/channels/rollup.py`. Three readings it applies that the answers leave open, for the
docs/II §01 edit:

- A disjunctive level ignores an Undetermined result when a sibling has a status; a level whose
  constituents are all Undetermined has no position.
- At the conjunctive level a contribution with no position makes the triple unknown, unless
  another contribution is terminal, in which case the triple is blocked: a known blocker
  dominates an unknown.
- A grant with no recorded `contribution` forms its own group; it is not assumed to cover both.

## Delivered from the Step 1 automation asks

- Fixture loader with a documented table schema: `tests/fixtures/SCHEMA.md`, `tests/fixtures/loader.py`.
  The manual research protocol is designed against this schema.
- `explain(result)` in `colophon/channels/explain.py`, straddles first.
- Protocol send-backs: `contribution` on grants; `counterparty.csv` and `demand.csv` validated in the
  same one-row-per-fact shape; duplicate field rows load as contradictions, never as errors or
  last-write-wins; `signals.last_reprint` as a date that survives the threshold decision.
- Rollup rule (three levels) as `rollup.py`; termination-interest fractions must sum to 1.

## Declined

- Docx-to-markdown converter. `docs/*.md` is canonical; the Word file and PDFs are circulation
  artifacts and are not upstream of the repo.
