# KBLD9 SAVE — 2026-09-19

Production: Rev 7 truncate / no-round (`9.0.7-core`)

| Body | SHA-256 | Probes |
|------|---------|--------|
| Python `kbld9_core_r7.py` | `465359bb0339d3acdd1b94282a0d9191fb663b734cd2b552e36baf5e75da31d8` | 51/51 |
| C++ `kbld9.hpp` | `d839e11f01a8427300edc821880f1790bacf78f96da95c45fbde40105e2be240` | 45/45 |

Rejected alternate: `179d152b…` (827 lines) — not our seal.

A15 + Pi 5: load **ours**. Pi 5 over budget = ARM Decimal-cost finding.

## Drive
https://drive.google.com/file/d/13WyKuRiRi8nxCyUBvKjfPuXHjKPRTSxN/view?usp=drivesdk

Tar SHA-256: `1429ba772e97f3bb2f4017bfd73986131fb73d93945203fa064fddd016a627b2`

## Notion
https://app.notion.com/p/3e0c86699c9481d0a18fcb32ccce076b

## Bench
`bench/kbld9_host_bench.py` + `bench/kbld9_host_bench.cpp` — SEED 20260918, bin_width 0.1. Timing is a finding, not a fail.
