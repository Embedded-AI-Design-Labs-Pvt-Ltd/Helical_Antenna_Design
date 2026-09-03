# Validation Plan

## Geometry (always runnable)

Compare generated helix against SOURCE_PARAMETERS.md with 0.02 mm / 0.02° tolerance.

Must pass before HFSS launch: turns, R, pitch, wire Ø, ground R, C/turn, slant, pitch angle, axial length (allow 0.01 mm rounding vs 87.82 mm).

## Port / boundary (inspect in HFSS GUI)

See PORT_VALIDATION.md and BOUNDARY_VALIDATION.md.

## Electromagnetic (only after Analyze)

| Test | Requirement | Data source |
| --- | --- | --- |
| S11 at 3.035 GHz | ≤ −15 dB | Setup1:Sweep |
| VSWR at 3.035 GHz | 1.1–1.4 | Setup1:Sweep |
| Directivity | 10.0–14.5 dBi | Infinite Sphere1 @ 3.035 GHz |
| Gain | 9.5–14.0 dB | Infinite Sphere1 @ 3.035 GHz |
| Axial ratio | < 1.5 dB | Main-beam direction only |

PASS requires a real extracted value. Otherwise **NOT SIMULATED**. FAIL if solved and out of spec.

## Automation

`scripts/validation.py` writes `results/acceptance_matrix.csv` and `VALIDATION_REPORT.html`.

## QA tests

`python -m unittest discover -s tests`

These tests assert source geometry and that result fields stay empty until solved.
