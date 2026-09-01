# Paper v2: Pre-Gate Scaffold

This directory is the active staging area for the transcript-insufficiency
reformulation. It is intentionally a small, compilable outline rather than a
claim of completed theory or experiments.

The manuscript remains in **pre-go/no-go** status. Full prose, theorem claims,
results, figures, and tables should be added only after the TraceTwin,
sequential-certificate, and real action-boundary gates are satisfied.

## Repository Boundary

- `paper/` is the frozen legacy manuscript. Do not edit or build it in place.
- `paper_v2/` is the only manuscript directory written by the root build
  targets.
- This scaffold does not copy legacy manuscript text, figures, tables, data, or
  result claims.
- Promotion of `paper_v2/` to `paper/` happens only after the go/no-go decision
  and the requested legacy Git tag are complete.

## Build

From the repository root:

```bash
make paper
make check-paper-v2
```

The PDF is written to `paper_v2/build/main.pdf`. The legacy boundary can be
checked without building either manuscript:

```bash
make check-legacy-paper
```

`make clean` removes only Paper v2 build products.

## Current Outline

The placeholder sections reserve space for the audit contract, TraceTwin and
certificate duality, the sequential certificate, the go/no-go evaluation, and
claim boundaries. Each section is explicitly marked as planned work.
