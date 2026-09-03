# Project Architecture

## Purpose

Repeatable Ansys HFSS workflow for the 3.035 GHz 3-turn helical antenna specified in
`Helical Antenna_Modified_Parameter (1)(1).docx`, with a one-button GUI, geometry generation,
HFSS model build, result extraction, validation, dashboard and engineering report.

## Folder structure

```
helical_antenna_hfss/
├── RUN.bat
├── run_gui.py
├── README.md
├── PROJECT_REQUIREMENTS.md
├── SOURCE_PARAMETERS.md
├── ENGINEERING_ASSUMPTIONS.md
├── VALIDATION_PLAN.md
├── PROJECT_ARCHITECTURE.md
├── PORT_VALIDATION.md
├── BOUNDARY_VALIDATION.md
├── SOLVER_CONFIGURATION.md
├── MESH_CONVERGENCE.md
├── gui/app.py
├── hfss/project|geometry|setup|boundaries|ports|results
├── scripts/   (geometry, port, materials, radiation, solver, extract, validate, report, workflow)
├── results/   (plots, csv, screenshots, reports)
├── docs/      (HTML dashboard, design, implementation, architecture)
├── reports/
└── tests/
```

## Dependencies

Required for GUI and documentation:

- Python 3.10+
- numpy, matplotlib, tkinter (stdlib)

Required to **show and solve** the design in Ansys:

- Ansys Electronics Desktop with HFSS
- Optional: `pyaedt` or `ansys-aedt-core`

Ansys is **not** bundled. If it is missing, the workflow still completes offline.

## Execution workflow

1. Operator launches `RUN.bat` / `run_gui.py`.
2. GUI displays source parameters and a calculated 3D preview.
3. RUN executes `scripts/workflow.py`:
   - generate & validate geometry
   - write materials / port / radiation / solver JSON
   - write IronPython `hfss/project/build_helix_hfss.py`
   - launch AEDT graphically (PyAEDT if available, else `ansysedt -RunScript`)
   - extract results if a solution exists; otherwise write NOT SIMULATED
   - validate, plot, dashboard, report, QA
4. Browser opens `docs/index.html`.

## What must run inside Ansys Electronics Desktop

These cannot be faked in Python:

- 3D Modeler boolean/material/boundary assignments as solved by HFSS
- Adaptive mesh and Setup1 convergence
- Frequency sweep S-parameters
- Far-field gain, directivity, axial ratio, 2D/3D patterns

Python **can** generate the identical geometry and the AEDT script that performs those assignments.

## Separation of data

| Class | Examples | Where stored |
| --- | --- | --- |
| Source requirements | R, pitch, N, wire, ground, frequency, performance targets | `SOURCE_PARAMETERS.md`, `scripts/common.py` SOURCE/TARGETS |
| Engineering assumptions | feed gap, 50 Ω lumped port, copper, air box, MaxDeltaS | `ENGINEERING_ASSUMPTIONS.md`, ASSUMPTIONS |
| Calculated values | C = 2πR, α = atan(P/C), λ0 = c/f, N·P | `geometry_parameters.json` calculated |
| HFSS simulated values | S11, VSWR, gain, directivity, AR | `results/hfss_results.json` only after a real solve |

## GUI vs scripts

- **GUI**: operator surface. One RUN button.
- **scripts/workflow.py**: integration agent (phases 1–23).
- **scripts/simulation_runner.py**: PyAEDT / ansysedt launch.
- **docs/**: HTML dashboard and design/implementation/architecture pages (Mermaid block, data-flow and control-flow diagrams).
