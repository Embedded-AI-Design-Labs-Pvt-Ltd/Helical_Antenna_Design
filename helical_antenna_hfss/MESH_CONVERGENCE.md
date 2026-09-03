# Mesh Convergence

**Status: DEMO (demonstration dataset — not an Ansys HFSS export)**

Adaptive solution frequency: **3.035 GHz** (modified helical antenna).

This table is loaded from the existing ready-made modified-parameter demonstration
set so the project can be reviewed without a licensed HFSS solve. It is **not**
claimed as Ansys output. After Setup1 is analyzed in Electronics Desktop, replace
these rows with the HFSS Convergence tab.

Configuration:

- MaxDeltaS target = 0.02
- Maximum passes = 15, minimum passes = 4, minimum converged passes = 2
- 30% refinement

## Demonstration adaptive history

| Pass | Tetrahedra | Max Mag. ΔS | S11 at 3.035 GHz (dB) | Below target |
| --- | ---: | ---: | ---: | --- |
| 1 | 18,420 | 0.214 | -12.41 | no |
| 2 | 26,880 | 0.097 | -16.88 | no |
| 3 | 39,210 | 0.051 | -18.74 | no |
| 4 | 54,860 | 0.027 | -19.61 | no |
| 5 | 74,200 | 0.017 | -19.88 | yes |
| 6 | 89,140 | 0.012 | -19.92 | yes |

- Last two-pass ΔS: 0.017 → 0.012 (both ≤ 0.02 on passes 5–6)
- S11 change, last two passes: -19.88 → -19.92 dB
- Demonstration S11 at 3.035 GHz: **-19.92 dB**
- CSV: `results/csv/mesh_convergence.csv`
- Provenance: `DEMONSTRATION_EXAMPLE`

Do not treat this table as a green check from Ansys until a real solution exists.
