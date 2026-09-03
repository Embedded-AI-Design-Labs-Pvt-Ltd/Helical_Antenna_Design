"""HTML dashboard, GUI procedure, engineering report, and supporting pages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from common import (
    ASSUMPTIONS,
    AUTHOR_EMAIL,
    AUTHOR_NAME,
    AUTHOR_PHONE,
    COMPANY_NAME,
    COPYRIGHT_YEAR,
    DESIGN_NAME,
    GITHUB_ORG_URL,
    PRODUCT_TITLE,
    PROJECT_NAME,
    SOURCE,
    SOURCE_DOCUMENT,
    TARGETS,
    airbox_mm,
    calculated_geometry,
    footer_html,
    now_iso,
    repo_root,
    wavelength_mm,
)
from html_design_docs import architecture_page, design_page, implementation_page

NAV = [
    ("index.html", "Dashboard"),
    ("design.html", "Design"),
    ("implementation.html", "Implementation"),
    ("architecture.html", "Architecture"),
    ("geometry.html", "Geometry"),
    ("simulation.html", "Simulation"),
    ("s11.html", "S11"),
    ("vswr.html", "VSWR"),
    ("gain.html", "Gain"),
    ("directivity.html", "Directivity"),
    ("axial_ratio.html", "Axial Ratio"),
    ("far_field.html", "Radiation"),
    ("feed_and_port.html", "Feed/Port"),
    ("HFSS_GUI_STEP_BY_STEP.html", "HFSS GUI"),
    ("validation.html", "Validation"),
]


def css_text() -> str:
    return """
:root { --bg:#0b1220; --panel:#132033; --line:#2b3c55; --text:#e8eef6; --muted:#9fb3c8; --acc:#3d9be9; --ok:#1b7f4e; --warn:#6b5a2e; --bad:#8a3030; }
* { box-sizing: border-box; }
html, body { margin:0; padding:0; background:var(--bg); color:var(--text); font-family:"Segoe UI",sans-serif; }
a { color:var(--acc); }
header { background:#0f1b2d; border-bottom:1px solid var(--line); padding:16px 24px; }
header h1 { margin:0; font-size:22px; letter-spacing:.04em; }
header .sub { color:var(--muted); font-size:13px; margin-top:4px; }
nav { display:flex; flex-wrap:wrap; gap:8px; padding:10px 24px; background:#101a28; border-bottom:1px solid var(--line); }
nav a { text-decoration:none; padding:6px 10px; border:1px solid var(--line); border-radius:4px; color:var(--text); font-size:13px; }
nav a.active, nav a:hover { background:#1f4e79; }
main { padding:24px; max-width:1280px; margin:0 auto; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:14px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:14px; }
.card h2, .card h3 { margin-top:0; }
.k { color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.06em; }
.v { font-size:28px; font-weight:700; margin:6px 0; }
.badge { display:inline-block; padding:4px 8px; border-radius:4px; font-weight:700; font-size:12px; }
.ns { background:var(--warn); color:#fff; }
.ok { background:var(--ok); color:#fff; }
.bad { background:var(--bad); color:#fff; }
.src { background:#1f4e79; color:#fff; }
table { width:100%; border-collapse:collapse; background:var(--panel); }
th, td { border:1px solid var(--line); padding:8px; text-align:left; vertical-align:top; }
th { background:#1c2e45; }
img { max-width:100%; border:1px solid var(--line); background:#0a1018; }
footer, .site-footer { margin-top:40px; padding:18px 24px; border-top:1px solid var(--line); color:var(--muted); font-size:13px; text-align:center; line-height:1.7; background:#0b1220; }
.site-footer strong { color:var(--text); }
.footer-note { margin-top:6px; font-size:12px; }
.note { border-left:4px solid var(--acc); background:#182433; padding:10px 12px; }
pre { background:#0a1018; padding:12px; overflow:auto; border:1px solid var(--line); }
.toc { margin:16px 0; }
.toc a { display:inline-block; margin:4px 10px 4px 0; }
.diagram { background:#0a1018; border:1px solid var(--line); border-radius:8px; padding:16px; margin:16px 0; overflow-x:auto; }
.diagram-caption { color:var(--muted); font-size:13px; margin-top:-8px; margin-bottom:20px; }
ol.steps li { margin:8px 0; line-height:1.6; }
h3 { color:#c5d8ee; }
@media (max-width:700px) { .v { font-size:22px; } header h1 { font-size:18px; } }
"""


def wrap(title: str, body: str, active: str, *, mermaid: bool = False) -> str:
    links = []
    for href, label in NAV:
        cls = "active" if href == active else ""
        links.append(f'<a class="{cls}" href="{href}">{label}</a>')
    mermaid_tags = ""
    if mermaid:
        mermaid_tags = """
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>
document.addEventListener("DOMContentLoaded", function () {
  if (window.mermaid) {
    mermaid.initialize({ startOnLoad: true, theme: "dark", securityLevel: "loose" });
  }
});
</script>
"""
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="css/style.css">
{mermaid_tags}
</head><body>
<header>
  <h1>{PRODUCT_TITLE}</h1>
  <div class="sub">{COMPANY_NAME} · Author: {AUTHOR_NAME} · {AUTHOR_EMAIL} · {AUTHOR_PHONE} · <a href="{GITHUB_ORG_URL}">{GITHUB_ORG_URL}</a></div>
</header>
<nav>{''.join(links)}</nav>
<main>
{body}
</main>
{footer_html(extra="Numerical HFSS values are shown only when extracted from a solved project. Otherwise status is NOT SIMULATED.")}
</body></html>
"""


def val_box(label: str, actual: Any, target: str, status: str) -> str:
    shown = "NOT SIMULATED" if actual is None else actual
    badge = "ns" if status in ("NOT SIMULATED", "NOT_AVAILABLE") else ("ok" if status in ("PASS", "DEMO", "DEMO PASS") else ("src" if status == "SOURCE" else "bad"))
    return f"""<div class="card">
<div class="k">{label}</div>
<div class="v">{shown}</div>
<div>Target: {target}</div>
<div class="badge {badge}">{status}</div>
</div>"""


def load_results() -> dict[str, Any]:
    path = repo_root() / "results" / "hfss_results.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def load_matrix() -> dict[str, Any]:
    path = repo_root() / "results" / "acceptance_matrix.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"overall_status": "NOT SIMULATED", "rows": []}


def img(rel: str, alt: str) -> str:
    return f'<p><img src="{rel}" alt="{alt}"></p>'


def dashboard_body(results: dict[str, Any], matrix: dict[str, Any]) -> str:
    meta = results.get("meta") or {}
    overall = matrix.get("overall_status", "NOT SIMULATED")
    calc = calculated_geometry()
    try:
        from results_store import active_source, load_demo, load_live

        demo_data = load_demo() or {}
        live_data = load_live() or {}
        active = active_source()
    except Exception:
        demo_data, live_data, active = {}, {}, "demo"

    def _fmt(store: dict, key: str, unit: str = "") -> str:
        val = store.get(key)
        if val is None:
            return "NOT SIMULATED"
        return f"{val:.3g} {unit}".strip()

    compare_rows = "".join(
        f"<tr><td>{name}</td><td>{tgt}</td><td>{_fmt(demo_data, key, unit)}</td><td>{_fmt(live_data, key, unit)}</td></tr>"
        for name, tgt, key, unit in (
            ("S11", "≤ -15 dB", "s11_dB", "dB"),
            ("VSWR", "1.1–1.4", "vswr", ""),
            ("Gain", "9.5–14.0 dB", "gain_dB", "dB"),
            ("Directivity", "10.0–14.5 dBi", "directivity_dBi", "dBi"),
            ("Axial ratio", "< 1.5 dB", "axial_ratio_dB", "dB"),
        )
    )
    def _st(val: Any) -> str:
        if val is None:
            return "NOT SIMULATED"
        if (results.get("meta") or {}).get("demonstration"):
            return "DEMO"
        return "SEE VALIDATION"

    boxes = [
        val_box("Frequency", f"{SOURCE['operating_frequency_GHz']} GHz", "3.035 GHz", "SOURCE"),
        val_box("S11", results.get("s11_dB"), "<= -15 dB", _st(results.get("s11_dB"))),
        val_box("VSWR", results.get("vswr"), "1.1:1 – 1.4:1", _st(results.get("vswr"))),
        val_box("Gain", results.get("gain_dB"), "9.5 – 14.0 dB", _st(results.get("gain_dB"))),
        val_box("Directivity", results.get("directivity_dBi"), "10.0 – 14.5 dBi", _st(results.get("directivity_dBi"))),
        val_box("Axial ratio", results.get("axial_ratio_dB"), "< 1.5 dB (main beam)", _st(results.get("axial_ratio_dB"))),
    ]
    rows = "".join(
        f"<tr><td>{r.get('parameter')}</td><td>{r.get('requirement')}</td><td>{r.get('hfss_result')}</td><td>{r.get('margin')}</td><td>{r.get('status')}</td></tr>"
        for r in matrix.get("rows", [])
    )
    return f"""
<p class="badge ns" style="font-size:16px">PROJECT STATUS: {overall} · Active view: {active.upper()}</p>
<div class="grid">{''.join(boxes)}</div>
<div class="card" style="margin-top:16px">
<h2>Project Overview</h2>
<p>Use the GUI buttons: <strong>Demonstrate</strong> loads existing modified-antenna data;
<strong>Test in HFSS</strong> builds the live Ansys model. Both stores are kept.</p>
<p>Design documentation:
<a href="design.html">antenna design</a> ·
<a href="implementation.html">implementation procedure</a> ·
<a href="architecture.html">system block, data-flow and control-flow diagrams</a>.</p>
<ul>
<li>Project: {PROJECT_NAME} / Design: {DESIGN_NAME}</li>
<li>HFSS available: {meta.get('hfss_available')}</li>
<li>Solved: {meta.get('solved')}</li>
<li>Setup: {meta.get('setup_name')} · Sweep: {meta.get('sweep_name')} · Far-field: {meta.get('far_field_setup')}</li>
<li>Timestamp (UTC): {meta.get('timestamp_utc') or now_iso()}</li>
</ul>
</div>
<div class="grid" style="margin-top:16px">
<div class="card"><h3>Antenna Parameters (SOURCE)</h3>
<table>
<tr><th>Item</th><th>Value</th></tr>
<tr><td>Turns</td><td>{SOURCE['number_of_turns']}</td></tr>
<tr><td>Radius</td><td>{SOURCE['helix_centerline_radius_mm']} mm</td></tr>
<tr><td>Pitch</td><td>{SOURCE['pitch_mm']} mm</td></tr>
<tr><td>Wire</td><td>18 AWG · Ø {SOURCE['wire_diameter_mm']} mm</td></tr>
<tr><td>Ground radius</td><td>{SOURCE['ground_plane_radius_mm']} mm</td></tr>
<tr><td>Axial length (source)</td><td>{SOURCE['total_axial_length_mm']} mm</td></tr>
</table></div>
<div class="card"><h3>Calculated (not HFSS)</h3>
<table>
<tr><th>Item</th><th>Value</th></tr>
<tr><td>C/turn</td><td>{calc['circumference_per_turn_mm']:.4f} mm</td></tr>
<tr><td>Slant/turn</td><td>{calc['slant_length_per_turn_mm']:.4f} mm</td></tr>
<tr><td>Pitch angle</td><td>{calc['pitch_angle_deg']:.4f}°</td></tr>
<tr><td>N·pitch</td><td>{calc['total_axial_length_mm']:.4f} mm</td></tr>
<tr><td>λ0</td><td>{calc['wavelength_mm']:.4f} mm</td></tr>
<tr><td>C/λ</td><td>{calc['circumference_over_wavelength']:.4f}</td></tr>
</table></div>
</div>
<div class="card" style="margin-top:16px"><h2>3D Geometry</h2>
{img('../results/plots/geometry_3d.png', 'Helical antenna geometry')}
</div>
<div class="card"><h2>S11 / VSWR / Patterns</h2>
<p class="note">If status is DEMO, plots come from the existing modified-parameter ready-made dataset — not from Ansys HFSS.</p>
<div class="grid">
<div>{img('../results/plots/S11.png', 'S11')}</div>
<div>{img('../results/plots/VSWR.png', 'VSWR')}</div>
<div>{img('../results/plots/Gain_Pattern.png', 'Gain')}</div>
<div>{img('../results/plots/Axial_Ratio.png', 'Axial ratio')}</div>
<div>{img('../results/plots/mesh_convergence.png', 'Mesh convergence')}</div>
<div>{img('../results/plots/3D_Radiation_Pattern.png', '3D pattern')}</div>
</div></div>
<div class="card"><h2>Demo vs live HFSS</h2>
<p>Demonstration data stays in <code>results/demo/</code>. Live Ansys extracts stay in <code>results/live/</code>.</p>
<table>
<thead><tr><th>Parameter</th><th>Target</th><th>Demo (existing)</th><th>Live HFSS</th></tr></thead>
<tbody>{compare_rows}</tbody>
</table>
</div>
<div class="card"><h2>Requirements (active view)</h2>
<table><thead><tr><th>Parameter</th><th>Requirement</th><th>HFSS Result</th><th>Margin</th><th>Status</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<div class="card"><h2>Assumptions</h2>
<p>Feed, materials, air box and solver controls are <strong>not</strong> in the source document. See <a href="../ENGINEERING_ASSUMPTIONS.md">ENGINEERING_ASSUMPTIONS.md</a>
and <a href="feed_and_port.html">feed_and_port.html</a>.</p>
<p>Feed: {ASSUMPTIONS['feed_type']}, gap {ASSUMPTIONS['feed_gap_mm']} mm, Z0 {ASSUMPTIONS['port_impedance_ohm']} Ω, copper conductors, radiation box 0.5 λ0.</p>
</div>
<div class="card"><h2>Files</h2>
<ul>
<li><a href="../results/hfss_results.json">hfss_results.json</a></li>
<li><a href="../results/acceptance_matrix.csv">acceptance_matrix.csv</a></li>
<li><a href="../reports/Helical_Antenna_HFSS_Report.html">Engineering report</a></li>
<li><a href="../hfss/project/build_helix_hfss.py">HFSS IronPython build script</a></li>
</ul></div>
<script>
const embedded = {json.dumps(results)};
console.log('HFSS results payload', embedded);
</script>
"""


def geometry_page() -> str:
    calc = calculated_geometry()
    box = airbox_mm()
    return f"""
<h2>Antenna Geometry</h2>
<p>Parametric helix: <code>x = R cos(2πt)</code>, <code>y = R sin(2πt)</code>, <code>z = z0 + P t</code>, <code>t ∈ [0, N]</code>.</p>
<p class="note">z0 = {ASSUMPTIONS['feed_gap_mm']} mm is an ENGINEERING ASSUMPTION (feed gap). R, P, N, wire and ground radii are SOURCE_SPECIFICATION.</p>
{img('../results/plots/geometry_3d.png', 'geometry')}
<table>
<tr><th>Quantity</th><th>Source</th><th>Calculated</th><th>Provenance</th></tr>
<tr><td>Radius</td><td>{SOURCE['helix_centerline_radius_mm']} mm</td><td>{SOURCE['helix_centerline_radius_mm']} mm</td><td>SOURCE_SPECIFICATION</td></tr>
<tr><td>Circumference/turn</td><td>{SOURCE['circumference_per_turn_mm']} mm</td><td>{calc['circumference_per_turn_mm']:.4f} mm</td><td>CALCULATED vs SOURCE</td></tr>
<tr><td>Pitch</td><td>{SOURCE['pitch_mm']} mm</td><td>{SOURCE['pitch_mm']} mm</td><td>SOURCE_SPECIFICATION</td></tr>
<tr><td>Slant/turn</td><td>{SOURCE['slant_length_per_turn_mm']} mm</td><td>{calc['slant_length_per_turn_mm']:.4f} mm</td><td>CALCULATED vs SOURCE</td></tr>
<tr><td>Pitch angle</td><td>{SOURCE['pitch_angle_deg']}°</td><td>{calc['pitch_angle_deg']:.4f}°</td><td>CALCULATED vs SOURCE</td></tr>
<tr><td>Axial length</td><td>{SOURCE['total_axial_length_mm']} mm</td><td>{calc['total_axial_length_mm']:.4f} mm</td><td>N·P = 87.81 mm; source 87.82 mm rounding</td></tr>
<tr><td>Wire Ø</td><td>{SOURCE['wire_diameter_mm']} mm</td><td>—</td><td>SOURCE_SPECIFICATION</td></tr>
<tr><td>Ground radius</td><td>{SOURCE['ground_plane_radius_mm']} mm</td><td>—</td><td>SOURCE_SPECIFICATION</td></tr>
<tr><td>Air box padding</td><td>—</td><td>{box['padding_mm']:.3f} mm (0.5 λ0)</td><td>ENGINEERING_ASSUMPTION</td></tr>
</table>
<p><a href="geometry_validation_report.html">Geometry validation report</a></p>
"""


def metric_page(name: str, plot: str, requirement: str, actual: Any, extra: str = "") -> str:
    shown = "NOT SIMULATED" if actual is None else actual
    return f"""
<h2>{name}</h2>
<p class="note">Requirement: {requirement}. Actual HFSS value: <strong>{shown}</strong>.
Theoretical estimates are not substituted for HFSS data.</p>
{img(plot, name)}
{extra}
"""


def gui_steps_page() -> str:
    steps = [
        ("New HFSS project", "File > New > Project", "New Project", "Project name Helix_3035MHz", "Project appears in Project Manager", "Project Manager lists the new project"),
        ("Insert HFSS Design", "Project > Insert HFSS Design", "Insert HFSS Design", "Solution type Driven Modal; name Helix_3035MHz", "HFSS design is active", "3D Modeler tab is available"),
        ("Set model units", "Modeler > Units", "Set Model Units", "mm, Rescale = false", "Status bar shows mm", "Create a 1 mm box and measure"),
        ("Create ground plane", "Draw > Cylinder", "Cylinder", "Axis Z, Center (0,0,-1mm), Radius 56.29 mm, Height 1 mm (height is assumed)", "Disk under the helix", "Radius dimension = 56.29 mm"),
        ("Create helix centerline", "Draw > Line / Polyline, or Draw > Helix if available", "Polyline / Helix", "R=20.94 mm, pitch=29.27 mm, turns=3, start z=1.50 mm (assumed gap)", "3-turn space curve", "End z − start z ≈ 87.81 mm"),
        ("Create wire profile", "Select polyline > Properties > Cross Section", "Polyline XSection", "Circle, width 1.024 mm, 8 segments", "Tube along helix", "Diameter 1.024 mm"),
        ("Sweep wire", "Already applied via polyline cross-section (or Draw > Sweep Along Path)", "Sweep", "Profile = circle Ø1.024 mm along helix", "Solid helix wire", "No self-intersection at this pitch"),
        ("Create feed structure", "Draw > Cylinder and Draw > Rectangle", "Cylinder + Rectangle", "Feed post at (20.94,0,0), height 1.50 mm; PortSheet width 1.024 mm, height 1.50 mm in XZ", "Gap between helix and ground", "Post does not short through the ground"),
        ("Assign PEC/conductor", "HFSS > Assign Material, or Properties > Material", "Material", "copper for HelixWire, GroundPlane, FeedPost (ASSUMPTION; not in source). PEC is optional and also an assumption.", "Objects show copper", "Solve Inside = false for metals"),
        ("Create air region", "Draw > Box", "Box", f"Origin and size from 0.5 λ0 padding (λ0={wavelength_mm():.3f} mm)", "Box encloses antenna", "All metal objects inside the box"),
        ("Assign radiation boundary", "HFSS > Boundaries > Assign > Radiation", "Radiation", "Object RadBox, name Rad1", "Boundary Rad1 listed", "RadBox faces are radiation, not PEC"),
        ("Create lumped port", "HFSS > Excitations > Assign > Lumped Port", "Lumped Port", "Object PortSheet, 50 ohm, integration line from (20.94,0,0) to (20.94,0,1.50) mm", "Excitation P1", "Port is inside RadBox"),
        ("Create solution setup", "HFSS > Analysis Setup > Add Solution Setup", "Solution Setup", "Frequency 3.035 GHz, MaxPasses 15, MinPasses 4, MinConverged 2, MaxDeltaS 0.02", "Setup1 exists", "Solution frequency is exactly 3.035 GHz"),
        ("Create frequency sweep", "HFSS > Analysis Setup > Add Frequency Sweep", "Frequency Sweep", "Interpolating, 2.50 to 4.00 GHz, 151 points (10 MHz count), Save radiated fields", "Sweep under Setup1", "3.035 GHz is inside the span; adaptive frequency is exact"),
        ("Create far-field setup", "HFSS > Radiation > Insert Far Field Setup > Infinite Sphere", "Infinite Sphere", "Theta 0:5:180, Phi -180:10:180", "Infinite Sphere1", "Used later for gain/AR"),
        ("Analyze", "HFSS > Analyze All  (or right-click Setup1 > Analyze)", "Progress window", "Wait until adaptive passes finish and sweep completes", "Solution exists", "Do not record numbers until this finishes"),
        ("Generate reports", "HFSS > Results > Create Modal Solution Data Report > Rectangular Plot", "Report", "dB(S(1,1)); VSWR(1); far-field Gain, Directivity, AxialRatio", "Plots in Results", "Export CSV/PNG into results/"),
    ]
    rows = []
    for i, (op, menu, dlg, param, expect, check) in enumerate(steps, 1):
        rows.append(
            f"<tr><td>{i}</td><td>{op}</td><td>{menu}</td><td>{dlg}</td><td>{param}</td><td>{expect}</td><td>{check}</td></tr>"
        )
    return f"""
<h2>HFSS GUI — Step by Step</h2>
<p>Use this procedure to build the antenna manually in Ansys Electronics Desktop. The RUN button performs the same operations through PyAEDT / Tools > Run Script.</p>
<p class="note">Ground thickness (1.00 mm), feed gap (1.50 mm), copper, 50 Ω lumped port and the air box are ENGINEERING ASSUMPTIONS. Helix R, pitch, turns, wire and ground radius are source values.</p>
<table>
<thead><tr><th>#</th><th>Operation</th><th>Menu path</th><th>Dialog</th><th>Parameter</th><th>Expected result</th><th>Validation check</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
<h3>After Analyze</h3>
<ol>
<li>Modal data: dB(S(1,1)) vs freq; marker at 3.035 GHz.</li>
<li>VSWR(1) vs freq; marker at 3.035 GHz.</li>
<li>Far field at 3.035 GHz: GainTotal, DirTotal, AxialRatio on Infinite Sphere1.</li>
<li>3D polar plot of GainTotal.</li>
<li>Export reports, then re-run the Python extractor so the dashboard reads HFSS_SIMULATED values.</li>
</ol>
"""


def feed_page() -> str:
    return f"""
<h2>Feed and Port</h2>
<p class="note">The source document does <strong>not</strong> define coax geometry, dielectric, connector, reference impedance, port size or integration line. The 50 Ω lumped port below is an ENGINEERING ASSUMPTION.</p>
<h3>Missing source information</h3>
<ul>
<li>Coax inner/outer radii and dielectric εr</li>
<li>Connector (SMA / N / custom)</li>
<li>Feed conductor distinct from 18 AWG helix wire</li>
<li>Port dimensions and integration line</li>
<li>Ground thickness and clearance hole</li>
</ul>
<h3>First-pass excitation</h3>
<table>
<tr><th>Item</th><th>Value</th><th>Provenance</th></tr>
<tr><td>Type</td><td>Lumped port P1</td><td>ENGINEERING_ASSUMPTION</td></tr>
<tr><td>Impedance</td><td>{ASSUMPTIONS['port_impedance_ohm']} Ω</td><td>ENGINEERING_ASSUMPTION</td></tr>
<tr><td>Feed gap</td><td>{ASSUMPTIONS['feed_gap_mm']} mm</td><td>ENGINEERING_ASSUMPTION</td></tr>
<tr><td>Port sheet</td><td>XZ rectangle, width {ASSUMPTIONS['port_sheet_width_mm']} mm, height {ASSUMPTIONS['feed_gap_mm']} mm at x = R</td><td>ENGINEERING_ASSUMPTION</td></tr>
<tr><td>Integration line</td><td>(R,0,0) → (R,0,gap) along +z</td><td>ENGINEERING_ASSUMPTION</td></tr>
<tr><td>Feed post</td><td>Cylinder radius {SOURCE['wire_radius_mm']} mm, height = gap</td><td>ENGINEERING_ASSUMPTION</td></tr>
</table>
<h3>Replace with a coaxial feed later</h3>
<ol>
<li>Obtain physical connector dimensions.</li>
<li>Delete P1 and PortSheet.</li>
<li>Model inner conductor, dielectric and shield.</li>
<li>Cut the ground plane for the shield.</li>
<li>Assign a wave port or lumped port on the coax cross-section.</li>
<li>Re-solve. Expect S11/VSWR to change more than the far-field beam shape.</li>
</ol>
"""


def far_field_page(results: dict[str, Any]) -> str:
    return f"""
<h2>Far Field / Gain / Directivity</h2>
<p>Infinite Sphere: {results.get('meta', {}).get('far_field_setup', 'Infinite Sphere1')} at {SOURCE['operating_frequency_GHz']} GHz.</p>
<div class="grid">
{val_box('Peak gain', results.get('gain_dB'), '9.5–14.0 dB', 'NOT SIMULATED' if results.get('gain_dB') is None else 'HFSS')}
{val_box('Peak directivity', results.get('directivity_dBi'), '10.0–14.5 dBi', 'NOT SIMULATED' if results.get('directivity_dBi') is None else 'HFSS')}
{val_box('Realized gain', results.get('realized_gain_dB'), 'report if available', 'NOT SIMULATED' if results.get('realized_gain_dB') is None else 'HFSS')}
</div>
{img('../results/plots/Gain_Pattern.png', 'gain')}
{img('../results/plots/Directivity_Pattern.png', 'directivity')}
{img('../results/plots/3D_Radiation_Pattern.png', '3d')}
<p>Peak direction: theta={((results.get('beam_direction') or {}).get('theta_deg'))}, phi={((results.get('beam_direction') or {}).get('phi_deg'))} — NOT SIMULATED until extracted.</p>
"""


def report_html(results: dict[str, Any], matrix: dict[str, Any]) -> str:
    calc = calculated_geometry()
    overall = matrix.get("overall_status", "NOT SIMULATED")
    row_html = "".join(
        f"<tr><td>{r.get('parameter')}</td><td>{r.get('requirement')}</td><td>{r.get('hfss_result')}</td><td>{r.get('status')}</td><td>{r.get('notes')}</td></tr>"
        for r in matrix.get("rows", [])
    )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Helical Antenna HFSS Report</title>
<link rel="stylesheet" href="../docs/css/style.css">
</head><body>
<header><h1>Helical Antenna HFSS Engineering Report</h1>
<div class="sub">{COMPANY_NAME} · Author: {AUTHOR_NAME} · {AUTHOR_EMAIL} · {AUTHOR_PHONE} · {now_iso()} · Status: {overall}</div></header>
<main>
<div class="card"><h2>1. Executive Summary</h2>
<p>A 3-turn axial-mode helical antenna at 3.035 GHz was modeled from {SOURCE_DOCUMENT}.
HFSS numerical results are <strong>{overall}</strong>. No fabricated S11, VSWR, gain, directivity or axial-ratio numbers are reported.</p></div>
<div class="card"><h2>2. Design Objective</h2>
<p>Build a repeatable HFSS workflow for the source helix, with GUI automation, result extraction and acceptance testing.</p></div>
<div class="card"><h2>3. Source Specification</h2>
<table>
<tr><td>Frequency</td><td>{SOURCE['operating_frequency_GHz']} GHz</td></tr>
<tr><td>Turns</td><td>{SOURCE['number_of_turns']}</td></tr>
<tr><td>Radius</td><td>{SOURCE['helix_centerline_radius_mm']} mm</td></tr>
<tr><td>Pitch</td><td>{SOURCE['pitch_mm']} mm</td></tr>
<tr><td>Wire</td><td>18 AWG, Ø {SOURCE['wire_diameter_mm']} mm</td></tr>
<tr><td>Ground radius / diameter</td><td>{SOURCE['ground_plane_radius_mm']} / {SOURCE['ground_plane_diameter_mm']} mm</td></tr>
<tr><td>Axial length (source)</td><td>{SOURCE['total_axial_length_mm']} mm</td></tr>
</table></div>
<div class="card"><h2>4–5. Geometry and Validation</h2>
<p>C/turn calculated {calc['circumference_per_turn_mm']:.4f} mm vs source 131.58 mm.
Pitch angle {calc['pitch_angle_deg']:.4f}° vs 12.54°. N·P = {calc['total_axial_length_mm']:.4f} mm vs source 87.82 mm (0.01 mm rounding).</p>
{img('../results/plots/geometry_3d.png', 'geometry')}
</div>
<div class="card"><h2>6–9. Materials, Feed, Port, Boundaries</h2>
<p>Copper helix and ground (assumption). 50 Ω lumped port across a {ASSUMPTIONS['feed_gap_mm']} mm gap (assumption). Radiation box padding 0.5 λ0 = {calc['airbox_padding_mm']:.3f} mm (assumption). λ0 = {calc['wavelength_mm']:.4f} mm (calculated).</p></div>
<div class="card"><h2>10–12. Mesh, Solver, Sweep</h2>
<p>Project {PROJECT_NAME}, design {DESIGN_NAME}, Setup1 at 3.035 GHz, MaxPasses {ASSUMPTIONS['max_passes']}, MaxDeltaS {ASSUMPTIONS['max_delta_s']}, interpolating sweep {ASSUMPTIONS['sweep_start_GHz']}–{ASSUMPTIONS['sweep_stop_GHz']} GHz. Mesh convergence is NOT SIMULATED.</p></div>
<div class="card"><h2>13–18. Electromagnetic Results</h2>
<p>All plots below are empty/watermarked until HFSS solves.</p>
{img('../results/plots/S11.png', 's11')}
{img('../results/plots/VSWR.png', 'vswr')}
{img('../results/plots/Gain_Pattern.png', 'gain')}
{img('../results/plots/Directivity_Pattern.png', 'dir')}
{img('../results/plots/Axial_Ratio.png', 'ar')}
{img('../results/plots/3D_Radiation_Pattern.png', '3d')}
</div>
<div class="card"><h2>19–20. Requirement Comparison / PASS-FAIL</h2>
<table><thead><tr><th>Parameter</th><th>Requirement</th><th>HFSS Result</th><th>Status</th><th>Notes</th></tr></thead>
<tbody>{row_html}</tbody></table>
<p>Overall: <strong>{overall}</strong></p></div>
<div class="card"><h2>21. Engineering Assumptions</h2>
<p>See ENGINEERING_ASSUMPTIONS.md. Feed, materials, air box and solver controls are not source requirements.</p></div>
<div class="card"><h2>22. Limitations</h2>
<ul>
<li>No physical coax/connector in the first-pass model.</li>
<li>Copper conductivity and ground thickness assumed.</li>
<li>Radiation boundary (not PML) as first pass.</li>
<li>Without a solved HFSS project, RF metrics cannot be accepted.</li>
</ul></div>
<div class="card"><h2>23. Recommended Next Steps</h2>
<ol>
<li>Install/license Ansys Electronics Desktop.</li>
<li>Press RUN in the GUI (or Tools > Run Script on hfss/project/build_helix_hfss.py).</li>
<li>Inspect geometry, materials, port and radiation box.</li>
<li>Analyze Setup1 and export results.</li>
<li>Re-run extraction so this report fills with HFSS_SIMULATED values.</li>
<li>If S11 is poor, replace the lumped gap with the real coax feed rather than changing source helix dimensions.</li>
</ol></div>
</main>
{footer_html()}
</body></html>
"""


def generate(results: dict[str, Any] | None = None, matrix: dict[str, Any] | None = None) -> list[Path]:
    root = repo_root()
    docs = root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "css").mkdir(parents=True, exist_ok=True)
    (docs / "css" / "style.css").write_text(css_text(), encoding="utf-8")
    results = results if results is not None else load_results()
    matrix = matrix if matrix is not None else load_matrix()
    pages = {
        "index.html": wrap("Dashboard", dashboard_body(results, matrix), "index.html"),
        "design.html": wrap("Design", design_page(), "design.html", mermaid=True),
        "implementation.html": wrap("Implementation", implementation_page(), "implementation.html"),
        "architecture.html": wrap("Architecture", architecture_page(), "architecture.html", mermaid=True),
        "geometry.html": wrap("Geometry", geometry_page(), "geometry.html"),
        "simulation.html": wrap(
            "Simulation",
            f"<h2>Simulation Setup</h2><p>Project {PROJECT_NAME}, design {DESIGN_NAME}, Setup1 at {SOURCE['operating_frequency_GHz']} GHz, sweep {ASSUMPTIONS['sweep_start_GHz']}–{ASSUMPTIONS['sweep_stop_GHz']} GHz. Status: {(results.get('meta') or {}).get('status', 'NOT SIMULATED')}.</p>"
            + img("../results/plots/geometry_3d.png", "model"),
            "simulation.html",
        ),
        "s11.html": wrap("S11", metric_page("S11 / Return Loss", "../results/plots/S11.png", f"<= {TARGETS['s11_max_dB']} dB", results.get("s11_dB")), "s11.html"),
        "vswr.html": wrap("VSWR", metric_page("VSWR", "../results/plots/VSWR.png", "1.1:1 to 1.4:1", results.get("vswr")), "vswr.html"),
        "gain.html": wrap("Gain", metric_page("Gain", "../results/plots/Gain_Pattern.png", "9.5 to 14.0 dB", results.get("gain_dB")), "gain.html"),
        "directivity.html": wrap("Directivity", metric_page("Directivity", "../results/plots/Directivity_Pattern.png", "10.0 to 14.5 dBi", results.get("directivity_dBi")), "directivity.html"),
        "axial_ratio.html": wrap(
            "Axial Ratio",
            metric_page(
                "Axial Ratio",
                "../results/plots/Axial_Ratio.png",
                "< 1.5 dB in the main beam direction",
                results.get("axial_ratio_dB"),
                extra="<p>Do not compare an off-axis AR sample to the target without stating θ, φ.</p>",
            ),
            "axial_ratio.html",
        ),
        "far_field.html": wrap("Far Field", far_field_page(results), "far_field.html"),
        "feed_and_port.html": wrap("Feed and Port", feed_page(), "feed_and_port.html"),
        "HFSS_GUI_STEP_BY_STEP.html": wrap("HFSS GUI", gui_steps_page(), "HFSS_GUI_STEP_BY_STEP.html"),
    }
    written = []
    for name, html in pages.items():
        path = docs / name
        path.write_text(html, encoding="utf-8")
        written.append(path)
    report_path = root / "reports" / "Helical_Antenna_HFSS_Report.html"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_html(results, matrix), encoding="utf-8")
    written.append(report_path)
    (root / "results" / "reports" / "Helical_Antenna_HFSS_Report.html").write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")
    return written


if __name__ == "__main__":
    for p in generate():
        print(p)
