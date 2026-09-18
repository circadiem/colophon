# tests

Channel fixtures, worked examples and (later) audit sampling. Every worked example from
`docs/II-rights-availability-logic.md` §05 lives in `tests/fixtures/` and must pass before any
channel-engine change merges (CLAUDE.md §4, §9).

`tests/fixtures/` holds the known cases as data: the inputs quoted from the deliverable and the
expected outputs. The `test_*.py` files assert against them.

## Fixture tables

`tests/fixtures/SCHEMA.md` defines two CSV tables, `cases.csv` (one row per fact, each with its
own tier and citation) and `expectations.csv` (one row per expected result at an injected
`as_of`). `tests/fixtures/loader.py` builds engine inputs from the first and checks the second.
The twenty-book manual pass records in this shape so that the research yields the regression suite
as a by-product. `tests/test_loader.py` proves the tables carry everything the hand-built fixtures
do by comparing the two paths result for result.
