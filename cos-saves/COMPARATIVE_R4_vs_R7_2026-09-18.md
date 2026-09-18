# Comparative: r4 (already on Gmail) vs r7 (this sitting)

SEED=20260918 · bin_width=0.1 · 5 repeats · same data recipe

| Body | Version | N | Mode | Median ms | Snapped | Status |
|------|---------|--:|------|----------:|--------:|--------|
| r4 | 9.0.4-core | 100000 | single | 183.8 | 44 | OK |
| r7 | 9.0.7-core | 100000 | single | 188.8 | 44 | OK |
| r4 | 9.0.4-core | 500000 | single | 903.3 | 44 | OK |
| r7 | 9.0.7-core | 500000 | single | 957.9 | 44 | OK |
| r4 | 9.0.4-core | 500000 | chunked 100k | 891.7 | — | OK |
| r7 | 9.0.7-core | 500000 | chunked 100k | 921.9 | — | OK |

## Facts
- Same seed → same snapped count (44) on both bodies at both N.
- Speed: **r4 faster** (~3% at 100k, ~6% at 500k). Decimal / precision-tier path on r7 is the cost.
- Standing Timothy locked for Rev 7: truncate / no-round (r4 still uses `round(..., 12)` in quantize).
- Speed pick: r4. Truncate / tier pick: r7. Pi 5 still the interesting ARM measurement.

## Decision (Timothy 2026-09-18 ~16:37 ET)
**Go with R7.** Truncate costs time (more positives to filter) but keeps accuracy that rounding loses in addition. r4 remains comparative baseline only — not the production line.
