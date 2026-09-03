"""Lead integration: run all phases without fabricating HFSS results."""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from demo_dataset import load_demonstration  # noqa: E402
from results_store import ensure_live_placeholder, publish  # noqa: E402
from common import (  # noqa: E402
    SOURCE,
    default_results_payload,
    ensure_dirs,
    find_ansysedt,
    footer_html,
    repo_root,
    write_json,
)
from geometry_generator import generate as generate_geometry  # noqa: E402
from hfss_setup import generate as generate_setup  # noqa: E402
from materials_setup import generate as generate_materials  # noqa: E402
from optimization import generate as generate_optimization  # noqa: E402
from plot_generator import generate_plots  # noqa: E402
from port_setup import generate as generate_port  # noqa: E402
from radiation_setup import generate as generate_radiation  # noqa: E402
from report_generator import generate as generate_reports  # noqa: E402
from result_extractor import extract  # noqa: E402
from simulation_runner import run as run_hfss  # noqa: E402
from validation import generate as generate_validation  # noqa: E402

LogFn = Callable[[str], None]


def _log(msg: str, log: LogFn | None) -> None:
    if log:
        log(msg)
    else:
        print(msg)


def run_all(
    *,
    solve: bool = False,
    open_hfss: bool = True,
    log: LogFn | None = None,
    mode: str = "live",
    run_qa: bool = True,
) -> dict:
    ensure_dirs()
    phases = []

    def phase(n: int, name: str, fn) -> object:
        _log(f"PHASE {n}: {name}", log)
        try:
            out = fn()
            phases.append({"phase": n, "name": name, "ok": True})
            return out
        except Exception as exc:
            _log(f"PHASE {n} failed: {exc}", log)
            _log(traceback.format_exc(), log)
            phases.append({"phase": n, "name": name, "ok": False, "error": str(exc)})
            return None

    phase(1, "Read source document parameters", lambda: SOURCE)
    geom = phase(2, "Validate / generate geometry", generate_geometry)
    phase(3, "Generate geometry artifacts", lambda: geom)
    phase(5, "Assign materials (documented)", generate_materials)
    phase(6, "Create feed and port definition", generate_port)
    phase(7, "Create air region definition", generate_radiation)
    phase(8, "Radiation boundary definition", generate_radiation)
    phase(9, "Adaptive solution configuration", generate_setup)
    phase(10, "Frequency sweep configuration", generate_setup)
    phase(11, "Far-field setup configuration", generate_setup)

    hfss_result = {
        "hfss_available": find_ansysedt() is not None,
        "solved": False,
        "desktop_open": False,
        "method": "skipped",
    }
    demo_mode = mode == "demo"
    if demo_mode:
        open_hfss = False
        _log("MODE: DEMONSTRATE — existing modified-antenna dataset. Live HFSS store is not overwritten.", log)
    else:
        _log("MODE: TEST IN HFSS — live Ansys path. Demonstration store is kept.", log)

    if open_hfss:
        hfss_result = phase(4, "Open/create HFSS project", lambda: run_hfss(solve=solve, log=log)) or hfss_result
        if solve:
            phase(12, "Run HFSS", lambda: hfss_result)
        else:
            _log("PHASE 12: Run HFSS skipped (solve not requested). Model may still be open in AEDT.", log)
            phases.append({"phase": 12, "name": "Run HFSS", "ok": True, "skipped": True})
    else:
        _log("PHASE 4/12: HFSS launch skipped.", log)
        from simulation_runner import write_ironpython_script

        write_ironpython_script()

    if demo_mode:
        results = phase(13, "Load demonstration dataset", load_demonstration) or load_demonstration()
        ensure_live_placeholder()
        publish(results, "demo", make_active=True)
    else:
        results = phase(
            13,
            "Extract live HFSS results",
            lambda: extract(
                hfss_available=bool(hfss_result.get("hfss_available")),
                solved=bool(hfss_result.get("solved")),
            ),
        )
        if results is None:
            results = default_results_payload(
                hfss_available=bool(hfss_result.get("hfss_available")),
                solved=bool(hfss_result.get("solved")),
            )
        results.setdefault("meta", {})["channel"] = "live_hfss"
        publish(results, "live", make_active=True)
        _log("Live HFSS channel updated. Demonstration dataset remains in results/demo/.", log)

    phase(18, "Validate against requirements", lambda: generate_validation(results))
    phase(19, "Generate plots", lambda: generate_plots(results))
    phase(12.5, "Optimization framework (no auto-change of source)", generate_optimization)
    written = phase(20, "Generate HTML dashboard", lambda: generate_reports(results, generate_validation(results)))
    phase(21, "Generate engineering report", lambda: written)
    qa = {"status": "SKIPPED"}
    if run_qa:
        qa = phase(22, "Run QA tests", _run_qa) or qa
    else:
        _log("PHASE 22: QA skipped (GUI action).", log)
    phase(23, "Final project structure ready", lambda: str(repo_root()))

    overall = "NOT SIMULATED"
    if results.get("meta", {}).get("solved"):
        overall = (generate_validation(results) or {}).get("overall_status", "PARTIAL")
    elif results.get("meta", {}).get("demonstration"):
        overall = (generate_validation(results) or {}).get("overall_status", "DEMO")
    summary = {
        "overall_status": overall,
        "mode": mode,
        "phases": phases,
        "hfss": hfss_result,
        "qa": qa,
        "geometry_ok": bool(geom and geom.get("verification", {}).get("all_pass")),
        "dashboard": str(repo_root() / "docs" / "index.html"),
    }
    write_json(repo_root() / "results" / "workflow_summary.json", summary)
    _log(f"FINAL STATUS: {overall}", log)
    return summary


def _run_qa() -> dict:
    import unittest

    loader = unittest.TestLoader()
    suite = loader.discover(str(repo_root() / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    payload = {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "status": "PASS" if result.wasSuccessful() else "FAIL",
    }
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>QA Report</title>
<style>
body{{font-family:Segoe UI,sans-serif;background:#0f1724;color:#e8eef6;padding:24px}}
.site-footer{{margin-top:40px;padding:18px 24px;border-top:1px solid #2b3c55;color:#9fb3c8;font-size:13px;text-align:center;line-height:1.7}}
.site-footer strong{{color:#e8eef6}}
</style>
</head><body>
<h1>QA Report</h1>
<p>Tests run: {payload['tests_run']}. Failures: {payload['failures']}. Errors: {payload['errors']}.</p>
<p>Status: <strong>{payload['status']}</strong></p>
<p>These tests check geometry, setup files and that electromagnetic results are not fabricated.</p>
{footer_html()}
</body></html>
"""
    (repo_root() / "QA_REPORT.html").write_text(html, encoding="utf-8")
    (repo_root() / "docs" / "QA_REPORT.html").write_text(html, encoding="utf-8")
    return payload


if __name__ == "__main__":
    solve = "--solve" in sys.argv
    no_hfss = "--no-hfss" in sys.argv
    mode = "demo" if "--demo" in sys.argv or no_hfss else "live"
    run_all(solve=solve, open_hfss=not no_hfss and mode == "live", mode=mode)
