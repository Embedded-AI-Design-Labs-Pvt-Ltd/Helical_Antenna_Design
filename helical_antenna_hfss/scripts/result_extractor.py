"""Extract HFSS results. Never invent numbers.

If a quantity cannot be read from a solved project, return NOT_AVAILABLE.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import (
    DESIGN_NAME,
    FAR_FIELD_NAME,
    PROJECT_NAME,
    SETUP_NAME,
    SOURCE,
    SWEEP_NAME,
    default_results_payload,
    find_ansysedt,
    repo_root,
    write_json,
)


NOT_AVAILABLE = "NOT_AVAILABLE"


def _try_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def extract_from_hfss(hfss) -> dict[str, Any]:
    payload = default_results_payload(hfss_available=True, solved=False)
    payload["meta"]["project_name"] = getattr(hfss, "project_name", PROJECT_NAME)
    payload["meta"]["design_name"] = getattr(hfss, "design_name", DESIGN_NAME)
    f0 = SOURCE["operating_frequency_GHz"]
    try:
        solved = bool(hfss.solution_converged) if hasattr(hfss, "solution_converged") else False
    except Exception:
        solved = False

    s11 = None
    vswr = None
    sweep_rows: list[dict[str, Any]] = []
    try:
        data = hfss.post.get_solution_data(
            expressions=["dB(S(1,1))", "VSWR(1)"],
            setup_sweep_name=f"{SETUP_NAME} : {SWEEP_NAME}",
        )
        freqs = list(data.primary_sweep_values)
        mag = list(data.data_real("dB(S(1,1))")) if hasattr(data, "data_real") else list(data.data_magnitude("dB(S(1,1))"))
        vswrs = list(data.data_real("VSWR(1)")) if "VSWR(1)" in getattr(data, "expressions", []) else []
        for i, freq in enumerate(freqs):
            s_val = mag[i] if i < len(mag) else None
            v_val = vswrs[i] if i < len(vswrs) else None
            sweep_rows.append({"frequency_GHz": float(freq), "s11_dB": _try_float(s_val), "vswr": _try_float(v_val)})
        if sweep_rows:
            solved = True
            nearest = min(sweep_rows, key=lambda row: abs(row["frequency_GHz"] - f0))
            s11 = nearest.get("s11_dB")
            vswr = nearest.get("vswr")
            payload["s11_at_3035MHz_dB"] = s11
            payload["vswr_at_3035MHz"] = vswr
            valid_s = [row for row in sweep_rows if row["s11_dB"] is not None]
            if valid_s:
                best = min(valid_s, key=lambda row: row["s11_dB"])
                payload["min_s11_dB"] = best["s11_dB"]
                payload["min_s11_frequency_GHz"] = best["frequency_GHz"]
    except Exception:
        pass

    def far_field_scalar(expr: str) -> float | None:
        try:
            data = hfss.post.get_solution_data(
                expressions=[expr],
                setup_sweep_name=f"{SETUP_NAME} : LastAdaptive",
                domain="Infinite Sphere",
                variations={"Freq": f"{f0}GHz"},
            )
            vals = list(data.data_real(expr))
            return max(vals) if vals else None
        except Exception:
            return None

    gain = far_field_scalar("GainTotal")
    rgain = far_field_scalar("RealizedGainTotal")
    direc = far_field_scalar("DirTotal")
    ar = far_field_scalar("AxialRatio")

    def set_q(key: str, value: float | None, unit: str) -> None:
        payload["quantities"][key]["unit"] = unit
        if value is None:
            payload["quantities"][key]["value"] = None
            payload["quantities"][key]["status"] = NOT_AVAILABLE
            payload["quantities"][key]["provenance"] = "NOT_SIMULATED"
        else:
            payload["quantities"][key]["value"] = value
            payload["quantities"][key]["status"] = "OK"
            payload["quantities"][key]["provenance"] = "HFSS_SIMULATED"
            payload["quantities"][key]["notes"] = f"Extracted from {SETUP_NAME}/{SWEEP_NAME}/{FAR_FIELD_NAME}"

    set_q("s11_dB", s11, "dB")
    set_q("vswr", vswr, "ratio")
    set_q("gain_dB", gain, "dB")
    set_q("realized_gain_dB", rgain, "dB")
    set_q("directivity_dBi", direc, "dBi")
    set_q("axial_ratio_dB", ar, "dB")

    payload["s11_dB"] = s11
    payload["vswr"] = vswr
    payload["gain_dB"] = gain
    payload["realized_gain_dB"] = rgain
    payload["directivity_dBi"] = direc
    payload["axial_ratio_dB"] = ar
    payload["sweep"] = sweep_rows
    payload["meta"]["solved"] = solved
    payload["meta"]["status"] = "PARTIAL" if solved else "NOT SIMULATED"
    payload["meta"]["setup_name"] = SETUP_NAME
    payload["meta"]["sweep_name"] = SWEEP_NAME
    payload["meta"]["far_field_setup"] = FAR_FIELD_NAME
    if solved:
        payload["warnings"] = []
    return payload


def extract(*, hfss=None, hfss_available: bool = False, solved: bool = False, write: bool = True) -> dict[str, Any]:
    if hfss is not None:
        payload = extract_from_hfss(hfss)
    else:
        payload = default_results_payload(
            hfss_available=hfss_available or find_ansysedt() is not None,
            solved=solved,
        )
    if not write:
        return payload
    root = repo_root()
    write_json(root / "results" / "hfss_results.json", payload)
    from results_store import publish

    payload.setdefault("meta", {})["channel"] = "live_hfss"
    publish(payload, "live", make_active=True)
    write_csv(root / "results" / "hfss_results.csv", payload)
    write_sparam_csv(root / "results" / "csv" / "s11.csv", payload, "s11_dB")
    write_sparam_csv(root / "results" / "s11.csv", payload, "s11_dB")
    write_sparam_csv(root / "results" / "csv" / "vswr.csv", payload, "vswr")
    write_sparam_csv(root / "results" / "vswr.csv", payload, "vswr")
    write_sparam_csv(root / "results" / "csv" / "axial_ratio.csv", payload, "axial_ratio_dB")
    return payload


def write_csv(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["quantity", "value", "unit", "status", "provenance"])
        w.writerow(["frequency", payload["frequency_GHz"], "GHz", "SOURCE_SPECIFICATION", "SOURCE_SPECIFICATION"])
        for key, item in payload["quantities"].items():
            val = item.get("value")
            w.writerow([key, "" if val is None else val, item.get("unit", ""), item.get("status"), item.get("provenance")])


def write_sparam_csv(path: Path, payload: dict[str, Any], field: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["frequency_GHz", field, "status", "provenance"])
        sweep = payload.get("sweep") or []
        if not sweep:
            w.writerow([payload["frequency_GHz"], "", "NOT SIMULATED", "NOT_SIMULATED"])
            return
        for row in sweep:
            val = row.get(field)
            w.writerow(
                [
                    row.get("frequency_GHz"),
                    "" if val is None else val,
                    "OK" if val is not None else "NOT_AVAILABLE",
                    "HFSS_SIMULATED" if val is not None else "NOT_SIMULATED",
                ]
            )


if __name__ == "__main__":
    out = extract()
    print("status", out["meta"]["status"])
    print("s11", out["s11_dB"])
