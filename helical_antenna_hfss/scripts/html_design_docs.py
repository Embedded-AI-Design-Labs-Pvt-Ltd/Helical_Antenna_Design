"""Detailed HTML bodies: antenna design, implementation procedure, system architecture."""

from __future__ import annotations

from common import (
    ASSUMPTIONS,
    COMPANY_NAME,
    COMPANY_WEBSITE,
    GITHUB_ORG_URL,
    SOURCE,
    SOURCE_DOCUMENT,
    TARGETS,
    calculated_geometry,
    wavelength_mm,
)


def mermaid(code: str) -> str:
    return f'<div class="diagram"><pre class="mermaid">\n{code.strip()}\n</pre></div>'


def design_page() -> str:
    calc = calculated_geometry()
    lam = wavelength_mm()
    return f"""
<h2>Antenna Design — Detailed Explanation</h2>
<p class="note">This page explains <strong>what</strong> is being designed and <strong>why</strong> each number exists.
Source geometry is locked from <code>{SOURCE_DOCUMENT}</code>. Feed, materials, air box and solver settings are
engineering assumptions, not source requirements.</p>

<div class="toc card">
<strong>On this page:</strong>
<a href="#purpose">Purpose</a>
<a href="#theory">Axial-mode helix</a>
<a href="#source">Source specification</a>
<a href="#calc">Calculated geometry</a>
<a href="#targets">RF targets</a>
<a href="#stack">Physical stack</a>
<a href="#assumptions">Assumptions</a>
<a href="#solver">Solver design</a>
<a href="#provenance">Provenance</a>
</div>

<h3 id="purpose">1. Purpose</h3>
<p>{COMPANY_NAME} built a repeatable Ansys HFSS workflow for a 3-turn axial-mode helical antenna at
<strong>{SOURCE['operating_frequency_GHz']} GHz</strong>. The product is not only the CAD model: it is a
one-click GUI, an IronPython/PyAEDT builder, dual result stores (demonstration vs live HFSS), validation
against the requirement matrix, and an HTML dashboard that never presents theoretical numbers as solved HFSS data.</p>
<p>Public repositories: <a href="{GITHUB_ORG_URL}">{GITHUB_ORG_URL}</a> ·
Website: <a href="{COMPANY_WEBSITE}">{COMPANY_WEBSITE}</a></p>

<h3 id="theory">2. Axial-mode helical antenna (design basis)</h3>
<p>A helix radiates in the <em>axial mode</em> when the circumference of one turn is on the order of one free-space
wavelength and the pitch angle is modest (typically about 12°–14°). In that regime the antenna produces a
circularly polarized beam along the helix axis (Kraus). This design uses:</p>
<ul>
<li>Circumference per turn C = 2πR ≈ {SOURCE['circumference_per_turn_mm']} mm</li>
<li>Free-space wavelength λ<sub>0</sub> = c / f<sub>0</sub> = {lam:.4f} mm at {SOURCE['operating_frequency_GHz']} GHz</li>
<li>C / λ<sub>0</sub> ≈ {SOURCE['circumference_per_turn_mm'] / lam:.3f} (near 1.33, axial-mode band)</li>
<li>Pitch angle α = arctan(P / C) ≈ {SOURCE['pitch_angle_deg']}°</li>
<li>Number of turns N = {SOURCE['number_of_turns']:.0f} (short helix; gain is modest compared with long helices)</li>
</ul>
<p>A circular ground plane under the helix acts as a reflector so the beam is predominantly in the +z (forward) direction.
Right-hand winding is assumed (not stated in the source document); a right-hand helix produces RHCP in the forward axial beam
under the usual Kraus convention.</p>

<h3 id="source">3. Locked source specification</h3>
<p>These values are transcribed from the source Word document. They are <strong>not</strong> optimized or rounded in code
except where the document itself already rounded (N·P vs listed axial length).</p>
<table>
<thead><tr><th>Parameter</th><th>Symbol</th><th>Value</th><th>Provenance</th></tr></thead>
<tbody>
<tr><td>Operating frequency</td><td>f<sub>0</sub></td><td>{SOURCE['operating_frequency_GHz']} GHz</td><td>SOURCE_SPECIFICATION</td></tr>
<tr><td>Number of turns</td><td>N</td><td>{SOURCE['number_of_turns']:.0f}</td><td>SOURCE_SPECIFICATION</td></tr>
<tr><td>Helix centerline radius</td><td>R</td><td>{SOURCE['helix_centerline_radius_mm']} mm</td><td>SOURCE_SPECIFICATION</td></tr>
<tr><td>Pitch</td><td>P</td><td>{SOURCE['pitch_mm']} mm</td><td>SOURCE_SPECIFICATION</td></tr>
<tr><td>Wire</td><td>—</td><td>18 AWG, Ø {SOURCE['wire_diameter_mm']} mm (r = {SOURCE['wire_radius_mm']} mm)</td><td>SOURCE_SPECIFICATION</td></tr>
<tr><td>Ground plane radius / diameter</td><td>R<sub>g</sub> / D<sub>g</sub></td><td>{SOURCE['ground_plane_radius_mm']} / {SOURCE['ground_plane_diameter_mm']} mm</td><td>SOURCE_SPECIFICATION</td></tr>
<tr><td>Axial length (listed)</td><td>L</td><td>{SOURCE['total_axial_length_mm']} mm</td><td>SOURCE_SPECIFICATION</td></tr>
<tr><td>Circumference / turn</td><td>C</td><td>{SOURCE['circumference_per_turn_mm']} mm</td><td>SOURCE_SPECIFICATION</td></tr>
<tr><td>Slant length / turn</td><td>S</td><td>{SOURCE['slant_length_per_turn_mm']} mm</td><td>SOURCE_SPECIFICATION</td></tr>
<tr><td>Pitch angle</td><td>α</td><td>{SOURCE['pitch_angle_deg']}°</td><td>SOURCE_SPECIFICATION</td></tr>
</tbody>
</table>

<h3 id="calc">4. Calculated geometry (must match source within rounding)</h3>
<p>Parametric centerline (right-hand):</p>
<pre>x = R · cos(2π t)
y = R · sin(2π t)
z = z<sub>0</sub> + P · t
t ∈ [0, N]</pre>
<p>z<sub>0</sub> is the feed gap (assumption). Closed-form checks:</p>
<table>
<thead><tr><th>Formula</th><th>Calculated</th><th>Source listed</th><th>Comment</th></tr></thead>
<tbody>
<tr><td>C = 2πR</td><td>{calc['circumference_per_turn_mm']:.4f} mm</td><td>{SOURCE['circumference_per_turn_mm']} mm</td><td>Match within 0.01 mm rounding</td></tr>
<tr><td>S = √(C² + P²)</td><td>{calc['slant_length_per_turn_mm']:.4f} mm</td><td>{SOURCE['slant_length_per_turn_mm']} mm</td><td>Match</td></tr>
<tr><td>α = arctan(P/C)</td><td>{calc['pitch_angle_deg']:.4f}°</td><td>{SOURCE['pitch_angle_deg']}°</td><td>Match</td></tr>
<tr><td>L = N·P</td><td>{calc['total_axial_length_mm']:.4f} mm</td><td>{SOURCE['total_axial_length_mm']} mm</td><td>0.01 mm listing rounding; pitch is not changed</td></tr>
<tr><td>λ<sub>0</sub> = c/f<sub>0</sub></td><td>{lam:.4f} mm</td><td>—</td><td>CALCULATED (not in the Word table)</td></tr>
</tbody>
</table>

<h3 id="targets">5. Electromagnetic acceptance targets</h3>
<p>These are design goals for a solved HFSS model at {SOURCE['operating_frequency_GHz']} GHz. Demonstration numbers
must never be used to mark PASS on a live Ansys run.</p>
<table>
<thead><tr><th>Metric</th><th>Requirement</th><th>Preferred band</th></tr></thead>
<tbody>
<tr><td>S11</td><td>≤ {TARGETS['s11_max_dB']} dB</td><td>{TARGETS['s11_preferred_min_dB']} to {TARGETS['s11_preferred_max_dB']} dB</td></tr>
<tr><td>VSWR</td><td>{TARGETS['vswr_min']} – {TARGETS['vswr_max']}</td><td>same</td></tr>
<tr><td>Directivity</td><td>{TARGETS['directivity_min_dBi']} – {TARGETS['directivity_max_dBi']} dBi</td><td>same</td></tr>
<tr><td>Gain</td><td>{TARGETS['gain_min_dB']} – {TARGETS['gain_max_dB']} dB</td><td>same</td></tr>
<tr><td>Axial ratio</td><td>&lt; {TARGETS['axial_ratio_max_dB']} dB in the main beam</td><td>on-axis / beam peak</td></tr>
</tbody>
</table>

<h3 id="stack">6. Physical design stack</h3>
<p>From −z to +z the model is: ground disk → lumped-port gap → 3-turn copper helix → vacuum radiation box.</p>
{mermaid('''
flowchart TB
  subgraph AirBox["Radiation box Rad1 — vacuum, 0.5 λ0 padding"]
    Helix["HelixWire — 18 AWG copper tube along centerline"]
    Feed["FeedPost + PortSheet P1 — 50 ohm lumped port"]
    GND["GroundPlane — copper disk R = 56.29 mm"]
  end
  GND --> Feed
  Feed --> Helix
  Helix --> Beam["Forward axial beam +z — expected RHCP"]
''')}
<p class="diagram-caption">Figure 1 — Physical design stack inside the HFSS radiation box (not a solved field plot).</p>

<h3 id="assumptions">7. Engineering assumptions (explicitly not source)</h3>
<table>
<thead><tr><th>Item</th><th>Chosen value</th><th>Why it exists</th></tr></thead>
<tbody>
<tr><td>Winding</td><td>{ASSUMPTIONS['winding']}</td><td>Handedness not in the source document</td></tr>
<tr><td>Conductor / ground</td><td>{ASSUMPTIONS['conductor_material']}</td><td>Material not specified; copper is the default RF choice</td></tr>
<tr><td>Ground thickness</td><td>{ASSUMPTIONS['ground_thickness_mm']} mm</td><td>Source lists radius only</td></tr>
<tr><td>Feed</td><td>{ASSUMPTIONS['feed_type']}, {ASSUMPTIONS['port_impedance_ohm']} Ω</td><td>No coax / connector drawing in the source</td></tr>
<tr><td>Feed gap</td><td>{ASSUMPTIONS['feed_gap_mm']} mm</td><td>Needed to place a lumped port without shorting the helix to ground</td></tr>
<tr><td>Radiation box</td><td>0.5 λ<sub>0</sub> padding ({calc['airbox_padding_mm']:.3f} mm)</td><td>Standard first-pass open-region size; not a PML</td></tr>
<tr><td>Setup1</td><td>{SOURCE['operating_frequency_GHz']} GHz, MaxPasses {ASSUMPTIONS['max_passes']}, MaxDeltaS {ASSUMPTIONS['max_delta_s']}</td><td>Solver controls never appear in the Word document</td></tr>
<tr><td>Sweep</td><td>{ASSUMPTIONS['sweep_start_GHz']}–{ASSUMPTIONS['sweep_stop_GHz']} GHz interpolating</td><td>Needed for S11/VSWR curves around f<sub>0</sub></td></tr>
</tbody>
</table>
<p>If S11 is poor after a real solve, replace the lumped gap with the physical coaxial feed rather than changing R, P or N.</p>

<h3 id="solver">8. HFSS solution design</h3>
<ul>
<li>Solution type: Driven Modal</li>
<li>Adaptive frequency: exactly {SOURCE['operating_frequency_GHz']} GHz (Setup1)</li>
<li>Sweep: interpolating {ASSUMPTIONS['sweep_start_GHz']}–{ASSUMPTIONS['sweep_stop_GHz']} GHz so 3.035 GHz is interior, not an endpoint</li>
<li>Far field: Infinite Sphere1 (θ, φ grid) for gain, directivity and axial ratio</li>
<li>What Python cannot fake: adaptive mesh, ΔS convergence, S-parameters, radiated fields</li>
</ul>

<h3 id="provenance">9. Provenance policy</h3>
<p>Every published number is tagged as one of: SOURCE_SPECIFICATION, CALCULATED, ENGINEERING_ASSUMPTION,
HFSS_SIMULATED, DEMONSTRATION_EXAMPLE, or NOT_SIMULATED. Demonstration plots and the ready-made CSV are
labeled DEMO. Live Ansys extraction is the only path that may write HFSS_SIMULATED values into
<code>results/live/</code>.</p>
"""


def implementation_page() -> str:
    return f"""
<h2>Implementation Procedure — Detailed Explanation</h2>
<p class="note">This page is the operator and developer procedure: how the software is built, how a run proceeds,
and how demonstration data is kept separate from live Ansys results.</p>

<div class="toc card">
<strong>On this page:</strong>
<a href="#quick">Quick start</a>
<a href="#gui">GUI procedure</a>
<a href="#phases">Workflow phases</a>
<a href="#modules">Module map</a>
<a href="#stores">Result stores</a>
<a href="#hfss">HFSS build path</a>
<a href="#validate">Validation</a>
<a href="#html">HTML generation</a>
<a href="#tests">Tests</a>
</div>

<h3 id="quick">1. Quick start</h3>
<ol class="steps">
<li>Install Python 3.10+ with <code>numpy</code> and <code>matplotlib</code>. Tkinter is part of the standard Windows build.</li>
<li>Optional: install Ansys Electronics Desktop (AEDT) with HFSS, and optionally <code>pyaedt</code>.</li>
<li>Double-click <code>RUN.bat</code> at the repository root or inside <code>helical_antenna_hfss/</code>.</li>
<li>The GUI opens with locked source parameters, a 3D helix preview, and two primary actions.</li>
<li>Open this HTML set from <code>helical_antenna_hfss/docs/index.html</code> after a run, or click <strong>Dashboard</strong>.</li>
</ol>

<h3 id="gui">2. GUI procedure (operator control flow)</h3>
<table>
<thead><tr><th>Control</th><th>What it does</th><th>What it must not do</th></tr></thead>
<tbody>
<tr><td><strong>DEMONSTRATE — EXISTING DATA</strong></td>
<td>Runs <code>workflow.run_all(mode="demo")</code>. Loads the ready-made modified-antenna dataset, publishes
<code>results/demo/</code>, regenerates plots and HTML, sets the active view to demo.</td>
<td>Does not overwrite <code>results/live/</code>. Does not launch Ansys. Does not claim PASS as a live HFSS solve.</td></tr>
<tr><td><strong>TEST IN HFSS — LIVE ANSYS</strong></td>
<td>Runs <code>workflow.run_all(mode="live")</code>. Builds geometry and the IronPython script. If AEDT is installed,
opens the model. Optional “Solve in HFSS” runs Setup1. Extraction writes <code>results/live/</code>.</td>
<td>Does not overwrite the demonstration store. If Ansys is missing or unsolved, live metrics stay NOT SIMULATED.</td></tr>
<tr><td>Show Demo / Show Live</td>
<td>Copies the chosen store to <code>results/hfss_results.json</code> and refreshes the comparison table.</td>
<td>Does not mix the two JSON files.</td></tr>
<tr><td>Dashboard / Report / HFSS script</td>
<td>Opens generated HTML or <code>hfss/project/build_helix_hfss.py</code>.</td>
<td>—</td></tr>
</tbody>
</table>

<h3 id="phases">3. Automated workflow phases</h3>
<p><code>scripts/workflow.py</code> is the integration agent. A live or demo run walks these phases (HFSS launch is skipped in demo mode):</p>
<ol class="steps">
<li>Read locked SOURCE constants from <code>scripts/common.py</code> (transcribed from the Word document).</li>
<li>Generate and validate helix polyline, wire tube, ground disk, feed post and port sheet.</li>
<li>Write geometry JSON/CSV and a 3D preview plot.</li>
<li>Live only: open or create the AEDT project (PyAEDT if present, else <code>ansysedt -RunScript</code>).</li>
<li>Write material assignments (copper helix/ground; vacuum box).</li>
<li>Write lumped-port definition P1 (50 Ω, integration line along the feed gap).</li>
<li>Write radiation-box size (0.5 λ<sub>0</sub> padding) and radiation boundary Rad1.</li>
<li>Write Setup1 (3.035 GHz adaptive), interpolating sweep, Infinite Sphere1.</li>
<li>Write IronPython <code>hfss/project/build_helix_hfss.py</code> so the same model can be built from Tools → Run Script.</li>
<li>Demo: load <code>examples/ready_made/</code>. Live: extract from a solved project, or write NOT SIMULATED.</li>
<li>Publish to the correct store; copy the active payload to <code>results/hfss_results.json</code>.</li>
<li>Validate against TARGETS (PASS only for real HFSS; demo rows are DEMO / DEMO PASS).</li>
<li>Generate plots (watermarked when not simulated), HTML dashboard, engineering report, optional QA.</li>
</ol>

<h3 id="modules">4. Implementation module map</h3>
<table>
<thead><tr><th>Module</th><th>Role in the implementation</th></tr></thead>
<tbody>
<tr><td><code>gui/app.py</code></td><td>Tkinter operator surface; threads <code>run_all</code> so the window stays responsive.</td></tr>
<tr><td><code>scripts/common.py</code></td><td>Single source of truth for SOURCE, TARGETS, ASSUMPTIONS, branding, paths.</td></tr>
<tr><td><code>scripts/geometry_generator.py</code></td><td>Centerline, solids metadata, calculated C/S/α/L, geometry validation.</td></tr>
<tr><td><code>scripts/materials_setup.py</code></td><td>Copper / vacuum documentation JSON consumed by the HFSS script.</td></tr>
<tr><td><code>scripts/port_setup.py</code></td><td>Lumped port sheet, impedance, integration line.</td></tr>
<tr><td><code>scripts/radiation_setup.py</code></td><td>Air-box extents and radiation boundary name.</td></tr>
<tr><td><code>scripts/hfss_setup.py</code></td><td>Setup1, sweep, far-field sphere, mesh/solver notes.</td></tr>
<tr><td><code>scripts/simulation_runner.py</code></td><td>PyAEDT or ansysedt launch; always writes the IronPython builder.</td></tr>
<tr><td><code>scripts/result_extractor.py</code></td><td>Reads a solved project when available; never invents S11/gain.</td></tr>
<tr><td><code>scripts/demo_dataset.py</code></td><td>Loads the existing ready-made example and tags it DEMONSTRATION_EXAMPLE.</td></tr>
<tr><td><code>scripts/results_store.py</code></td><td>Isolates <code>results/demo/</code> from <code>results/live/</code>.</td></tr>
<tr><td><code>scripts/validation.py</code></td><td>Acceptance matrix; PASS reserved for HFSS_SIMULATED.</td></tr>
<tr><td><code>scripts/report_generator.py</code></td><td>Writes <code>docs/*.html</code> including these design pages.</td></tr>
<tr><td><code>hfss/project/build_helix_hfss.py</code></td><td>IronPython that AEDT executes inside the 3D modeler.</td></tr>
</tbody>
</table>

<h3 id="stores">5. Dual-store implementation (data isolation)</h3>
<ol class="steps">
<li>Demonstration JSON is written only by demo mode from <code>examples/ready_made/</code>.</li>
<li>Live JSON is written only by extraction after a live path (solved or NOT SIMULATED placeholder).</li>
<li><code>results/active_source.json</code> records which store the dashboard currently displays.</li>
<li><code>results/hfss_results.json</code> is a working copy of the active store for report embedding.</li>
</ol>
<p>This isolation is the main implementation rule: pressing Demonstrate must not destroy a previous live solve,
and pressing Test in HFSS must not destroy the published demonstration dataset.</p>

<h3 id="hfss">6. Building the model inside Ansys</h3>
<p>Preferred automated path: PyAEDT creates project <code>Helix_3035MHz</code>, design <code>Helix_3035MHz</code>,
units mm, then creates GroundPlane, HelixWire, FeedPost, PortSheet, RadBox, assigns materials, P1, Rad1, Setup1 and Sweep.</p>
<p>Fallback path: <code>ansysedt -RunScript hfss/project/build_helix_hfss.py</code> (window stays open; do not use
<code>-RunScriptAndExit</code> if the operator needs to inspect the model).</p>
<p>Manual path: follow <a href="HFSS_GUI_STEP_BY_STEP.html">HFSS GUI step-by-step</a> — same dimensions and names.</p>
<p>After Analyze All, export reports or re-run extraction so live JSON becomes HFSS_SIMULATED.</p>

<h3 id="validate">7. Validation implementation</h3>
<ul>
<li>Geometry: R, P, N, wire Ø, ground radius must match SOURCE; N·P vs 87.82 mm is documented as 0.01 mm rounding.</li>
<li>Setup: solution frequency must be exactly 3.035 GHz; sweep must contain that frequency.</li>
<li>RF: S11, VSWR, gain, directivity, AR compared to TARGETS only when provenance is HFSS_SIMULATED.</li>
<li>Demo comparison uses status DEMO / DEMO PASS so it cannot be mistaken for a certified Ansys run.</li>
</ul>

<h3 id="html">8. HTML documentation generation</h3>
<p>Running the workflow (or <code>python scripts/report_generator.py</code>) writes:</p>
<ul>
<li><code>docs/design.html</code> — this design theory and specification</li>
<li><code>docs/implementation.html</code> — this procedure</li>
<li><code>docs/architecture.html</code> — system block, data-flow and control-flow diagrams</li>
<li>Dashboard, geometry, S11/VSWR/gain pages, engineering report under <code>reports/</code></li>
</ul>
<p>Diagrams are rendered with Mermaid.js in the browser. If the CDN is blocked, the diagram source remains visible
inside <code>&lt;pre class="mermaid"&gt;</code> blocks.</p>

<h3 id="tests">9. Automated tests</h3>
<p>From <code>helical_antenna_hfss/</code> run <code>python -m pytest tests -q</code>. Unit tests cover geometry formulas,
setup JSON, and result-store isolation. They do not require Ansys.</p>
"""


def architecture_page() -> str:
    return f"""
<h2>System Architecture — Block, Data Flow and Control Flow</h2>
<p class="note">These diagrams describe the software system that implements the 3.035 GHz helix in HFSS.
They are not electromagnetic field plots.</p>

<div class="toc card">
<strong>On this page:</strong>
<a href="#block">System block diagram</a>
<a href="#data">Data flow</a>
<a href="#control">Control flow</a>
<a href="#stores">Store architecture</a>
<a href="#trust">Trust boundary</a>
</div>

<h3 id="block">1. System block diagram</h3>
<p>The operator never edits source helix dimensions in the GUI. Automation reads locked constants, builds CAD and HFSS
objects, then publishes either demonstration or live results into HTML.</p>
{mermaid('''
flowchart TB
  subgraph Actor["Operator"]
    USER["Desktop GUI — gui/app.py"]
  end

  subgraph App["Python automation — helical_antenna_hfss"]
    WF["workflow.py integration agent"]
    GEO["geometry_generator"]
    CFG["materials / port / radiation / hfss_setup"]
    SIM["simulation_runner + IronPython builder"]
    EXT["result_extractor"]
    DEM["demo_dataset"]
    STO["results_store"]
    VAL["validation"]
    RPT["report_generator"]
  end

  subgraph Ansys["Ansys Electronics Desktop"]
    AEDT["Project Helix_3035MHz"]
    SOL["HFSS Setup1 + Sweep + Infinite Sphere1"]
  end

  subgraph Out["Published artifacts"]
    HTML["docs/*.html dashboard and design pages"]
    JSON["results/demo and results/live"]
    PLT["results/plots"]
  end

  USER --> WF
  WF --> GEO
  WF --> CFG
  WF --> SIM
  SIM --> AEDT
  AEDT --> SOL
  SOL --> EXT
  WF --> DEM
  EXT --> STO
  DEM --> STO
  STO --> VAL
  VAL --> RPT
  RPT --> HTML
  STO --> JSON
  RPT --> PLT
''')}
<p class="diagram-caption">Figure 2 — System block diagram. Ansys is optional at runtime; HTML and geometry still generate offline.</p>

<h3>Component responsibilities</h3>
<table>
<thead><tr><th>Block</th><th>Inputs</th><th>Outputs</th><th>Failure behaviour</th></tr></thead>
<tbody>
<tr><td>GUI</td><td>Button clicks, optional Solve checkbox</td><td>Calls <code>run_all(mode=...)</code></td><td>Errors shown in the log pane; UI thread not blocked</td></tr>
<tr><td>workflow.py</td><td>mode demo|live, open_hfss, solve</td><td>Phase log, published store, HTML</td><td>Failed phase recorded; later phases still attempt reports</td></tr>
<tr><td>geometry_generator</td><td>SOURCE, ASSUMPTIONS.feed_gap</td><td>Polyline, validation HTML/JSON</td><td>Mismatches reported; source R/P/N not auto-changed</td></tr>
<tr><td>simulation_runner</td><td>Generated JSON + IronPython</td><td>Open AEDT model; optional solve</td><td>If ansysedt missing, script is still written</td></tr>
<tr><td>result_extractor</td><td>Solved project or none</td><td>Live JSON or NOT SIMULATED</td><td>Never fills metrics from theory</td></tr>
<tr><td>demo_dataset</td><td>examples/ready_made</td><td>Tagged demonstration payload</td><td>Missing files raise a clear error</td></tr>
<tr><td>report_generator</td><td>Active results + matrix</td><td>docs/ HTML including these pages</td><td>Pages still render with NOT SIMULATED badges</td></tr>
</tbody>
</table>

<h3 id="data">2. Data-flow diagram</h3>
<p>Data moves left to right from the locked specification to either the demonstration archive or a live HFSS extract.
The two stores never write into each other.</p>
{mermaid('''
flowchart LR
  subgraph Spec["Specification data"]
    DOCX["Source Word document"]
    SRC["common.SOURCE and TARGETS"]
    ASM["common.ASSUMPTIONS"]
  end

  subgraph Build["Build data"]
    GJSON["geometry_parameters.json"]
    IPY["build_helix_hfss.py"]
    MDL["AEDT 3D model"]
  end

  subgraph Results["Result data"]
    READY["examples/ready_made CSV/JSON"]
    DEMO["results/demo"]
    LIVE["results/live"]
    ACT["results/hfss_results.json"]
    MTX["acceptance_matrix.json"]
  end

  subgraph Views["Views"]
    GUI["GUI comparison table"]
    DASH["HTML dashboard"]
    RPT["Engineering report"]
  end

  DOCX --> SRC
  SRC --> GJSON
  ASM --> GJSON
  GJSON --> IPY
  IPY --> MDL
  MDL -->|"solved S / far-field"| LIVE
  MDL -->|"unsolved"| LIVE
  READY --> DEMO
  DEMO --> ACT
  LIVE --> ACT
  ACT --> MTX
  ACT --> GUI
  ACT --> DASH
  MTX --> DASH
  MTX --> RPT
''')}
<p class="diagram-caption">Figure 3 — Data flow. Live metrics originate only from Ansys; demo metrics originate only from ready-made files.</p>

<h3>Principal data artifacts</h3>
<table>
<thead><tr><th>Artifact</th><th>Produced by</th><th>Consumed by</th></tr></thead>
<tbody>
<tr><td><code>scripts/common.py</code> SOURCE dict</td><td>Manual transcription from the Word document</td><td>All generators</td></tr>
<tr><td><code>hfss/geometry/*.json</code></td><td>geometry_generator</td><td>IronPython builder, geometry HTML</td></tr>
<tr><td><code>hfss/project/build_helix_hfss.py</code></td><td>simulation_runner</td><td>AEDT Tools → Run Script</td></tr>
<tr><td><code>examples/ready_made/helix_example_results.json</code></td><td>Prior modified-antenna example (not this PC’s Ansys)</td><td>demo_dataset</td></tr>
<tr><td><code>results/demo/*.json</code></td><td>demo publish</td><td>GUI Show Demo, dashboard</td></tr>
<tr><td><code>results/live/*.json</code></td><td>live extract or placeholder</td><td>GUI Show Live, dashboard</td></tr>
<tr><td><code>results/plots/*.png</code></td><td>plot_generator</td><td>HTML img tags</td></tr>
<tr><td><code>docs/*.html</code></td><td>report_generator</td><td>Browser / GUI Dashboard</td></tr>
</tbody>
</table>

<h3 id="control">3. Control-flow diagram</h3>
<p>Control starts at <code>RUN.bat</code>, which starts the GUI (and may pre-run a CLI workflow). Every subsequent branch
is an explicit operator choice or a detected environment condition (Ansys present or not, Solve checked or not).</p>
{mermaid('''
flowchart TD
  START["RUN.bat / python run_gui.py"] --> GUI["HelixGUI main window"]
  GUI --> WAIT["Wait for operator"]
  WAIT --> A{"Which button?"}

  A -->|"DEMONSTRATE"| D1["mode = demo"]
  D1 --> D2["Generate geometry and setup JSON"]
  D2 --> D3["Skip AEDT launch"]
  D3 --> D4["Load ready-made demonstration"]
  D4 --> D5["Publish results/demo — do not touch live"]
  D5 --> D6["Validate as DEMO not PASS"]
  D6 --> PUB["Plots + HTML + open dashboard"]

  A -->|"TEST IN HFSS"| L1["mode = live"]
  L1 --> L2["Generate geometry and setup JSON"]
  L2 --> L3{"ansysedt found?"}
  L3 -->|No| L4["Write IronPython only"]
  L4 --> L5["Live payload NOT SIMULATED"]
  L3 -->|Yes| L6["Open AEDT and build model"]
  L6 --> L7{"Solve checkbox?"}
  L7 -->|No| L5
  L7 -->|Yes| L8["Analyze Setup1 and Sweep"]
  L8 --> L9{"Solution exists?"}
  L9 -->|Yes| L10["Extract S11 VSWR gain AR"]
  L9 -->|No| L5
  L10 --> L11["Publish results/live — do not touch demo"]
  L5 --> L11
  L11 --> L12["Validate: PASS only if HFSS_SIMULATED"]
  L12 --> PUB

  A -->|"Show Demo / Show Live"| S1["Copy chosen store to active JSON"]
  S1 --> S2["Refresh GUI table"]

  A -->|"Dashboard / Report"| B1["webbrowser.open HTML"]

  PUB --> WAIT
  S2 --> WAIT
  B1 --> WAIT
''')}
<p class="diagram-caption">Figure 4 — Control flow. Demo and live paths share geometry generation but never share result writers.</p>

<h3 id="stores">4. Result-store architecture</h3>
{mermaid('''
flowchart TB
  subgraph Isolated["Isolated stores"]
    DEMO["results/demo/hfss_results.json"]
    LIVE["results/live/hfss_results.json"]
  end
  FLAG["results/active_source.json  demo or live"]
  WORK["results/hfss_results.json  working copy"]
  HTML["docs/index.html embedded payload"]
  DEMO -->|"Show Demo or Demonstrate"| FLAG
  LIVE -->|"Show Live or Test in HFSS"| FLAG
  FLAG --> WORK
  WORK --> HTML
''')}
<p class="diagram-caption">Figure 5 — Active-source pointer selects which isolated store the dashboard embeds.</p>

<h3 id="trust">5. Trust boundary</h3>
<ul>
<li><strong>Trusted specification:</strong> Word document → <code>SOURCE</code> / <code>TARGETS</code> (human-transcribed, unit-tested).</li>
<li><strong>Trusted simulation:</strong> only values extracted from a solved HFSS project.</li>
<li><strong>Untrusted as HFSS:</strong> ready-made example, theoretical Kraus estimates, empty plots, mesh tables labeled DEMO.</li>
<li><strong>Offline completeness:</strong> missing Ansys is a valid state. The system still emits geometry, scripts, HTML and NOT SIMULATED metrics.</li>
</ul>
<p>Company: {COMPANY_NAME}. Repositories: <a href="{GITHUB_ORG_URL}">{GITHUB_ORG_URL}</a>.</p>
"""
