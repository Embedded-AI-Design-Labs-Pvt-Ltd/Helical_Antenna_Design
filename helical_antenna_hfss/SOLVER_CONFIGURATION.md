# Solver Configuration

These controls are ENGINEERING_ASSUMPTIONS except the center frequency, which is the source operating frequency.

| Item | Value |
| --- | --- |
| Project / design | Helix_3035MHz / Helix_3035MHz |
| Solution type | Driven Modal |
| Units | mm |
| Setup | Setup1 @ **3.035 GHz** |
| Maximum passes | 15 |
| Minimum passes | 4 |
| Minimum converged passes | 2 |
| MaxDeltaS | 0.02 |
| Percent refinement | 30 |
| Basis order | 1 (HFSS default first-order unless changed in GUI) |
| Sweep | Sweep, interpolating, 2.50–4.00 GHz, 151 points |
| Save radiated fields | Yes (needed for far-field vs frequency) |
| Far field | Infinite Sphere1 |

JSON copy: `hfss/setup/solver_configuration.json`.

Do not report ΔS or pass count as “converged” until HFSS writes a solution.
