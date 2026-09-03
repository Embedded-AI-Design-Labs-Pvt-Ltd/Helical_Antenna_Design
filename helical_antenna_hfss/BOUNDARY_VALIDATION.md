# Boundary Validation

## Calculated wavelength

f = 3.035 GHz  
λ0 = 299792458 / 3.035e9 = **98.778 mm** (CALCULATED)

Padding = 0.5 λ0 ≈ **49.39 mm** (ENGINEERING_ASSUMPTION)

## Checks after the HFSS model is built

| Check | Expected |
| --- | --- |
| Radiation boundary Rad1 on RadBox | Present |
| RadBox material | vacuum |
| Helix, ground, feed post, port | Entirely inside RadBox |
| No unintended PEC on RadBox faces | Radiation, not Perfect E |
| Port inside computational region | Yes |
| Overlaps | Inspect in HFSS (boolean/interference) |
| Disconnected feed | Helix start should meet FeedPost at z = gap |

PML is not used on the first pass. Switching to PML is an engineering change, not a source requirement.

Air-box numbers: `hfss/boundaries/radiation.json`.

Mesh/boundary interaction after solve: **NOT SIMULATED**.
