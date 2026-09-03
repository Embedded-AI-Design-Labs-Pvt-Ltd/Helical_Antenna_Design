"""Load the existing modified-parameter demonstration dataset.

This is NOT an Ansys HFSS solve and NOT a VNA measurement.
Source: Helical Antenna_Modified_Parameter ready-made example
(examples/ready_made/helix_example_results.json from the sibling Antenna_Design
project, copied here for this HFSS workflow).

S11/VSWR come from the documented series-RLC example at 3.035 GHz.
Directivity/gain use the Kraus-based example sweep already stored with that file.
Mesh passes are an illustrative adaptive table for demonstration only.
"""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any

from common import (
    PROJECT_NAME,
    SETUP_NAME,
    SOURCE,
    SWEEP_NAME,
    now_iso,
    repo_root,
    write_json,
)

PROVENANCE = "DEMONSTRATION_EXAMPLE"
DEMO_STATUS = "DEMO"
EXAMPLE_MESSAGE = (
    "Demonstration dataset for the modified 3.035 GHz helical antenna. "
    "Not an Ansys HFSS finite-element solve. Replace by analyzing Setup1 in AEDT."
)

SIBLING_EXAMPLE = Path(r"E:\Sami\Antenna_Design\examples\ready_made\helix_example_results.json")


def example_dir() -> Path:
    path = repo_root() / "examples" / "ready_made"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _copy_existing_examples() -> Path:
    dest = example_dir() / "helix_example_results.json"
    src = SIBLING_EXAMPLE
    local_src = dest
    if src.is_file() and (not dest.is_file() or src.stat().st_mtime > dest.stat().st_mtime):
        shutil.copy2(src, dest)
        s1p = src.with_suffix(".s1p")
        csv_src = src.parent / "helix_example_sweep.csv"
        if s1p.is_file():
            shutil.copy2(s1p, dest.with_suffix(".s1p"))
        if csv_src.is_file():
            shutil.copy2(csv_src, dest.parent / "helix_example_sweep.csv")
    if not dest.is_file() and local_src.is_file():
        return local_src
    if not dest.is_file():
        raise FileNotFoundError(
            "Ready-made demonstration file not found. Expected "
            f"{dest} or {src}"
        )
    return dest


def _lerp(a: float | None, b: float | None, t: float) -> float | None:
    if a is None or b is None:
        return None
    return a + t * (b - a)


def interpolate_at_ghz(sweep: list[dict[str, Any]], f_ghz: float) -> dict[str, Any]:
    rows = []
    for row in sweep:
        f = row.get("frequency_GHz")
        if f is None and row.get("frequency_Hz") is not None:
            f = float(row["frequency_Hz"]) / 1e9
        if f is None:
            continue
        rows.append((float(f), row))
    rows.sort(key=lambda item: item[0])
    if not rows:
        return {}
    if f_ghz <= rows[0][0]:
        return dict(rows[0][1])
    if f_ghz >= rows[-1][0]:
        return dict(rows[-1][1])
    for (f1, a), (f2, b) in zip(rows, rows[1:]):
        if f1 <= f_ghz <= f2:
            t = 0.0 if f2 == f1 else (f_ghz - f1) / (f2 - f1)
            out = dict(a)
            for key in (
                "s11_dB",
                "vswr",
                "gain_dBi",
                "realized_gain_dBi",
                "directivity_dBi",
                "axial_ratio_dB",
                "efficiency_percent",
                "resistance_ohm",
                "reactance_ohm",
            ):
                out[key] = _lerp(a.get(key), b.get(key), t)
            out["frequency_GHz"] = f_ghz
            out["frequency_Hz"] = f_ghz * 1e9
            return out
    return dict(rows[0][1])


def demonstration_mesh_table() -> list[dict[str, Any]]:
    """Illustrative adaptive history for this helix size/frequency.

    Not exported from Ansys. Used only so MESH_CONVERGENCE.md and the dashboard
    have a complete demonstration. MaxDeltaS target in the project is 0.02.
    """
    return [
        {"pass": 1, "tetrahedra": 18420, "max_delta_s": 0.214, "s11_dB": -12.41, "converged": False},
        {"pass": 2, "tetrahedra": 26880, "max_delta_s": 0.097, "s11_dB": -16.88, "converged": False},
        {"pass": 3, "tetrahedra": 39210, "max_delta_s": 0.051, "s11_dB": -18.74, "converged": False},
        {"pass": 4, "tetrahedra": 54860, "max_delta_s": 0.027, "s11_dB": -19.61, "converged": False},
        {"pass": 5, "tetrahedra": 74200, "max_delta_s": 0.017, "s11_dB": -19.88, "converged": True},
        {"pass": 6, "tetrahedra": 89140, "max_delta_s": 0.012, "s11_dB": -19.92, "converged": True},
    ]


def _qty(name: str, value: float | None, unit: str) -> dict[str, Any]:
    return {
        "name": name,
        "value": value,
        "unit": unit,
        "status": "DEMO" if value is not None else "NOT_AVAILABLE",
        "provenance": PROVENANCE if value is not None else "NOT_SIMULATED",
        "notes": EXAMPLE_MESSAGE,
    }


def load_demonstration(*, make_active: bool = True) -> dict[str, Any]:
    path = _copy_existing_examples()
    raw = json.loads(path.read_text(encoding="utf-8"))
    sweep_in = raw.get("sweep") or []
    sweep = []
    for row in sweep_in:
        freq_hz = row.get("frequency_Hz")
        freq_ghz = freq_hz / 1e9 if freq_hz else row.get("frequency_GHz")
        sweep.append(
            {
                "frequency_GHz": freq_ghz,
                "s11_dB": row.get("s11_dB"),
                "vswr": row.get("vswr"),
                "gain_dB": row.get("gain_dBi") or row.get("gain_dB"),
                "realized_gain_dB": row.get("realized_gain_dBi") or row.get("realized_gain_dB"),
                "directivity_dBi": row.get("directivity_dBi"),
                "axial_ratio_dB": row.get("axial_ratio_dB"),
            }
        )
    f0 = SOURCE["operating_frequency_GHz"]
    at_f0 = interpolate_at_ghz(sweep_in, f0)
    s11 = at_f0.get("s11_dB", raw.get("s11_dB"))
    vswr = at_f0.get("vswr", raw.get("vswr"))
    gain = at_f0.get("gain_dBi", raw.get("gain_dBi") or raw.get("gain_dB"))
    direc = at_f0.get("directivity_dBi", raw.get("directivity_dBi"))
    ar = at_f0.get("axial_ratio_dB", raw.get("axial_ratio_dB"))
    rgain = at_f0.get("realized_gain_dBi", raw.get("realized_gain_dBi") or gain)
    eff = at_f0.get("efficiency_percent", raw.get("radiation_efficiency_percent"))
    if eff is not None and eff > 1.5:
        eff = eff / 100.0

    valid_s = [row for row in sweep if row.get("s11_dB") is not None]
    best = min(valid_s, key=lambda row: row["s11_dB"]) if valid_s else None
    mesh = demonstration_mesh_table()
    payload = {
        "meta": {
            "status": DEMO_STATUS,
            "project_name": PROJECT_NAME,
            "design_name": PROJECT_NAME,
            "setup_name": SETUP_NAME,
            "sweep_name": SWEEP_NAME,
            "far_field_setup": "Infinite Sphere1",
            "port_name": "P1",
            "timestamp_utc": now_iso(),
            "hfss_available": False,
            "solved": False,
            "demonstration": True,
            "source_document": "Helical Antenna_Modified_Parameter (1)(1).docx",
            "dataset": str(path),
            "company": "Embedded AI Design Labs Pvt Ltd",
            "author": "Muhammad Samiullah",
            "provenance": PROVENANCE,
        },
        "frequency_Hz": f0 * 1e9,
        "frequency_GHz": f0,
        "s11_dB": s11,
        "vswr": vswr,
        "gain_dB": gain,
        "realized_gain_dB": rgain,
        "directivity_dBi": direc,
        "axial_ratio_dB": ar,
        "radiation_efficiency": eff,
        "beam_direction": {"theta_deg": 0.0, "phi_deg": 0.0},
        "s11_at_3035MHz_dB": s11,
        "vswr_at_3035MHz": vswr,
        "min_s11_dB": None if best is None else best["s11_dB"],
        "min_s11_frequency_GHz": None if best is None else best["frequency_GHz"],
        "quantities": {
            "s11_dB": _qty("S11", s11, "dB"),
            "vswr": _qty("VSWR", vswr, "ratio"),
            "gain_dB": _qty("Gain", gain, "dB"),
            "realized_gain_dB": _qty("RealizedGain", rgain, "dB"),
            "directivity_dBi": _qty("Directivity", direc, "dBi"),
            "axial_ratio_dB": _qty("AxialRatio", ar, "dB"),
            "radiation_efficiency": _qty("RadiationEfficiency", eff, "ratio"),
            "peak_theta_deg": _qty("PeakTheta", 0.0, "deg"),
            "peak_phi_deg": _qty("PeakPhi", 0.0, "deg"),
            "resonant_frequency_GHz": _qty("ResonantFrequency", best["frequency_GHz"] if best else f0, "GHz"),
        },
        "sweep": sweep,
        "mesh_convergence": mesh,
        "warnings": [EXAMPLE_MESSAGE],
    }
    root = repo_root()
    from results_store import publish

    publish(payload, "demo", make_active=make_active)
    _write_mesh_csv(root / "results" / "demo" / "mesh_convergence.csv", mesh)
    if make_active:
        _write_mesh_csv(root / "results" / "csv" / "mesh_convergence.csv", mesh)
        _write_mesh_csv(root / "results" / "mesh_convergence.csv", mesh)
        _write_sweep_csv(root / "results" / "csv" / "s11.csv", sweep, "s11_dB")
        _write_sweep_csv(root / "results" / "s11.csv", sweep, "s11_dB")
        _write_sweep_csv(root / "results" / "csv" / "vswr.csv", sweep, "vswr")
        _write_sweep_csv(root / "results" / "vswr.csv", sweep, "vswr")
        _write_sweep_csv(root / "results" / "csv" / "axial_ratio.csv", sweep, "axial_ratio_dB")
        write_mesh_markdown(mesh, payload)
    return payload


def _write_mesh_csv(path: Path, mesh: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["pass", "tetrahedra", "max_delta_s", "s11_dB", "converged", "provenance"])
        w.writeheader()
        for row in mesh:
            w.writerow({**row, "provenance": PROVENANCE})


def _write_sweep_csv(path: Path, sweep: list[dict[str, Any]], field: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["frequency_GHz", field, "status", "provenance"])
        for row in sweep:
            w.writerow([row.get("frequency_GHz"), row.get(field), DEMO_STATUS, PROVENANCE])


def write_mesh_markdown(mesh: list[dict[str, Any]], payload: dict[str, Any]) -> None:
    last = mesh[-1]
    prev = mesh[-2]
    rows = "\n".join(
        f"| {r['pass']} | {r['tetrahedra']:,} | {r['max_delta_s']:.3f} | {r['s11_dB']:.2f} | "
        f"{'yes' if r['converged'] else 'no'} |"
        for r in mesh
    )
    md = f"""# Mesh Convergence

**Status: DEMO (demonstration dataset — not an Ansys HFSS export)**

Adaptive solution frequency: **{SOURCE['operating_frequency_GHz']} GHz** (modified helical antenna).

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
{rows}

- Last two-pass ΔS: {prev['max_delta_s']:.3f} → {last['max_delta_s']:.3f} (both ≤ 0.02 on passes 5–6)
- S11 change, last two passes: {prev['s11_dB']:.2f} → {last['s11_dB']:.2f} dB
- Demonstration S11 at 3.035 GHz: **{payload['s11_dB']:.2f} dB**
- CSV: `results/csv/mesh_convergence.csv`
- Provenance: `{PROVENANCE}`

Do not treat this table as a green check from Ansys until a real solution exists.
"""
    (repo_root() / "MESH_CONVERGENCE.md").write_text(md, encoding="utf-8")
    (repo_root() / "hfss" / "setup" / "MESH_CONVERGENCE.md").write_text(md, encoding="utf-8")


if __name__ == "__main__":
    out = load_demonstration()
    print(out["meta"]["status"], "S11", out["s11_dB"], "VSWR", out["vswr"])
