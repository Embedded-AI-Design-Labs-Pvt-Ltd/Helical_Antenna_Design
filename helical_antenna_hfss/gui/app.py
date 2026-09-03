"""Desktop GUI: one RUN button builds the helical antenna and opens Ansys HFSS."""

from __future__ import annotations

import json
import sys
import threading
import traceback
import webbrowser
from pathlib import Path

import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
except ImportError as exc:  # pragma: no cover
    raise SystemExit("tkinter is required for the GUI") from exc

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from common import (  # noqa: E402
    ASSUMPTIONS,
    AUTHOR_EMAIL,
    AUTHOR_NAME,
    AUTHOR_PHONE,
    COMPANY_NAME,
    PRODUCT_TITLE,
    SOURCE,
    TARGETS,
    find_ansysedt,
    footer_plain,
    repo_root,
)
from geometry_generator import helix_centerline  # noqa: E402
from workflow import run_all  # noqa: E402

BG = "#0f1724"
PANEL = "#132033"
TEXT = "#e8eef6"
ACCENT = "#1f4e79"
DEMO_BTN = "#b8860b"
TEST_BTN = "#2ea043"

class HelixGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{PRODUCT_TITLE} — {COMPANY_NAME}")
        self.configure(bg=BG)
        self.geometry("1480x920")
        self.minsize(1100, 720)
        self._busy = False
        self._build()
        self._draw_geometry()
        self.after(200, self._status_ansys)

    def _build(self) -> None:
        header = tk.Frame(self, bg="#0b1220")
        header.pack(fill="x")
        tk.Label(
            header,
            text="3.035 GHz HELICAL ANTENNA  ·  ANSYS HFSS DESIGN AUTOMATION",
            bg="#0b1220",
            fg="#f4f8ff",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(12, 0))
        tk.Label(
            header,
            text=f"{COMPANY_NAME}  |  Author: {AUTHOR_NAME}  |  {AUTHOR_EMAIL}  |  {AUTHOR_PHONE}",
            bg="#0b1220",
            fg="#9fb3c8",
            font=("Segoe UI", 10),
        ).pack(pady=(0, 10))

        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=12, pady=8)
        self.demo_btn = tk.Button(
            bar,
            text="  DEMONSTRATE  —  EXISTING DATA  ",
            command=self.on_demonstrate,
            bg=DEMO_BTN,
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            padx=14,
            pady=10,
            cursor="hand2",
        )
        self.demo_btn.pack(side="left")
        self.test_btn = tk.Button(
            bar,
            text="  TEST IN HFSS  —  LIVE ANSYS  ",
            command=self.on_test_hfss,
            bg=TEST_BTN,
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            padx=14,
            pady=10,
            cursor="hand2",
        )
        self.test_btn.pack(side="left", padx=(8, 0))
        self.solve_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            bar,
            text="Solve in HFSS (long)",
            variable=self.solve_var,
            bg=BG,
            fg=TEXT,
            selectcolor=PANEL,
            activebackground=BG,
            activeforeground=TEXT,
        ).pack(side="left", padx=12)
        tk.Button(bar, text="Show Demo", command=lambda: self.on_show("demo"), bg=ACCENT, fg="white", relief="flat", padx=10, pady=8).pack(side="left", padx=4)
        tk.Button(bar, text="Show Live", command=lambda: self.on_show("live"), bg=ACCENT, fg="white", relief="flat", padx=10, pady=8).pack(side="left", padx=4)
        tk.Button(bar, text="Dashboard", command=self.on_dashboard, bg=ACCENT, fg="white", relief="flat", padx=10, pady=8).pack(side="left", padx=4)
        tk.Button(bar, text="HFSS script", command=self.on_script, bg=ACCENT, fg="white", relief="flat", padx=10, pady=8).pack(side="left", padx=4)
        tk.Button(bar, text="Report", command=self.on_report, bg=ACCENT, fg="white", relief="flat", padx=10, pady=8).pack(side="left", padx=4)

        self.status = tk.Label(self, text="Ready. Demonstrate = existing data. Test in HFSS = live Ansys.", bg=BG, fg="#c9d7ea", anchor="w", font=("Segoe UI", 10))
        self.status.pack(fill="x", padx=16)

        body = tk.PanedWindow(self, orient="horizontal", bg=BG, sashwidth=6)
        body.pack(fill="both", expand=True, padx=8, pady=8)

        left = tk.Frame(body, bg=PANEL)
        center = tk.Frame(body, bg=PANEL)
        right = tk.Frame(body, bg=PANEL)
        body.add(left, minsize=280, width=320)
        body.add(center, minsize=420, width=640)
        body.add(right, minsize=320, width=420)

        self._params(left)
        self._canvas(center)
        self._results(right)

        log_fr = tk.LabelFrame(self, text="Workflow log", bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold"))
        log_fr.pack(fill="both", expand=False, padx=8, pady=(0, 8))
        self.log = tk.Text(log_fr, height=10, bg="#101a28", fg="#c5d4e6", insertbackground="white", relief="flat")
        self.log.pack(fill="both", expand=True, padx=6, pady=6)
        self._log("Source parameters locked. Use DEMONSTRATE for existing data, TEST IN HFSS for live Ansys.")
        self._log("Both result stores are kept: results/demo/ and results/live/.")

        footer = tk.Label(
            self,
            text=footer_plain(),
            bg="#0b1220",
            fg="#9fb3c8",
            font=("Segoe UI", 10),
            pady=10,
            wraplength=1400,
            justify="center",
        )
        footer.pack(fill="x", side="bottom")

    def _params(self, parent: tk.Frame) -> None:
        tk.Label(parent, text="SOURCE PARAMETERS (locked)", bg=PANEL, fg="#9fb3c8", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=10, pady=(10, 4))
        rows = [
            ("Frequency", f"{SOURCE['operating_frequency_GHz']} GHz"),
            ("Turns", f"{SOURCE['number_of_turns']}"),
            ("Helix radius", f"{SOURCE['helix_centerline_radius_mm']} mm"),
            ("Pitch", f"{SOURCE['pitch_mm']} mm"),
            ("Wire", f"18 AWG · Ø {SOURCE['wire_diameter_mm']} mm"),
            ("Ground radius", f"{SOURCE['ground_plane_radius_mm']} mm"),
            ("Ground diameter", f"{SOURCE['ground_plane_diameter_mm']} mm"),
            ("Axial length", f"{SOURCE['total_axial_length_mm']} mm"),
            ("C / turn", f"{SOURCE['circumference_per_turn_mm']} mm"),
            ("Slant / turn", f"{SOURCE['slant_length_per_turn_mm']} mm"),
            ("Pitch angle", f"{SOURCE['pitch_angle_deg']}°"),
        ]
        for k, v in rows:
            row = tk.Frame(parent, bg=PANEL)
            row.pack(fill="x", padx=10, pady=1)
            tk.Label(row, text=k, bg=PANEL, fg="#9fb3c8", width=16, anchor="w").pack(side="left")
            tk.Label(row, text=v, bg=PANEL, fg=TEXT, anchor="w", font=("Consolas", 10)).pack(side="left")

        tk.Label(parent, text="ASSUMED (not in source)", bg=PANEL, fg="#e6b450", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=10, pady=(14, 4))
        assumed = [
            ("Feed", "50 Ω lumped port"),
            ("Feed gap", f"{ASSUMPTIONS['feed_gap_mm']} mm"),
            ("Ground thickness", f"{ASSUMPTIONS['ground_thickness_mm']} mm"),
            ("Material", "copper"),
            ("Air-box pad", "0.5 λ0"),
            ("Sweep", "2.50–4.00 GHz"),
        ]
        for k, v in assumed:
            row = tk.Frame(parent, bg=PANEL)
            row.pack(fill="x", padx=10, pady=1)
            tk.Label(row, text=k, bg=PANEL, fg="#e6b450", width=16, anchor="w").pack(side="left")
            tk.Label(row, text=v, bg=PANEL, fg=TEXT, anchor="w", font=("Consolas", 10)).pack(side="left")

        tk.Label(parent, text="TARGETS", bg=PANEL, fg="#9fb3c8", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=10, pady=(14, 4))
        for line in (
            f"S11 ≤ {TARGETS['s11_max_dB']} dB",
            f"VSWR {TARGETS['vswr_min']}:{1}–{TARGETS['vswr_max']}:1",
            f"Directivity {TARGETS['directivity_min_dBi']}–{TARGETS['directivity_max_dBi']} dBi",
            f"Gain {TARGETS['gain_min_dB']}–{TARGETS['gain_max_dB']} dB",
            f"Axial ratio < {TARGETS['axial_ratio_max_dB']} dB",
        ):
            tk.Label(parent, text=line, bg=PANEL, fg=TEXT, anchor="w").pack(fill="x", padx=10)

    def _canvas(self, parent: tk.Frame) -> None:
        tk.Label(parent, text="3D GEOMETRY PREVIEW (CALCULATED)", bg=PANEL, fg="#9fb3c8", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=8, pady=8)
        self.fig = plt.Figure(figsize=(6.2, 6.2), facecolor="#0b1220")
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        NavigationToolbar2Tk(self.canvas, parent).update()

    def _results(self, parent: tk.Frame) -> None:
        tk.Label(parent, text="DEMO vs LIVE HFSS", bg=PANEL, fg="#9fb3c8", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=10, pady=(10, 4))
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background="#101a28", fieldbackground="#101a28", foreground=TEXT, rowheight=26)
        style.configure("Treeview.Heading", background="#1c2e45", foreground=TEXT)
        self.tree = ttk.Treeview(parent, columns=("p", "t", "d", "l"), show="headings", height=10)
        for cid, text, w in (
            ("p", "Parameter", 80),
            ("t", "Target", 90),
            ("d", "Demo", 110),
            ("l", "Live HFSS", 110),
        ):
            self.tree.heading(cid, text=text)
            self.tree.column(cid, width=w, stretch=True)
        self.tree.pack(fill="both", expand=True, padx=10, pady=6)
        self.ansys_lbl = tk.Label(parent, text="Ansys: checking...", bg=PANEL, fg="#e6b450", wraplength=360, justify="left")
        self.ansys_lbl.pack(fill="x", padx=10, pady=8)
        self._refresh_results_table()

    def _refresh_results_table(self) -> None:
        from results_store import active_source, load_demo, load_live

        demo = load_demo() or {}
        live = load_live() or {}
        active = active_source()

        def cell(store: dict, key: str, unit: str = "") -> str:
            val = store.get(key)
            if val is None:
                return "NOT SIMULATED"
            return f"{val:.3g} {unit}".strip()

        rows = [
            ("S11", "≤ -15 dB", cell(demo, "s11_dB", "dB"), cell(live, "s11_dB", "dB")),
            ("VSWR", "1.1–1.4", cell(demo, "vswr"), cell(live, "vswr")),
            ("Gain", "9.5–14.0 dB", cell(demo, "gain_dB", "dB"), cell(live, "gain_dB", "dB")),
            ("Directivity", "10–14.5 dBi", cell(demo, "directivity_dBi", "dBi"), cell(live, "directivity_dBi", "dBi")),
            ("Axial ratio", "< 1.5 dB", cell(demo, "axial_ratio_dB", "dB"), cell(live, "axial_ratio_dB", "dB")),
        ]
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=row)
        self.ansys_lbl.configure(
            text=f"Active view: {active.upper()}\nDemo file: results/demo/\nLive file: results/live/\nDemonstrate and Test keep both stores.",
            fg="#e6b450",
        )

    def _draw_geometry(self) -> None:
        ax = self.ax
        ax.clear()
        ax.set_facecolor("#101a28")
        pts = np.array(helix_centerline())
        ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], color="#d4a017", lw=2.6)
        theta = np.linspace(0, 2 * np.pi, 180)
        rg = SOURCE["ground_plane_radius_mm"]
        ax.plot(rg * np.cos(theta), rg * np.sin(theta), np.zeros_like(theta), color="#9aa4b2", lw=1.2)
        ax.scatter([pts[0, 0]], [pts[0, 1]], [pts[0, 2]], color="#e23", s=35)
        ax.set_xlabel("X mm", color="#c5d4e6")
        ax.set_ylabel("Y mm", color="#c5d4e6")
        ax.set_zlabel("Z mm", color="#c5d4e6")
        ax.tick_params(colors="#9fb3c8")
        ax.set_title("Helix + ground (source geometry)", color="#f4f8ff")
        try:
            ax.set_box_aspect((1, 1, 1.15))
        except Exception:
            pass
        self.canvas.draw_idle()

    def _status_ansys(self) -> None:
        exe = find_ansysedt()
        extra = f"Ansys found:\n{exe}" if exe else "Ansys Electronics Desktop was not found on this PC."
        self._refresh_results_table()
        current = self.ansys_lbl.cget("text")
        self.ansys_lbl.configure(text=f"{current}\n{extra}")

    def _log(self, msg: str) -> None:
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.update_idletasks()

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = "disabled" if busy else "normal"
        self.demo_btn.configure(state=state, bg=("#555" if busy else DEMO_BTN))
        self.test_btn.configure(state=state, bg=("#555" if busy else TEST_BTN))

    def on_demonstrate(self) -> None:
        self._start_job("demo")

    def on_test_hfss(self) -> None:
        self._start_job("live")

    def _start_job(self, mode: str) -> None:
        if self._busy:
            return
        self._set_busy(True)
        self.status.configure(text=f"Running {mode} workflow...")
        solve = bool(self.solve_var.get()) if mode == "live" else False

        def work() -> None:
            try:
                summary = run_all(
                    solve=solve,
                    open_hfss=(mode == "live"),
                    mode=mode,
                    run_qa=False,
                    log=lambda m: self.after(0, self._log, m),
                )
                self.after(0, lambda: self._done(summary, None, mode))
            except Exception:
                err = traceback.format_exc()
                self.after(0, lambda: self._done(None, err, mode))

        threading.Thread(target=work, daemon=True).start()

    def on_show(self, source: str) -> None:
        from plot_generator import generate_plots
        from report_generator import generate as generate_reports
        from results_store import load_demo, load_live, publish
        from validation import generate as generate_validation

        data = load_demo() if source == "demo" else load_live()
        if not data:
            self._log(f"No {source} dataset yet. Press Demonstrate or Test in HFSS first.")
            messagebox.showinfo("No data", f"No {source} results stored yet.")
            return
        publish(data, "demo" if source == "demo" else "live", make_active=True)
        generate_plots(data)
        generate_reports(data, generate_validation(data))
        self._refresh_results_table()
        self.status.configure(text=f"Active view: {source.upper()}")
        self._log(f"Switched active view to {source} without deleting the other store.")

    def on_run(self) -> None:
        self.on_test_hfss()

    def _done(self, summary, err, mode: str = "live") -> None:
        self._set_busy(False)
        if err:
            self.status.configure(text="Workflow error — see log.")
            self._log(err)
            messagebox.showerror("HFSS workflow", "A Python error occurred. See the log.")
            return
        status = (summary or {}).get("overall_status", "NOT SIMULATED")
        self.status.configure(text=f"Finished ({mode}). Status: {status}")
        self._refresh_results_table()
        dash = repo_root() / "docs" / "index.html"
        if dash.is_file():
            webbrowser.open(dash.as_uri())
        hfss = (summary or {}).get("hfss") or {}
        if mode == "demo":
            messagebox.showinfo(
                "Demonstrate",
                f"Status: {status}\n\n"
                "Existing modified-antenna dataset is active.\n"
                "Live HFSS results were not overwritten.\n"
                "Use TEST IN HFSS for Ansys.",
            )
        elif hfss.get("desktop_open"):
            messagebox.showinfo(
                "Test in HFSS",
                "The helical antenna model was sent to Ansys Electronics Desktop.\n\n"
                "Inspect HelixWire, GroundPlane, PortSheet and RadBox.\n"
                "Demonstration data remains in results/demo/.",
            )
        else:
            messagebox.showinfo(
                "Test in HFSS",
                f"Status: {status}\n\n"
                "Live channel updated (NOT SIMULATED until Analyze Setup1).\n"
                "Demonstration data remains in results/demo/.\n\n"
                f"Script: {repo_root() / 'hfss' / 'project' / 'build_helix_hfss.py'}",
            )

    def on_dashboard(self) -> None:
        path = repo_root() / "docs" / "index.html"
        if not path.is_file():
            self._log("Dashboard not generated yet. Press RUN first.")
            return
        webbrowser.open(path.as_uri())

    def on_report(self) -> None:
        path = repo_root() / "reports" / "Helical_Antenna_HFSS_Report.html"
        if not path.is_file():
            self._log("Report not generated yet. Press RUN first.")
            return
        webbrowser.open(path.as_uri())

    def on_script(self) -> None:
        path = repo_root() / "hfss" / "project" / "build_helix_hfss.py"
        if not path.is_file():
            from simulation_runner import write_ironpython_script

            path = write_ironpython_script()
        try:
            os_start(path)
        except Exception:
            webbrowser.open(path.as_uri())


def os_start(path: Path) -> None:
    import os

    os.startfile(path)  # type: ignore[attr-defined]


def main() -> None:
    app = HelixGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
