# Source Parameters

**Document:** Helical Antenna_Modified_Parameter (1)(1).docx  
**Provenance:** SOURCE_SPECIFICATION  
**Do not edit these values in code unless the user explicitly requests a change.**

## Geometry and frequency

| Parameter | Value |
| --- | --- |
| Operating frequency | 3.035 GHz |
| Number of turns | 3 |
| Helix centerline radius | 20.94 mm |
| Pitch / vertical spacing | 29.27 mm |
| Wire | 18 AWG |
| Wire diameter | ≈ 1.024 mm |
| Wire radius | ≈ 0.512 mm |
| Ground-plane radius | 56.29 mm |
| Ground-plane diameter | 112.59 mm |
| Total axial helix length | 87.82 mm |
| Circumference / turn | 131.58 mm |
| Slant length / turn | 134.79 mm |
| Pitch angle | 12.54° |

## Performance table in the source (targets, not measurements)

| Performance parameter | Typical optimized value | Meaning in the document |
| --- | --- | --- |
| Operating frequency | 3.035 GHz | Centered on the target band |
| Reflection loss (S11) | ≤ (−15 dB to −25 dB) | Impedance match target |
| VSWR | 1.1:1 to 1.4:1 | Transmission-line match target |
| Directivity | 10.0–14.5 dBi | Beam concentration target |
| Antenna gain | 9.5–14.0 dB | Forward gain target |
| Axial ratio | < 1.5 dB | Circular polarization target |

These are **design targets**. They are not HFSS results.

## Calculated cross-checks (not source edits)

- C = 2πR = 2π × 20.94 = 131.5708 mm (source 131.58 mm)
- L_slant = √(C² + P²) = 134.795 mm (source 134.79 mm)
- α = atan(P/C) = 12.541° (source 12.54°)
- N × P = 3 × 29.27 = **87.81 mm** (source lists **87.82 mm**)

The 0.01 mm axial-length difference is rounding. Pitch is not changed.
