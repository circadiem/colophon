# Colophon

Colophon finds children's books whose film and television adaptation rights are available, or
about to be, and routes them toward film and television. It produces evidence-backed leads with
confidence tiers. It never asserts clear title and never advises a rightsholder.

`CLAUDE.md` is binding. The specification lives in `docs/`: the discovery deliverables
`docs/I-*.md` through `docs/VII-*.md` are the source of truth and `docs/PRD.md` is the build spec.

## Layout

```
colophon/          source package (PRD correction, Step 0 answer 2.15: one importable namespace)
  harvest/         one module per source, writes snapshots only
  normalize/       snapshot -> typed rows, original ids preserved
  resolve/         edition clustering, canonical work + confidence
  graph/           rights graph: edges, parties, evidence sets
  channels/        §203, §304, contractual, option-lapse — pure functions   <- implemented
  inference/       evidence taxonomy, rules R1-R5, claim construction
  extraction/      batch prompts, typed events, span enforcement
  scoring/         adaptability model + calibration harness
  api/             single-tenant service for the surface
  web/             PWA: queue, work view, calendar, outreach
  compliance/      source-terms register, disclosure text, retention jobs
tests/             channel fixtures, worked examples, audit sampling      <- implemented
brand/             design tokens and component specs (not used yet)
docs/              the contract
```

Only `colophon/channels/` and `tests/` contain code. Everything else is a placeholder directory
with a README stating what it will hold (docs/V, Phase 0: channel rules are fixed and unit-tested
before Month 01 starts).

## Running the tests

```
pip install -e ".[dev]"
pytest
```

Runtime has no dependencies beyond the standard library. pytest is the only development dependency.
