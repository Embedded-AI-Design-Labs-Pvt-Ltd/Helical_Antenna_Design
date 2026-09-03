# Project Requirements

## Source of truth

`docs/source/Helical Antenna_Modified_Parameter (1)(1).docx`

Do not change source-defined antenna parameters unless explicitly requested.

## Operator requirements

An engineer must be able to:

1. Generate the antenna geometry.
2. Open the model in Ansys Electronics Desktop / HFSS.
3. Inspect the 3D geometry in the HFSS GUI.
4. Assign materials.
5. Define excitation / feed.
6. Define radiation boundary.
7. Create adaptive solution setup.
8. Run frequency sweep.
9–15. Generate S11, VSWR, gain, directivity, axial ratio, 2D and 3D patterns (after a real solve).
16. Compare results against targets automatically.
17. Export plots and tables.
18. Generate an HTML simulation report.

## Target results (acceptance, not claimed measurements)

| Quantity | Target |
| --- | --- |
| Operating frequency | 3.035 GHz |
| S11 | ≤ −15 dB, preferred −15 to −25 dB |
| VSWR | 1.1:1 to 1.4:1 |
| Directivity | 10.0 to 14.5 dBi |
| Gain | 9.5 to 14.0 dB |
| Axial ratio | < 1.5 dB (main beam) |

PASS is allowed only when an HFSS result exists and meets the target.
If HFSS has not solved: **NOT SIMULATED**.

## Non-requirements from the source document

The source does **not** define coax geometry, dielectric, conductor conductivity,
air-box size, or exact port implementation. Those are documented assumptions.
