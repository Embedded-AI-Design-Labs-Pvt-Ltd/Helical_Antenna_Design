# 3.035 GHz Helical Antenna — HFSS Automation

Press **RUN**. The GUI builds the source-document helical antenna and opens it in **Ansys Electronics Desktop / HFSS** so you can inspect the 3D design.

## Quick start

1. Double-click `RUN.bat` (or `python helical_antenna_hfss/run_gui.py`).
2. Confirm the locked source parameters on the left.
3. Click **RUN — BUILD DESIGN & OPEN ANSYS HFSS**.
4. Electronics Desktop opens with HelixWire, GroundPlane, PortSheet and RadBox.
5. Inspect materials, lumped port P1, radiation boundary and Setup1.
6. Optionally check **Also solve in HFSS** (long). Until that finishes, all S11/VSWR/gain/AR values stay **NOT SIMULATED**.

If Ansys is not installed, RUN still generates geometry, IronPython scripts, HTML dashboard and reports. Results remain **NOT SIMULATED**. Theoretical estimates are never copied into HFSS result fields.

## What is locked (source document)

From `Helical Antenna_Modified_Parameter (1)(1).docx`:

| Item | Value |
| --- | --- |
| Frequency | 3.035 GHz |
| Turns | 3 |
| Helix radius | 20.94 mm |
| Pitch | 29.27 mm |
| Wire | 18 AWG, Ø 1.024 mm |
| Ground radius | 56.29 mm |

These values are not changed unless you explicitly request it.

## What is assumed (not in the source)

Feed gap, 50 Ω lumped port, copper, ground thickness, air-box size and solver controls. See `ENGINEERING_ASSUMPTIONS.md`.

## Project layout

See `PROJECT_ARCHITECTURE.md`.

## Manual HFSS path

Ansys Electronics Desktop → **Tools → Run Script** → `hfss/project/build_helix_hfss.py`

Keep the AEDT window open (the launcher uses `-RunScript`, not `-RunScriptAndExit`).

HTML documentation (written by `scripts/report_generator.py`):

- `docs/design.html` — antenna design theory, locked source parameters, RF targets
- `docs/implementation.html` — operator and developer procedure
- `docs/architecture.html` — system block diagram, data-flow and control-flow diagrams
- `docs/index.html` — dashboard

## Provenance

Every number is one of: `SOURCE_SPECIFICATION`, `CALCULATED`, `ENGINEERING_ASSUMPTION`, `HFSS_SIMULATED`, `USER_PROVIDED`, or `NOT_SIMULATED`.

---

**Embedded AI Design Labs Pvt Ltd**  
Author: Muhammad Samiullah · info@embedailabs.com · 9611748385  
[GitHub](https://github.com/Embedded-AI-Design-Labs-Pvt-Ltd) · [Website](https://www.embedailabs.com)  
© 2026 Embedded AI Design Labs Pvt Ltd. All rights reserved.
