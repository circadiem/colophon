# tests

Channel fixtures, worked examples and (later) audit sampling. Every worked example from
`docs/II-rights-availability-logic.md` §05 lives in `tests/fixtures/` and must pass before any
channel-engine change merges (CLAUDE.md §4, §9).

`tests/fixtures/` holds the known cases as data: the inputs quoted from the deliverable and the
expected outputs. The `test_*.py` files assert against them.
