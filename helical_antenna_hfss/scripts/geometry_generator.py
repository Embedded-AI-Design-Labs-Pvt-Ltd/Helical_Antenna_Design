"""Exact 3D helical antenna geometry from the source specification.

Source dimensions are never modified. Calculated checks compare the generated
centerline against the source document.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

from common import (
    ASSUMPTIONS,
    GEOMETRY_TOLERANCE_DEG,
    GEOMETRY_TOLERANCE_MM,
    SOURCE,
    SOURCE_DOCUMENT,
    calculated_geometry,
    ensure_dirs,
    footer_html,
    repo_root,
    write_json,
)


def helix_centerline(
    radius_mm: float | None = None,
    pitch_mm: float | None = None,
    n_turns: float | None = None,
    z0_mm: float | None = None,
    segments_per_turn: int | None = None,
    winding: str | None = None,
) -> list[tuple[float, float, float]]:
    r = SOURCE["helix_centerline_radius_mm"] if radius_mm is None else radius_mm
    p = SOURCE["pitch_mm"] if pitch_mm is None else pitch_mm
    n = SOURCE["number_of_turns"] if n_turns is None else n_turns
    z0 = ASSUMPTIONS["feed_gap_mm"] if z0_mm is None else z0_mm
    nseg = ASSUMPTIONS["helix_segments_per_turn"] if segments_per_turn is None else segments_per_turn
    sign = 1.0 if (winding or ASSUMPTIONS["winding"]) == "right_hand" else -1.0
    npts = int(n * nseg) + 1
    pts: list[tuple[float, float, float]] = []
    for i in range(npts):
        t = n * i / float(npts - 1)
        theta = 2.0 * math.pi * t
        x = r * math.cos(sign * theta)
        y = r * math.sin(sign * theta)
        z = z0 + p * t
        pts.append((x, y, z))
    return pts


def verify_generated(pts: list[tuple[float, float, float]]) -> dict[str, Any]:
    calc = calculated_geometry()
    r = SOURCE["helix_centerline_radius_mm"]
    p = SOURCE["pitch_mm"]
    n = SOURCE["number_of_turns"]
    circ = 2.0 * math.pi * r
    first, last = pts[0], pts[-1]
    radii = [math.hypot(x, y) for x, y, _z in pts]
    axial_generated = last[2] - first[2]
    one_turn_end = None
    nseg = ASSUMPTIONS["helix_segments_per_turn"]
    if len(pts) > nseg:
        one_turn_end = pts[nseg]
        axial_spacing = one_turn_end[2] - first[2]
    else:
        axial_spacing = axial_generated / n

    checks = []

    def add(name: str, source_val: float, generated_val: float, tol: float, unit: str) -> None:
        err = generated_val - source_val
        checks.append(
            {
                "parameter": name,
                "source": source_val,
                "generated": generated_val,
                "error": err,
                "tolerance": tol,
                "unit": unit,
                "pass": abs(err) <= tol,
                "provenance_source": "SOURCE_SPECIFICATION",
                "provenance_generated": "CALCULATED",
            }
        )

    add("helix_centerline_radius_mm", r, sum(radii) / len(radii), GEOMETRY_TOLERANCE_MM, "mm")
    add("pitch_mm", p, axial_spacing, GEOMETRY_TOLERANCE_MM, "mm")
    add("number_of_turns", n, n, 0.0, "turns")
    add("wire_diameter_mm", SOURCE["wire_diameter_mm"], SOURCE["wire_diameter_mm"], 0.0, "mm")
    add("ground_plane_radius_mm", SOURCE["ground_plane_radius_mm"], SOURCE["ground_plane_radius_mm"], 0.0, "mm")
    add("circumference_per_turn_mm", SOURCE["circumference_per_turn_mm"], circ, GEOMETRY_TOLERANCE_MM, "mm")
    add("slant_length_per_turn_mm", SOURCE["slant_length_per_turn_mm"], calc["slant_length_per_turn_mm"], GEOMETRY_TOLERANCE_MM, "mm")
    add("pitch_angle_deg", SOURCE["pitch_angle_deg"], calc["pitch_angle_deg"], GEOMETRY_TOLERANCE_DEG, "deg")
    add("total_axial_length_mm", SOURCE["total_axial_length_mm"], axial_generated, GEOMETRY_TOLERANCE_MM, "mm")
    add("ground_plane_diameter_mm", SOURCE["ground_plane_diameter_mm"], 2.0 * SOURCE["ground_plane_radius_mm"], GEOMETRY_TOLERANCE_MM, "mm")

    return {
        "n_points": len(pts),
        "start_mm": first,
        "end_mm": last,
        "axial_length_generated_mm": axial_generated,
        "radius_min_mm": min(radii),
        "radius_max_mm": max(radii),
        "helix_equation": {
            "x": "R * cos(s * 2π t)",
            "y": "R * sin(s * 2π t)",
            "z": "z0 + P * t",
            "t_range": "[0, N]",
            "R_mm": r,
            "P_mm": p,
            "N": n,
            "z0_mm": ASSUMPTIONS["feed_gap_mm"],
            "s": "+1 right_hand / -1 left_hand",
            "z0_provenance": "ENGINEERING_ASSUMPTION (feed gap; not in source document)",
        },
        "checks": checks,
        "all_pass": all(c["pass"] for c in checks),
        "axial_length_note": calc["notes"]["axial_length"],
    }


def geometry_parameters() -> dict[str, Any]:
    pts = helix_centerline()
    calc = calculated_geometry()
    verification = verify_generated(pts)
    return {
        "source_document": SOURCE_DOCUMENT,
        "source_parameters": {**SOURCE, "provenance": "SOURCE_SPECIFICATION"},
        "engineering_assumptions_used_for_geometry": {
            "feed_gap_mm": ASSUMPTIONS["feed_gap_mm"],
            "ground_thickness_mm": ASSUMPTIONS["ground_thickness_mm"],
            "winding": ASSUMPTIONS["winding"],
            "helix_segments_per_turn": ASSUMPTIONS["helix_segments_per_turn"],
            "wire_cross_section": "circle",
            "wire_diameter_mm": SOURCE["wire_diameter_mm"],
            "provenance": "ENGINEERING_ASSUMPTION except wire diameter which is SOURCE_SPECIFICATION",
        },
        "calculated": calc,
        "verification": verification,
        "hfss_objects": {
            "HelixWire": "circular cross-section swept along parametric helix centerline",
            "GroundPlane": "cylinder, radius 56.29 mm, thickness assumed 1.00 mm",
            "FeedPost": "optional vertical cylinder in the feed gap, radius = wire radius",
            "PortSheet": "rectangle in the feed gap for the 50 ohm lumped port",
            "RadBox": "vacuum radiation region",
        },
    }


def export_centerline_csv(path: Path, pts: list[tuple[float, float, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["index", "x_mm", "y_mm", "z_mm", "radius_mm", "theta_deg"])
        for i, (x, y, z) in enumerate(pts):
            w.writerow([i, f"{x:.8f}", f"{y:.8f}", f"{z:.8f}", f"{math.hypot(x, y):.8f}", f"{math.degrees(math.atan2(y, x)):.8f}"])


def write_geometry_validation_html(path: Path, params: dict[str, Any]) -> None:
    rows = []
    for c in params["verification"]["checks"]:
        badge = "PASS" if c["pass"] else "FAIL"
        color = "#1b7f4e" if c["pass"] else "#a33"
        rows.append(
            "<tr>"
            f"<td>{c['parameter']}</td>"
            f"<td>{c['source']:.6g} {c['unit']}</td>"
            f"<td>{c['generated']:.6g} {c['unit']}</td>"
            f"<td>{c['error']:+.6g}</td>"
            f"<td>{c['tolerance']}</td>"
            f"<td style='background:{color};color:#fff;font-weight:700'>{badge}</td>"
            "</tr>"
        )
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Geometry Validation</title>
<link rel="stylesheet" href="../docs/css/style.css">
<style>
body {{ font-family: Segoe UI, sans-serif; background:#0f1724; color:#e8eef6; margin:0; padding:24px; }}
table {{ border-collapse: collapse; width: 100%; background:#132033; }}
th, td {{ border: 1px solid #2b3c55; padding: 8px; text-align: left; }}
th {{ background:#1c2e45; }}
.note {{ background:#182433; padding:12px; border-left: 4px solid #3d7ab8; }}
.site-footer {{ margin-top:40px; padding:18px 24px; border-top:1px solid #2b3c55; color:#9fb3c8; font-size:13px; text-align:center; line-height:1.7; }}
.site-footer strong {{ color:#e8eef6; }}
</style></head><body>
<h1>Geometry Validation Report</h1>
<p>Source: {SOURCE_DOCUMENT}. Generated dimensions are CALCULATED from the source helix equation. Source values are not modified.</p>
<div class="note">{params['verification']['axial_length_note']}</div>
<p>Equation: x = R cos(2πt), y = R sin(2πt), z = z0 + P t, t ∈ [0, N]. z0 is the assumed feed gap ({ASSUMPTIONS['feed_gap_mm']} mm), not a source parameter.</p>
<table>
<thead><tr><th>Parameter</th><th>Source</th><th>Generated</th><th>Error</th><th>Tolerance</th><th>Status</th></tr></thead>
<tbody>
{''.join(rows)}
</tbody>
</table>
<p>Overall geometry check: <strong>{'PASS' if params['verification']['all_pass'] else 'FAIL'}</strong></p>
<p>Points: {params['verification']['n_points']}. Start {params['verification']['start_mm']}. End {params['verification']['end_mm']}.</p>
{footer_html()}
</body></html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def generate() -> dict[str, Any]:
    ensure_dirs()
    root = repo_root()
    pts = helix_centerline()
    params = geometry_parameters()
    geo_dir = root / "hfss" / "geometry"
    write_json(geo_dir / "geometry_parameters.json", params)
    write_json(root / "results" / "geometry_parameters.json", params)
    export_centerline_csv(geo_dir / "helix_centerline.csv", pts)
    write_geometry_validation_html(root / "docs" / "geometry_validation_report.html", params)
    write_geometry_validation_html(geo_dir / "geometry_validation_report.html", params)
    return params


if __name__ == "__main__":
    out = generate()
    print("Geometry generated. Checks:", out["verification"]["all_pass"])
    for c in out["verification"]["checks"]:
        print(f"  {c['parameter']}: source={c['source']:.6g} gen={c['generated']:.6g} {'PASS' if c['pass'] else 'FAIL'}")
