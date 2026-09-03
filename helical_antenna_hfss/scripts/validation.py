"""Acceptance matrix. PASS only if a real HFSS result exists and meets the target."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import SOURCE, TARGETS, footer_html, repo_root, write_json


def _status(result: float | None, passed: bool | None, *, demo: bool = False) -> str:
    if result is None:
        return "NOT SIMULATED"
    if demo:
        return "DEMO PASS" if passed else "DEMO FAIL"
    if passed:
        return "PASS"
    return "FAIL"


def evaluate(results: dict[str, Any] | None = None) -> dict[str, Any]:
    if results is None:
        path = repo_root() / "results" / "hfss_results.json"
        if path.is_file():
            import json

            results = json.loads(path.read_text(encoding="utf-8"))
        else:
            results = {}

    f0 = SOURCE["operating_frequency_GHz"]
    s11 = results.get("s11_dB")
    vswr = results.get("vswr")
    gain = results.get("gain_dB")
    direc = results.get("directivity_dBi")
    ar = results.get("axial_ratio_dB")
    solved = bool((results.get("meta") or {}).get("solved"))
    demo = bool((results.get("meta") or {}).get("demonstration")) or (
        (results.get("meta") or {}).get("status") == "DEMO"
    )
    note_src = "DEMONSTRATION_EXAMPLE (modified-parameter ready-made set)" if demo else "HFSS_SIMULATED"

    rows = []

    def add(parameter: str, requirement: str, value: float | None, unit: str, passed: bool | None, notes: str) -> None:
        margin = ""
        if value is None:
            hfss_result = "NOT SIMULATED"
            status = "NOT SIMULATED"
        else:
            hfss_result = f"{value:.4g} {unit}"
            status = _status(value, passed, demo=demo)
        rows.append(
            {
                "parameter": parameter,
                "requirement": requirement,
                "hfss_result": hfss_result,
                "margin": margin,
                "status": status,
                "notes": notes,
                "value": value,
            }
        )

    add(
        "Operating frequency",
        f"{f0} GHz (source)",
        f0,
        "GHz",
        True,
        "This is the SOURCE_SPECIFICATION operating point, not an HFSS-extracted resonance.",
    )
    rows[-1]["hfss_result"] = f"{f0} GHz (setup)" if not solved else rows[-1]["hfss_result"]
    rows[-1]["status"] = "SOURCE" if not solved else rows[-1]["status"]
    rows[-1]["value"] = f0

    s11_pass = None if s11 is None else s11 <= TARGETS["s11_max_dB"]
    if s11 is not None:
        rows.append(
            {
                "parameter": "S11 at 3.035 GHz",
                "requirement": f"<= {TARGETS['s11_max_dB']} dB (preferred {TARGETS['s11_preferred_min_dB']} to {TARGETS['s11_preferred_max_dB']} dB)",
                "hfss_result": f"{s11:.4g} dB",
                "margin": f"{TARGETS['s11_max_dB'] - s11:.4g} dB vs -15 dB",
                "status": _status(s11, s11_pass, demo=demo),
                "notes": note_src,
                "value": s11,
            }
        )
    else:
        add("S11 at 3.035 GHz", "<= -15 dB, preferred -15 to -25 dB", None, "dB", None, "No HFSS S-parameter data.")

    if vswr is None:
        add("VSWR at 3.035 GHz", "1.1:1 to 1.4:1", None, "", None, "No HFSS VSWR data.")
    else:
        passed = TARGETS["vswr_min"] <= vswr <= TARGETS["vswr_max"]
        rows.append(
            {
                "parameter": "VSWR at 3.035 GHz",
                "requirement": "1.1:1 to 1.4:1",
                "hfss_result": f"{vswr:.4g}:1",
                "margin": f"distance to band {min(abs(vswr - TARGETS['vswr_min']), abs(vswr - TARGETS['vswr_max'])):.4g}",
                "status": _status(vswr, passed, demo=demo),
                "notes": note_src + ". Target is a band, not a single number.",
                "value": vswr,
            }
        )

    if direc is None:
        add("Directivity", "10.0 to 14.5 dBi", None, "dBi", None, "No HFSS far-field data.")
    else:
        passed = TARGETS["directivity_min_dBi"] <= direc <= TARGETS["directivity_max_dBi"]
        rows.append(
            {
                "parameter": "Directivity",
                "requirement": "10.0 to 14.5 dBi",
                "hfss_result": f"{direc:.4g} dBi",
                "margin": f"{direc - TARGETS['directivity_min_dBi']:.4g} dB above min",
                "status": _status(direc, passed, demo=demo),
                "notes": note_src + ". Compare main-beam directivity, not an arbitrary cut.",
                "value": direc,
            }
        )

    if gain is None:
        add("Gain", "9.5 to 14.0 dB", None, "dB", None, "No HFSS far-field data.")
    else:
        passed = TARGETS["gain_min_dB"] <= gain <= TARGETS["gain_max_dB"]
        rows.append(
            {
                "parameter": "Gain",
                "requirement": "9.5 to 14.0 dB",
                "hfss_result": f"{gain:.4g} dB",
                "margin": f"{gain - TARGETS['gain_min_dB']:.4g} dB above min",
                "status": _status(gain, passed, demo=demo),
                "notes": note_src,
                "value": gain,
            }
        )

    if ar is None:
        add("Axial ratio", "< 1.5 dB (main beam)", None, "dB", None, "No HFSS axial-ratio data. Direction must be identified.")
    else:
        passed = ar < TARGETS["axial_ratio_max_dB"]
        rows.append(
            {
                "parameter": "Axial ratio (main beam)",
                "requirement": "< 1.5 dB",
                "hfss_result": f"{ar:.4g} dB",
                "margin": f"{TARGETS['axial_ratio_max_dB'] - ar:.4g} dB below 1.5 dB",
                "status": _status(ar, passed, demo=demo),
                "notes": note_src + ". Main-beam direction (θ=0°, φ=0°).",
                "value": ar,
            }
        )

    statuses = {row["status"] for row in rows}
    if demo:
        if "DEMO FAIL" in statuses:
            overall = "DEMO FAIL"
        elif any(s == "DEMO PASS" for s in statuses):
            overall = "DEMO"
        else:
            overall = "DEMO"
    elif "FAIL" in statuses and solved:
        overall = "FAIL"
    elif all(s in {"PASS", "SOURCE"} for s in statuses) and solved:
        overall = "PASS"
    elif solved:
        overall = "PARTIAL"
    else:
        overall = "NOT SIMULATED"

    return {
        "overall_status": overall,
        "rows": rows,
        "solved": solved,
        "demonstration": demo,
        "rule": (
            "DEMO uses the existing modified-parameter ready-made dataset; it is not an HFSS solve. "
            "PASS is reserved for actual HFSS results that meet the requirement."
        ),
    }


def write_acceptance_csv(path: Path, matrix: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Parameter", "Requirement", "HFSS Result", "Margin", "PASS/FAIL", "Notes"])
        for row in matrix["rows"]:
            w.writerow([row["parameter"], row["requirement"], row["hfss_result"], row["margin"], row["status"], row["notes"]])


def generate(results: dict[str, Any] | None = None) -> dict[str, Any]:
    matrix = evaluate(results)
    root = repo_root()
    write_json(root / "results" / "acceptance_matrix.json", matrix)
    write_acceptance_csv(root / "results" / "csv" / "acceptance_matrix.csv", matrix)
    write_acceptance_csv(root / "results" / "acceptance_matrix.csv", matrix)
    write_validation_html(root / "VALIDATION_REPORT.html", matrix)
    write_validation_html(root / "docs" / "validation.html", matrix)
    return matrix


def write_validation_html(path: Path, matrix: dict[str, Any]) -> None:
    color = {
        "PASS": "#1b7f4e",
        "FAIL": "#a33",
        "NOT SIMULATED": "#6b5a2e",
        "PARTIAL": "#6b5a2e",
        "SOURCE": "#1f4e79",
        "DEMO": "#1f4e79",
        "DEMO PASS": "#1b7f4e",
        "DEMO FAIL": "#a33",
    }
    rows_html = []
    for row in matrix["rows"]:
        bg = color.get(row["status"], "#333")
        rows_html.append(
            "<tr>"
            f"<td>{row['parameter']}</td>"
            f"<td>{row['requirement']}</td>"
            f"<td>{row['hfss_result']}</td>"
            f"<td>{row['margin']}</td>"
            f"<td style='background:{bg};color:#fff;font-weight:700'>{row['status']}</td>"
            f"<td>{row['notes']}</td>"
            "</tr>"
        )
    overall_bg = color.get(matrix["overall_status"], "#333")
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Validation Report</title>
<style>
body {{ font-family: Segoe UI, sans-serif; background:#0f1724; color:#e8eef6; margin:0; padding:24px; }}
table {{ border-collapse: collapse; width:100%; background:#132033; }}
th, td {{ border:1px solid #2b3c55; padding:8px; text-align:left; vertical-align:top; }}
th {{ background:#1c2e45; }}
.badge {{ display:inline-block; padding:8px 16px; font-size:20px; font-weight:700; }}
.site-footer {{ margin-top:40px; padding:18px 24px; border-top:1px solid #2b3c55; color:#9fb3c8; font-size:13px; text-align:center; line-height:1.7; }}
.site-footer strong {{ color:#e8eef6; }}
</style></head><body>
<h1>Requirements Validation</h1>
<p class="badge" style="background:{overall_bg};color:#fff">OVERALL: {matrix['overall_status']}</p>
<p>{matrix['rule']}</p>
<table>
<thead><tr><th>Parameter</th><th>Requirement</th><th>HFSS Result</th><th>Margin</th><th>PASS/FAIL</th><th>Notes</th></tr></thead>
<tbody>{''.join(rows_html)}</tbody>
</table>
{footer_html()}
</body></html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    m = generate()
    print(m["overall_status"])
    for row in m["rows"]:
        print(row["parameter"], row["status"], row["hfss_result"])
