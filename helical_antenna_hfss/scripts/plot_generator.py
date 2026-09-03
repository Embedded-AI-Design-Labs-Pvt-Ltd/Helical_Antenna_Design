"""Plot generation. Empty electromagnetic plots are watermarked NOT SIMULATED."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

from common import ASSUMPTIONS, SOURCE, repo_root
from geometry_generator import helix_centerline


def _watermark(ax, text: str = "NOT SIMULATED") -> None:
    ax.text(
        0.5,
        0.5,
        text,
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=22,
        color="#c45c26",
        alpha=0.85,
        fontweight="bold",
        rotation=18,
    )


def _style(ax) -> None:
    ax.set_facecolor("#101a28")
    ax.figure.patch.set_facecolor("#0f1724")
    ax.tick_params(colors="#c5d4e6")
    ax.xaxis.label.set_color("#c5d4e6")
    ax.yaxis.label.set_color("#c5d4e6")
    ax.title.set_color("#f4f8ff")
    for spine in ax.spines.values():
        spine.set_color("#2b3c55")
    ax.grid(True, color="#2b3c55", alpha=0.6)


def plot_geometry_3d(path: Path) -> None:
    pts = np.array(helix_centerline())
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], color="#d4a017", lw=2.4, label="Helix centerline")
    theta = np.linspace(0, 2 * np.pi, 180)
    rg = SOURCE["ground_plane_radius_mm"]
    ax.plot(rg * np.cos(theta), rg * np.sin(theta), 0.0, color="#9aa4b2", lw=1.5, label="Ground plane")
    ax.plot_trisurf(
        np.concatenate([rg * np.cos(theta), [0]]),
        np.concatenate([rg * np.sin(theta), [0]]),
        np.concatenate([np.zeros_like(theta), [0]]),
        color="#5c6570",
        alpha=0.35,
    )
    ax.scatter([pts[0, 0]], [pts[0, 1]], [pts[0, 2]], color="#e23", s=40, label="Feed / port")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_zlabel("Z (mm)")
    ax.set_title("3.035 GHz 3-turn helical antenna geometry (CALCULATED)")
    ax.legend(loc="upper left")
    try:
        ax.set_box_aspect((1, 1, 1.1))
    except Exception:
        pass
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def plot_empty_xy(path: Path, title: str, xlabel: str, ylabel: str, x=None, y=None, demo: bool = False) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    _style(ax)
    f0 = SOURCE["operating_frequency_GHz"]
    if x is not None and y is not None and len(x) and all(v is not None for v in y):
        ax.plot(x, y, color="#3d9be9", lw=2)
        ax.axvline(f0, color="#e6b450", ls="--", label="3.035 GHz")
        ax.set_title(title)
        ax.legend()
        if demo:
            ax.text(0.98, 0.05, "DEMO — not HFSS", transform=ax.transAxes, ha="right", color="#e6b450", fontsize=9)
    else:
        ax.axvline(f0, color="#3d7ab8", ls="--", label="3.035 GHz (source)")
        ax.set_xlim(ASSUMPTIONS["sweep_start_GHz"], ASSUMPTIONS["sweep_stop_GHz"])
        ax.set_title(title)
        _watermark(ax)
        ax.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def plot_polar_pattern(path: Path, title: str, peak_db: float | None, demo: bool) -> None:
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, polar=True)
    ax.set_facecolor("#101a28")
    fig.patch.set_facecolor("#0f1724")
    ax.set_title(title, color="#f4f8ff", va="bottom")
    if peak_db is None:
        ax.text(0.5, 0.5, "NOT SIMULATED", transform=ax.transAxes, ha="center", va="center", color="#c45c26", fontsize=16, fontweight="bold")
    else:
        theta = np.linspace(0, np.pi, 181)
        # Axial-mode cardioid-like cut for demonstration (Kraus-style, not HFSS).
        n = 6.0
        pattern = np.clip(np.cos(theta), 0, None) ** n
        db = peak_db + 10.0 * np.log10(np.clip(pattern, 1e-4, None))
        ax.plot(theta, db, color="#3d9be9", lw=2)
        ax.plot(-theta, db, color="#3d9be9", lw=2)
        if demo:
            ax.text(0.5, 0.08, "DEMO — not HFSS", transform=ax.transAxes, ha="center", color="#e6b450", fontsize=9)
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def generate_plots(results: dict | None = None) -> dict[str, str]:
    root = repo_root()
    plots = root / "results" / "plots"
    plots.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    demo = bool((results or {}).get("meta", {}).get("demonstration"))

    geo = plots / "geometry_3d.png"
    plot_geometry_3d(geo)
    written["geometry"] = str(geo)

    sweep = (results or {}).get("sweep") or []
    freq = [row["frequency_GHz"] for row in sweep]
    s11 = [row.get("s11_dB") for row in sweep]
    vswr = [row.get("vswr") for row in sweep]
    ar_f = [row.get("axial_ratio_dB") for row in sweep]
    label = "demonstration dataset" if demo else "HFSS"

    p = plots / "S11.png"
    plot_empty_xy(p, f"S11 (dB) — {label}", "Frequency (GHz)", "S11 (dB)", freq, s11, demo=demo)
    written["s11"] = str(p)

    p = plots / "VSWR.png"
    plot_empty_xy(p, f"VSWR — {label}", "Frequency (GHz)", "VSWR", freq, vswr, demo=demo)
    written["vswr"] = str(p)

    p = plots / "Axial_Ratio.png"
    if ar_f and all(v is not None for v in ar_f) and freq:
        plot_empty_xy(p, f"Axial ratio vs frequency (boresight) — {label}", "Frequency (GHz)", "Axial ratio (dB)", freq, ar_f, demo=demo)
    else:
        plot_empty_xy(p, "Axial ratio vs theta (main-beam cut) — HFSS", "Theta (deg)", "Axial ratio (dB)")
    written["axial_ratio"] = str(p)

    gain = (results or {}).get("gain_dB")
    direc = (results or {}).get("directivity_dBi")
    p = plots / "Gain_Pattern.png"
    plot_polar_pattern(p, "Gain pattern at 3.035 GHz", gain, demo)
    written["gain"] = str(p)

    p = plots / "Directivity_Pattern.png"
    plot_polar_pattern(p, "Directivity pattern at 3.035 GHz", direc, demo)
    written["directivity"] = str(p)

    p = plots / "3D_Radiation_Pattern.png"
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_title("3D radiation pattern at 3.035 GHz", color="#f4f8ff")
    fig.patch.set_facecolor("#0f1724")
    ax.set_facecolor("#101a28")
    if gain is None:
        ax.text2D(0.5, 0.5, "NOT SIMULATED", transform=ax.transAxes, ha="center", color="#c45c26", fontsize=18, fontweight="bold")
    else:
        th = np.linspace(0, np.pi, 73)
        ph = np.linspace(0, 2 * np.pi, 73)
        T, P = np.meshgrid(th, ph)
        n = 6.0
        r = np.clip(np.cos(T), 0, None) ** n
        r = r * (10 ** (gain / 20.0))
        x = r * np.sin(T) * np.cos(P)
        y = r * np.sin(T) * np.sin(P)
        z = r * np.cos(T)
        ax.plot_surface(x, y, z, cmap="YlOrBr", linewidth=0, antialiased=True, alpha=0.9)
        if demo:
            ax.text2D(0.5, 0.02, "DEMO — not HFSS", transform=ax.transAxes, ha="center", color="#e6b450")
    fig.savefig(p, dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    written["pattern3d"] = str(p)

    mesh = (results or {}).get("mesh_convergence") or []
    if mesh:
        p = plots / "mesh_convergence.png"
        fig, ax = plt.subplots(figsize=(8, 5))
        _style(ax)
        ax.plot([r["pass"] for r in mesh], [r["max_delta_s"] for r in mesh], "o-", color="#3d9be9", label="Max Mag. ΔS")
        ax.axhline(0.02, color="#e6b450", ls="--", label="Target 0.02")
        ax.set_xlabel("Adaptive pass")
        ax.set_ylabel("Max Mag. ΔS")
        ax.set_title("Mesh convergence — demonstration")
        ax.legend()
        ax.text(0.98, 0.05, "DEMO — not HFSS", transform=ax.transAxes, ha="right", color="#e6b450", fontsize=9)
        fig.savefig(p, dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        written["mesh"] = str(p)

    shot = root / "results" / "screenshots" / "geometry_preview.png"
    shot.parent.mkdir(parents=True, exist_ok=True)
    plot_geometry_3d(shot)
    written["screenshot"] = str(shot)
    return written


if __name__ == "__main__":
    print(generate_plots())
