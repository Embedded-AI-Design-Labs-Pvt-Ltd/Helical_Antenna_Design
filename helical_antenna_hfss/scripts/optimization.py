"""Parametric optimization framework.

Does NOT modify the source nominal design automatically.
No fabricated electromagnetic results.
"""

from __future__ import annotations

import csv
import itertools
from pathlib import Path
from typing import Any

from common import ASSUMPTIONS, SOURCE, footer_html, repo_root, write_json


NOMINAL = {
    "label": "SOURCE_NOMINAL_DESIGN",
    "helix_radius_mm": SOURCE["helix_centerline_radius_mm"],
    "pitch_mm": SOURCE["pitch_mm"],
    "wire_diameter_mm": SOURCE["wire_diameter_mm"],
    "ground_radius_mm": SOURCE["ground_plane_radius_mm"],
    "feed_gap_mm": ASSUMPTIONS["feed_gap_mm"],
    "feed_position_mm": SOURCE["helix_centerline_radius_mm"],
    "s11_dB": None,
    "vswr": None,
    "gain_dB": None,
    "directivity_dBi": None,
    "axial_ratio_dB": None,
    "status": "NOT SIMULATED",
    "provenance": "SOURCE_SPECIFICATION for geometry; ENGINEERING_ASSUMPTION for feed_gap; electromagnetic columns NOT_SIMULATED",
}


def candidate_grid() -> list[dict[str, Any]]:
    """Relative perturbations around the source design. Geometry only until HFSS solves."""
    radius_scale = [1.0]
    pitch_scale = [1.0]
    # Keep default grid as nominal-only so the source design is not auto-modified.
    # Broader grids are available via build_grid(enabled=True).
    rows = []
    for rs, ps in itertools.product(radius_scale, pitch_scale):
        row = dict(NOMINAL)
        row["helix_radius_mm"] = SOURCE["helix_centerline_radius_mm"] * rs
        row["pitch_mm"] = SOURCE["pitch_mm"] * ps
        row["label"] = "SOURCE_NOMINAL_DESIGN" if rs == 1.0 and ps == 1.0 else "CANDIDATE"
        rows.append(row)
    return rows


def build_grid(*, expand: bool = False) -> list[dict[str, Any]]:
    if not expand:
        return candidate_grid()
    radii = [0.98, 1.00, 1.02]
    pitches = [0.98, 1.00, 1.02]
    gaps = [1.0, 1.5, 2.0]
    rows = []
    for rs, ps, gap in itertools.product(radii, pitches, gaps):
        row = dict(NOMINAL)
        row["helix_radius_mm"] = round(SOURCE["helix_centerline_radius_mm"] * rs, 4)
        row["pitch_mm"] = round(SOURCE["pitch_mm"] * ps, 4)
        row["feed_gap_mm"] = gap
        row["label"] = (
            "SOURCE_NOMINAL_DESIGN"
            if abs(rs - 1) < 1e-12 and abs(ps - 1) < 1e-12 and abs(gap - ASSUMPTIONS["feed_gap_mm"]) < 1e-12
            else "CANDIDATE_NOT_SOLVED"
        )
        row["s11_dB"] = None
        row["status"] = "NOT SIMULATED"
        rows.append(row)
    return rows


def generate(*, expand: bool = False) -> dict[str, Any]:
    rows = build_grid(expand=expand)
    root = repo_root()
    csv_path = root / "results" / "csv" / "optimization_results.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "label",
        "helix_radius_mm",
        "pitch_mm",
        "wire_diameter_mm",
        "ground_radius_mm",
        "feed_gap_mm",
        "feed_position_mm",
        "s11_dB",
        "vswr",
        "gain_dB",
        "directivity_dBi",
        "axial_ratio_dB",
        "status",
        "provenance",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})
    (root / "results" / "optimization_results.csv").write_text(csv_path.read_text(encoding="utf-8"), encoding="utf-8")
    report = {
        "source_nominal_design": NOMINAL,
        "optimized_design": None,
        "optimized_design_note": "No optimized design exists until HFSS parametric solves complete. The source nominal geometry is never overwritten automatically.",
        "objective": {
            "primary": "S11 at 3.035 GHz",
            "secondary": "VSWR",
            "additional": ["Gain", "Directivity", "Axial ratio"],
        },
        "variables": ["helix_radius", "pitch", "wire_diameter", "ground_radius", "feed_gap", "feed_position"],
        "candidates": rows,
        "n_candidates": len(rows),
        "n_solved": 0,
    }
    write_json(root / "results" / "optimization_results.json", report)
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Optimization Report</title>
<style>
body {{ font-family: Segoe UI, sans-serif; background:#0f1724; color:#e8eef6; padding:24px; }}
.card {{ background:#132033; padding:16px; border:1px solid #2b3c55; margin:12px 0; }}
.nominal {{ border-left:4px solid #3d7ab8; }}
.warn {{ color:#e6b450; }}
.site-footer {{ margin-top:40px; padding:18px 24px; border-top:1px solid #2b3c55; color:#9fb3c8; font-size:13px; text-align:center; line-height:1.7; }}
.site-footer strong {{ color:#e8eef6; }}
</style></head><body>
<h1>Parametric Optimization Framework</h1>
<div class="card nominal">
<h2>SOURCE NOMINAL DESIGN</h2>
<p>R = {SOURCE['helix_centerline_radius_mm']} mm, pitch = {SOURCE['pitch_mm']} mm, N = {SOURCE['number_of_turns']},
wire Ø = {SOURCE['wire_diameter_mm']} mm, ground R = {SOURCE['ground_plane_radius_mm']} mm.</p>
<p>This geometry is the baseline. Automation will not replace it with an "optimized" geometry unless you explicitly run a solved parametric sweep and accept a candidate.</p>
</div>
<div class="card">
<h2>OPTIMIZED DESIGN</h2>
<p class="warn">NOT SIMULATED — no candidate has HFSS results. There is no optimized design.</p>
</div>
<p>Objectives: primary S11 @ 3.035 GHz; secondary VSWR; additional gain, directivity, axial ratio.</p>
<p>Candidates written: {len(rows)}. Solved: 0.</p>
<p>CSV: results/csv/optimization_results.csv</p>
{footer_html()}
</body></html>
"""
    (root / "docs" / "optimization_report.html").write_text(html, encoding="utf-8")
    (root / "results" / "reports" / "optimization_report.html").write_text(html, encoding="utf-8")
    return report


if __name__ == "__main__":
    print(generate()["n_candidates"], "candidates; solved 0")
