"""Keep demonstration and live HFSS result stores separate.

results/demo/hfss_results.json  — ready-made modified-antenna dataset
results/live/hfss_results.json  — Ansys HFSS extract (or NOT SIMULATED)
results/hfss_results.json       — currently active view (dashboard/plots)
results/active_source.json      — {"source": "demo"|"live"}
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Literal

from common import default_results_payload, repo_root, write_json

Source = Literal["demo", "live"]


def demo_path() -> Path:
    p = repo_root() / "results" / "demo"
    p.mkdir(parents=True, exist_ok=True)
    return p / "hfss_results.json"


def live_path() -> Path:
    p = repo_root() / "results" / "live"
    p.mkdir(parents=True, exist_ok=True)
    return p / "hfss_results.json"


def active_path() -> Path:
    return repo_root() / "results" / "hfss_results.json"


def flag_path() -> Path:
    return repo_root() / "results" / "active_source.json"


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_demo() -> dict[str, Any] | None:
    return read_json(demo_path())


def load_live() -> dict[str, Any] | None:
    return read_json(live_path())


def active_source() -> Source:
    data = read_json(flag_path()) or {}
    src = data.get("source", "demo")
    return "live" if src == "live" else "demo"


def save_store(payload: dict[str, Any], source: Source) -> Path:
    path = demo_path() if source == "demo" else live_path()
    write_json(path, payload)
    return path


def publish(payload: dict[str, Any], source: Source, *, make_active: bool = True) -> dict[str, Any]:
    save_store(payload, source)
    if make_active:
        write_json(active_path(), payload)
        write_json(flag_path(), {"source": source, "demonstration": source == "demo"})
        dest = repo_root() / "results" / source
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(active_path(), dest / "hfss_results.json")
    return payload


def ensure_live_placeholder() -> dict[str, Any]:
    existing = load_live()
    if existing is not None:
        return existing
    payload = default_results_payload(hfss_available=False, solved=False)
    payload["meta"]["channel"] = "live_hfss"
    save_store(payload, "live")
    return payload


def both() -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    return load_demo(), load_live()
