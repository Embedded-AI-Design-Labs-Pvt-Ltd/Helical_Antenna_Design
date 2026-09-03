# Engineering Assumptions

**Provenance: ENGINEERING_ASSUMPTION**

The source Word document defines helix geometry, wire gauge and performance *targets*.
It does **not** define the items below. They are first-pass modeling choices so that
an HFSS project can be built. They are **not** source requirements.

## Feed / port (not in source)

| Item | Assumed value | Why |
| --- | --- | --- |
| Excitation type | 50 Ω lumped port P1 | Source has no coax drawing |
| Reference impedance | 50 Ω | Industry default; not specified |
| Feed gap | 1.50 mm | Needed so the helix does not short to the ground plane |
| Port sheet | XZ rectangle, width = wire Ø 1.024 mm, height = 1.50 mm, at x = R | Spans the gap |
| Integration line | (R, 0, 0) mm → (R, 0, 1.50) mm | Helix positive relative to ground |
| Feed post | Cylinder, radius = wire radius 0.512 mm, height = gap | Connects helix start to the port |
| Connector | Not modeled | No SMA/N drawing in source |
| Coax dielectric | None (vacuum gap) | No εr given |
| How to replace | See `docs/feed_and_port.html` and `PORT_VALIDATION.md` | When physical feed data exists |

## Materials (not in source)

| Object | Material | Notes |
| --- | --- | --- |
| HelixWire | copper | 18 AWG implies copper in practice; document does not name the metal |
| GroundPlane | copper | Same |
| FeedPost | copper | Same |
| RadBox | vacuum | Air approximation |
| PEC | **not used** by default | If enabled later, that is also an assumption, not a source requirement |
| Copper conductivity | 5.8×10⁷ S/m | HFSS copper library typical |

## Ground thickness (not in source)

1.00 mm. The source gives radius/diameter only.

## Winding sense (not in source)

Right-hand helix. Kraus convention: RH winding → RHCP in the forward axial beam.
Change to left-hand only if the hardware is LH.

## Radiation region (not in source)

| Item | Value |
| --- | --- |
| λ0 at 3.035 GHz | c/f = 98.778 mm (**CALCULATED**) |
| Padding | 0.5 λ0 ≈ 49.39 mm |
| Boundary | Radiation on object RadBox (not PML on the first pass) |

## Solver (not in source)

| Item | Value |
| --- | --- |
| Solution type | Driven Modal |
| Setup frequency | 3.035 GHz (**SOURCE** operating frequency used as HFSS solution frequency) |
| Max / min passes | 15 / 4 |
| Min converged passes | 2 |
| MaxDeltaS | 0.02 |
| Refinement | 30% |
| Sweep | Interpolating 2.50–4.00 GHz, 151 points (10 MHz count) |
| Far field | Infinite Sphere, θ 0:5:180°, φ −180:10:180° |

A 10 MHz grid starting at 2.50 GHz does **not** land on 3.035 GHz. The adaptive
solution frequency is exactly 3.035 GHz; the interpolating sweep covers the span
and can be sampled at 3.035 GHz.

## What must not be claimed

- Do not call copper, 50 Ω, feed gap, or air-box size “per the source document”.
- Do not fill S11/gain/AR with closed-form estimates.
- Do not claim mesh convergence until HFSS reports it.
