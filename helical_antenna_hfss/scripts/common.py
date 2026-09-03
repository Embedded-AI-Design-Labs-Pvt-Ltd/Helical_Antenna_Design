"""Shared constants, paths, and provenance helpers.

Provenance categories (never mix these):
  SOURCE_SPECIFICATION  — transcribed from the source Word document
  CALCULATED            — derived from formulas using source dimensions
  ENGINEERING_ASSUMPTION — not in the source document; documented in ENGINEERING_ASSUMPTIONS.md
  HFSS_SIMULATED        — extracted from a solved Ansys HFSS project
  USER_PROVIDED         — supplied by the operator at runtime
  NOT_SIMULATED         — HFSS has not produced this quantity
"""

from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

C0_M_S = 299792458.0

COMPANY_NAME = "Embedded AI Design Labs Pvt Ltd"
AUTHOR_NAME = "Muhammad Samiullah"
AUTHOR_EMAIL = "info@embedailabs.com"
AUTHOR_PHONE = "9611748385"
COPYRIGHT_YEAR = 2026
PRODUCT_TITLE = "3.035 GHz Helical Antenna HFSS Automation"
GITHUB_ORG_URL = "https://github.com/Embedded-AI-Design-Labs-Pvt-Ltd"
COMPANY_WEBSITE = "https://www.embedailabs.com"


def copyright_line() -> str:
    return f"© {COPYRIGHT_YEAR} {COMPANY_NAME}. All rights reserved."


def footer_plain() -> str:
    return (
        f"{COMPANY_NAME}  |  Author: {AUTHOR_NAME}  |  {AUTHOR_EMAIL}  |  "
        f"{AUTHOR_PHONE}  |  {GITHUB_ORG_URL}  |  {copyright_line()}"
    )


def footer_html(*, extra: str = "") -> str:
    extra_html = f"<div class='footer-note'>{extra}</div>" if extra else ""
    return (
        "<footer class='site-footer'>"
        f"<div><strong>{COMPANY_NAME}</strong></div>"
        f"<div>Author: {AUTHOR_NAME} &nbsp;·&nbsp; "
        f"<a href='mailto:{AUTHOR_EMAIL}'>{AUTHOR_EMAIL}</a> &nbsp;·&nbsp; "
        f"<a href='tel:{AUTHOR_PHONE}'>{AUTHOR_PHONE}</a></div>"
        f"<div><a href='{GITHUB_ORG_URL}'>{GITHUB_ORG_URL}</a> &nbsp;·&nbsp; "
        f"<a href='{COMPANY_WEBSITE}'>{COMPANY_WEBSITE}</a></div>"
        f"<div>{copyright_line()}</div>"
        f"{extra_html}"
        "</footer>"
    )


PROJECT_NAME = "Helix_3035MHz"
DESIGN_NAME = "Helix_3035MHz"
SETUP_NAME = "Setup1"
SWEEP_NAME = "Sweep"
FAR_FIELD_NAME = "Infinite Sphere1"
PORT_NAME = "P1"
RADIATION_BOUNDARY_NAME = "Rad1"

SOURCE_DOCUMENT = "Helical Antenna_Modified_Parameter (1)(1).docx"

# --- SOURCE_SPECIFICATION (do not change unless the user explicitly requests it) ---
SOURCE = {
    "operating_frequency_GHz": 3.035,
    "number_of_turns": 3.0,
    "helix_centerline_radius_mm": 20.94,
    "pitch_mm": 29.27,
    "wire_awg": 18,
    "wire_diameter_mm": 1.024,
    "wire_radius_mm": 0.512,
    "ground_plane_radius_mm": 56.29,
    "ground_plane_diameter_mm": 112.59,
    "total_axial_length_mm": 87.82,
    "circumference_per_turn_mm": 131.58,
    "slant_length_per_turn_mm": 134.79,
    "pitch_angle_deg": 12.54,
}

TARGETS = {
    "operating_frequency_GHz": 3.035,
    "s11_max_dB": -15.0,
    "s11_preferred_min_dB": -25.0,
    "s11_preferred_max_dB": -15.0,
    "vswr_min": 1.1,
    "vswr_max": 1.4,
    "directivity_min_dBi": 10.0,
    "directivity_max_dBi": 14.5,
    "gain_min_dB": 9.5,
    "gain_max_dB": 14.0,
    "axial_ratio_max_dB": 1.5,
}

# --- ENGINEERING_ASSUMPTION (explicitly NOT source requirements) ---
ASSUMPTIONS = {
    "winding": "right_hand",
    "winding_note": "Handedness is not stated in the source document. Right-hand winding is assumed (Kraus convention: RH helix produces RHCP in the axial forward beam).",
    "conductor_material": "copper",
    "ground_material": "copper",
    "air_material": "vacuum",
    "use_pec": False,
    "copper_conductivity_S_per_m": 5.8e7,
    "ground_thickness_mm": 1.00,
    "feed_type": "lumped_port_50ohm",
    "feed_gap_mm": 1.50,
    "port_impedance_ohm": 50.0,
    "port_sheet_width_mm": 1.024,
    "helix_segments_per_turn": 48,
    "helix_cross_section_segments": 8,
    "airbox_padding_wavelengths": 0.5,
    "solution_type": "DrivenModal",
    "model_units": "mm",
    "sweep_start_GHz": 2.50,
    "sweep_stop_GHz": 4.00,
    "sweep_step_MHz": 10.0,
    "sweep_type": "Interpolating",
    "max_passes": 15,
    "min_passes": 4,
    "min_converged_passes": 2,
    "max_delta_s": 0.02,
    "percent_refinement": 30,
    "basis_order": 1,
    "theta_start_deg": 0.0,
    "theta_stop_deg": 180.0,
    "theta_step_deg": 5.0,
    "phi_start_deg": -180.0,
    "phi_stop_deg": 180.0,
    "phi_step_deg": 10.0,
    "connector": "not_modeled",
    "coax_geometry": "not_modeled",
    "dielectric_feed": "none_vacuum_gap",
}

GEOMETRY_TOLERANCE_MM = 0.02
GEOMETRY_TOLERANCE_DEG = 0.02


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def wavelength_m(frequency_Hz: float | None = None) -> float:
    f = frequency_Hz if frequency_Hz is not None else SOURCE["operating_frequency_GHz"] * 1e9
    return C0_M_S / f


def wavelength_mm(frequency_Hz: float | None = None) -> float:
    return wavelength_m(frequency_Hz) * 1e3


def ensure_dirs() -> None:
    root = repo_root()
    for rel in (
        "hfss/project",
        "hfss/geometry",
        "hfss/setup",
        "hfss/boundaries",
        "hfss/ports",
        "hfss/results",
        "results/plots",
        "results/csv",
        "results/screenshots",
        "results/reports",
        "docs/css",
        "docs/js",
        "docs/source",
        "tests",
        "reports",
        "gui",
    ):
        (root / rel).mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def empty_simulated_quantity(name: str) -> dict[str, Any]:
    return {
        "name": name,
        "value": None,
        "unit": "",
        "status": "NOT_AVAILABLE",
        "provenance": "NOT_SIMULATED",
        "notes": "Ansys HFSS has not been solved for this quantity. No theoretical substitute is reported.",
    }


def find_ansysedt() -> Path | None:
    env_keys = (
        "ANSYSEM_ROOT252",
        "ANSYSEM_ROOT251",
        "ANSYSEM_ROOT242",
        "ANSYSEM_ROOT241",
        "ANSYSEM_ROOT232",
        "ANSYSEM_ROOT231",
        "ANSYSEM_ROOT221",
        "ANSYSEM_ROOT212",
    )
    candidates: list[Path] = []
    for key in env_keys:
        raw = os.environ.get(key)
        if raw:
            root = Path(raw)
            candidates.extend(
                [
                    root / "ansysedt.exe",
                    root / "Win64" / "ansysedt.exe",
                    root / "AnsysEM" / "Win64" / "ansysedt.exe",
                ]
            )
    explicit = os.environ.get("ANSYS_AEDT") or os.environ.get("ANSYSEDT")
    if explicit:
        candidates.append(Path(explicit))
    search_roots = [
        Path(r"C:\Program Files\AnsysEM"),
        Path(r"C:\Program Files\ANSYS Inc"),
        Path(r"C:\Program Files\Ansys Inc"),
        Path(r"C:\Program Files (x86)\AnsysEM"),
        Path.home() / "AppData" / "Local" / "AnsysEM",
        Path(r"D:\Program Files\AnsysEM"),
        Path(r"E:\Program Files\AnsysEM"),
    ]
    for root in search_roots:
        if not root.is_dir():
            continue
        candidates.append(root / "ansysedt.exe")
        try:
            children = list(root.iterdir())
        except OSError:
            children = []
        for child in children:
            if not child.is_dir():
                continue
            candidates.extend(
                [
                    child / "ansysedt.exe",
                    child / "Win64" / "ansysedt.exe",
                    child / "AnsysEM" / "Win64" / "ansysedt.exe",
                    child / "Win64" / "AnsysEM" / "ansysedt.exe",
                ]
            )
    which = shutil_which("ansysedt")
    if which:
        candidates.append(Path(which))
    seen: set[str] = set()
    for path in candidates:
        key = str(path).lower()
        if key in seen:
            continue
        seen.add(key)
        if path.is_file():
            return path
    return None


def shutil_which(cmd: str) -> str | None:
    import shutil

    return shutil.which(cmd)


def calculated_geometry() -> dict[str, Any]:
    r = SOURCE["helix_centerline_radius_mm"]
    p = SOURCE["pitch_mm"]
    n = SOURCE["number_of_turns"]
    circ = 2.0 * math.pi * r
    slant = math.hypot(circ, p)
    pitch_angle = math.degrees(math.atan2(p, circ))
    axial = n * p
    f_hz = SOURCE["operating_frequency_GHz"] * 1e9
    lam_mm = wavelength_mm(f_hz)
    return {
        "provenance": "CALCULATED",
        "helix_diameter_mm": 2.0 * r,
        "circumference_per_turn_mm": circ,
        "slant_length_per_turn_mm": slant,
        "pitch_angle_deg": pitch_angle,
        "total_axial_length_mm": axial,
        "ground_plane_diameter_mm": 2.0 * SOURCE["ground_plane_radius_mm"],
        "wire_radius_mm": SOURCE["wire_diameter_mm"] / 2.0,
        "wavelength_mm": lam_mm,
        "wavelength_m": lam_mm / 1e3,
        "circumference_over_wavelength": circ / lam_mm,
        "pitch_over_wavelength": p / lam_mm,
        "axial_length_over_wavelength": axial / lam_mm,
        "ground_radius_over_wavelength": SOURCE["ground_plane_radius_mm"] / lam_mm,
        "feed_gap_mm": ASSUMPTIONS["feed_gap_mm"],
        "ground_thickness_mm": ASSUMPTIONS["ground_thickness_mm"],
        "airbox_padding_mm": ASSUMPTIONS["airbox_padding_wavelengths"] * lam_mm,
        "notes": {
            "axial_length": (
                "N * pitch = 3 * 29.27 = 87.81 mm. Source lists 87.82 mm. "
                "Difference is 0.01 mm (rounding). Source pitch is not changed."
            ),
            "axial_mode": (
                "C/λ ≈ 1.33 and α ≈ 12.54° are consistent with axial-mode helical operation "
                "(Kraus: C/λ ~ 0.75–1.33, α ~ 12–14°). This is a calculated indicator, not an HFSS result."
            ),
        },
    }


def airbox_mm() -> dict[str, float]:
    calc = calculated_geometry()
    pad = calc["airbox_padding_mm"]
    gp_r = SOURCE["ground_plane_radius_mm"]
    feed_gap = ASSUMPTIONS["feed_gap_mm"]
    gp_t = ASSUMPTIONS["ground_thickness_mm"]
    axial = SOURCE["total_axial_length_mm"]
    xmin = -(gp_r + pad)
    zmin = -(gp_t + pad)
    xsize = 2.0 * (gp_r + pad)
    ysize = xsize
    zsize = gp_t + feed_gap + axial + 2.0 * pad
    return {
        "xmin_mm": xmin,
        "ymin_mm": xmin,
        "zmin_mm": zmin,
        "xsize_mm": xsize,
        "ysize_mm": ysize,
        "zsize_mm": zsize,
        "padding_mm": pad,
        "zmax_mm": zmin + zsize,
    }


def sweep_includes_operating_frequency() -> dict[str, Any]:
    f0 = SOURCE["operating_frequency_GHz"]
    start = ASSUMPTIONS["sweep_start_GHz"]
    stop = ASSUMPTIONS["sweep_stop_GHz"]
    step_ghz = ASSUMPTIONS["sweep_step_MHz"] / 1000.0
    npts = int(round((stop - start) / step_ghz)) + 1
    on_grid = abs(((f0 - start) / step_ghz) - round((f0 - start) / step_ghz)) < 1e-9
    return {
        "start_GHz": start,
        "stop_GHz": stop,
        "step_MHz": ASSUMPTIONS["sweep_step_MHz"],
        "nominal_point_count": npts,
        "operating_frequency_GHz": f0,
        "operating_frequency_in_span": start <= f0 <= stop,
        "operating_frequency_on_10MHz_grid": on_grid,
        "note": (
            "A 10 MHz linear grid from 2.50 GHz does not land on 3.035 GHz. "
            "The adaptive solution frequency is exactly 3.035 GHz. "
            "The interpolating sweep reports S-parameters across 2.50–4.00 GHz and can be "
            "sampled at 3.035 GHz. Discrete 10 MHz reporting is retained as requested."
        ),
    }


def default_results_payload(hfss_available: bool = False, solved: bool = False) -> dict[str, Any]:
    status = "PASS" if solved else "NOT SIMULATED"
    if solved is False and hfss_available:
        status = "NOT SIMULATED"
    quantities = {
        "s11_dB": empty_simulated_quantity("S11"),
        "vswr": empty_simulated_quantity("VSWR"),
        "gain_dB": empty_simulated_quantity("Gain"),
        "realized_gain_dB": empty_simulated_quantity("RealizedGain"),
        "directivity_dBi": empty_simulated_quantity("Directivity"),
        "axial_ratio_dB": empty_simulated_quantity("AxialRatio"),
        "radiation_efficiency": empty_simulated_quantity("RadiationEfficiency"),
        "peak_theta_deg": empty_simulated_quantity("PeakTheta"),
        "peak_phi_deg": empty_simulated_quantity("PeakPhi"),
        "resonant_frequency_GHz": empty_simulated_quantity("ResonantFrequency"),
    }
    for key, unit in (
        ("s11_dB", "dB"),
        ("vswr", "ratio"),
        ("gain_dB", "dB"),
        ("realized_gain_dB", "dB"),
        ("directivity_dBi", "dBi"),
        ("axial_ratio_dB", "dB"),
        ("radiation_efficiency", "ratio"),
        ("peak_theta_deg", "deg"),
        ("peak_phi_deg", "deg"),
        ("resonant_frequency_GHz", "GHz"),
    ):
        quantities[key]["unit"] = unit
    return {
        "meta": {
            "status": status if not solved else "PARTIAL",
            "project_name": PROJECT_NAME,
            "design_name": DESIGN_NAME,
            "setup_name": SETUP_NAME,
            "sweep_name": SWEEP_NAME,
            "far_field_setup": FAR_FIELD_NAME,
            "port_name": PORT_NAME,
            "timestamp_utc": now_iso(),
            "hfss_available": hfss_available,
            "solved": solved,
            "source_document": SOURCE_DOCUMENT,
            "company": COMPANY_NAME,
            "author": AUTHOR_NAME,
        },
        "frequency_Hz": SOURCE["operating_frequency_GHz"] * 1e9,
        "frequency_GHz": SOURCE["operating_frequency_GHz"],
        "s11_dB": None,
        "vswr": None,
        "gain_dB": None,
        "realized_gain_dB": None,
        "directivity_dBi": None,
        "axial_ratio_dB": None,
        "radiation_efficiency": None,
        "beam_direction": {"theta_deg": None, "phi_deg": None},
        "s11_at_3035MHz_dB": None,
        "vswr_at_3035MHz": None,
        "min_s11_dB": None,
        "min_s11_frequency_GHz": None,
        "quantities": quantities,
        "sweep": [],
        "warnings": [
            "Numerical electromagnetic results are NOT SIMULATED until Ansys HFSS actually solves this design."
        ],
    }
