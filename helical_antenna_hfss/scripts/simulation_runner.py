"""Build the HFSS model (PyAEDT or IronPython) and optionally analyze.

Default behavior opens Electronics Desktop GRAPHICALLY so the engineer can
inspect the 3D helical antenna. Solving is opt-in because a full adaptive
sweep is long and must not be faked.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from common import (
    ASSUMPTIONS,
    DESIGN_NAME,
    PROJECT_NAME,
    SETUP_NAME,
    SOURCE,
    airbox_mm,
    find_ansysedt,
    repo_root,
    write_json,
)
from geometry_generator import helix_centerline
from hfss_setup import apply_setup_to_hfss, solver_configuration
from materials_setup import apply_to_hfss as apply_materials
from port_setup import apply_to_hfss as apply_port
from radiation_setup import apply_to_hfss as apply_radiation


LogFn = Callable[[str], None]


def _log(message: str, log: LogFn | None) -> None:
    if log:
        log(message)
    else:
        print(message)


def project_path() -> Path:
    return repo_root() / "hfss" / "project" / f"{PROJECT_NAME}.aedt"


def _import_hfss():
    try:
        from ansys.aedt.core import Hfss  # type: ignore
        return Hfss
    except ImportError:
        from pyaedt import Hfss  # type: ignore
        return Hfss


def build_geometry_on_hfss(hfss) -> None:
    hfss.modeler.model_units = "mm"
    pts = helix_centerline()
    hfss.modeler.create_polyline(
        points=[[x, y, z] for x, y, z in pts],
        name="HelixWire",
        xsection_type="Circle",
        xsection_width=SOURCE["wire_diameter_mm"],
        xsection_num_seg=int(ASSUMPTIONS["helix_cross_section_segments"]),
        matname=ASSUMPTIONS["conductor_material"],
    )
    hfss.modeler.create_cylinder(
        orientation="Z",
        origin=[0.0, 0.0, -ASSUMPTIONS["ground_thickness_mm"]],
        radius=SOURCE["ground_plane_radius_mm"],
        height=ASSUMPTIONS["ground_thickness_mm"],
        name="GroundPlane",
        matname=ASSUMPTIONS["ground_material"],
    )
    apply_port(hfss)
    apply_radiation(hfss)
    apply_materials(hfss)
    apply_setup_to_hfss(hfss)


def build_with_pyaedt(*, solve: bool = False, log: LogFn | None = None) -> dict[str, Any]:
    Hfss = _import_hfss()
    aedt = project_path()
    aedt.parent.mkdir(parents=True, exist_ok=True)
    _log("Launching Ansys Electronics Desktop (graphical HFSS)...", log)
    hfss = Hfss(
        project=str(aedt),
        design=DESIGN_NAME,
        solution_type="DrivenModal",
        new_desktop=True,
        close_on_exit=False,
        non_graphical=os.environ.get("HELIX_HFSS_NONGRAPHICAL") == "1",
    )
    build_geometry_on_hfss(hfss)
    hfss.save_project()
    _log(f"HFSS project saved: {aedt}", log)
    _log("Inspect the 3D helix, ground plane, port sheet and radiation box in the HFSS GUI.", log)
    solved = False
    if solve:
        _log("Analyzing Setup1 — this can take a long time...", log)
        hfss.analyze_setup(SETUP_NAME)
        solved = True
        s1p = repo_root() / "results" / "hfss_helix.s1p"
        try:
            hfss.export_touchstone(output_file=str(s1p))
            _log(f"Exported Touchstone: {s1p}", log)
        except Exception as exc:
            _log(f"Touchstone export failed (model still solved): {exc}", log)
    return {
        "method": "pyaedt",
        "project": str(aedt),
        "solved": solved,
        "hfss_available": True,
        "desktop_open": True,
    }


def write_ironpython_script() -> Path:
    pts = helix_centerline()
    box = airbox_mm()
    r = SOURCE["helix_centerline_radius_mm"]
    gap = ASSUMPTIONS["feed_gap_mm"]
    width = ASSUMPTIONS["port_sheet_width_mm"]
    wire_r = SOURCE["wire_radius_mm"]
    gp_r = SOURCE["ground_plane_radius_mm"]
    gp_t = ASSUMPTIONS["ground_thickness_mm"]
    wd = SOURCE["wire_diameter_mm"]
    f0 = SOURCE["operating_frequency_GHz"]
    npts_sweep = solver_configuration()["frequency_sweep"]["nominal_point_count"]
    point_lines = []
    seg_lines = []
    for i, (x, y, z) in enumerate(pts):
        point_lines.append(
            f'    pl_points.append(["NAME:PLPoint", "X:=", "{x:.8f}mm", "Y:=", "{y:.8f}mm", "Z:=", "{z:.8f}mm"])'
        )
        if i < len(pts) - 1:
            seg_lines.append(
                f'    pl_segs.append(["NAME:PLSegment", "SegmentType:=", "Line", "StartIndex:=", {i}, "NoOfPoints:=", 2])'
            )
    script = f'''# Ansys Electronics Desktop IronPython
# {PROJECT_NAME} — 3.035 GHz 3-turn helical antenna
# Run: AEDT > Tools > Run Script   OR   ansysedt.exe -RunScript this_file.py
# Units: mm. Source dimensions are not modified.
# Feed/port/materials/airbox are ENGINEERING ASSUMPTIONS.

from __future__ import print_function
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop = ScriptEnv.GetDesktop()
oDesktop.RestoreWindow()
oProject = oDesktop.NewProject()
oProject.Rename("{PROJECT_NAME}", True)
oProject.InsertDesign("HFSS", "{DESIGN_NAME}", "DrivenModal", "")
oDesign = oProject.SetActiveDesign("{DESIGN_NAME}")
oEditor = oDesign.SetActiveEditor("3D Modeler")
oEditor.SetModelUnits(["NAME:Units Parameter", "Units:=", "mm", "Rescale:=", False])

pl_points = ["NAME:PolylinePoints"]
pl_segs = ["NAME:PolylineSegments"]
{chr(10).join(point_lines)}
{chr(10).join(seg_lines)}

oEditor.CreatePolyline(
    ["NAME:PolylineParameters", "IsPolylineCovered:=", True, "IsPolylineClosed:=", False,
     pl_points, pl_segs,
     ["NAME:PolylineXSection", "XSectionType:=", "Circle", "XSectionOrient:=", "Auto",
      "XSectionWidth:=", "{wd}mm", "XSectionTopWidth:=", "0mm", "XSectionHeight:=", "0mm",
      "XSectionNumSegments:=", "{int(ASSUMPTIONS['helix_cross_section_segments'])}", "XSectionBendType:=", "Corner"]],
    ["NAME:Attributes", "Name:=", "HelixWire", "Color:=", "(220 160 40)",
     "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"copper\\"", "SolveInside:=", False]
)

oEditor.CreateCylinder(
    ["NAME:CylinderParameters", "XCenter:=", "0mm", "YCenter:=", "0mm",
     "ZCenter:=", "{-gp_t}mm", "Radius:=", "{gp_r}mm", "Height:=", "{gp_t}mm",
     "WhichAxis:=", "Z", "NumSides:=", "0"],
    ["NAME:Attributes", "Name:=", "GroundPlane", "Color:=", "(140 140 140)",
     "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"copper\\"", "SolveInside:=", False]
)

oEditor.CreateCylinder(
    ["NAME:CylinderParameters", "XCenter:=", "{r}mm", "YCenter:=", "0mm",
     "ZCenter:=", "0mm", "Radius:=", "{wire_r}mm", "Height:=", "{gap}mm",
     "WhichAxis:=", "Z", "NumSides:=", "0"],
    ["NAME:Attributes", "Name:=", "FeedPost", "Color:=", "(200 40 40)",
     "PartCoordinateSystem:=", "Global", "MaterialValue:=", "\\"copper\\"", "SolveInside:=", False]
)

oEditor.CreateRectangle(
    ["NAME:RectangleParameters", "IsCovered:=", True,
     "XStart:=", "{r - width/2.0}mm", "YStart:=", "0mm", "ZStart:=", "0mm",
     "Width:=", "{width}mm", "Height:=", "{gap}mm", "WhichAxis:=", "Y"],
    ["NAME:Attributes", "Name:=", "PortSheet", "PartCoordinateSystem:=", "Global",
     "MaterialValue:=", "\\"vacuum\\"", "SolveInside:=", True]
)

oEditor.CreateBox(
    ["NAME:BoxParameters",
     "XPosition:=", "{box['xmin_mm']}mm", "YPosition:=", "{box['ymin_mm']}mm",
     "ZPosition:=", "{box['zmin_mm']}mm",
     "XSize:=", "{box['xsize_mm']}mm", "YSize:=", "{box['ysize_mm']}mm",
     "ZSize:=", "{box['zsize_mm']}mm"],
    ["NAME:Attributes", "Name:=", "RadBox", "PartCoordinateSystem:=", "Global",
     "MaterialValue:=", "\\"vacuum\\"", "SolveInside:=", True, "Transparency:=", 0.9]
)

oModule = oDesign.GetModule("BoundarySetup")
oModule.AssignLumpedPort(
    ["NAME:P1", "Objects:=", ["PortSheet"], "RenormalizeAllTerminals:=", True, "DoDeembed:=", False,
     ["NAME:Modes", ["NAME:Mode1", "ModeNum:=", 1, "UseIntLine:=", True,
      ["NAME:IntLine",
       "Start:=", ["{r}mm", "0mm", "0mm"],
       "End:=", ["{r}mm", "0mm", "{gap}mm"]],
      "CharImp:=", "Zpi"]],
     "Resistance:=", "{ASSUMPTIONS['port_impedance_ohm']}ohm", "Reactance:=", "0ohm"]
)
oModule.AssignRadiation(["NAME:Rad1", "Objects:=", ["RadBox"], "IsFssReference:=", False, "IsForPML:=", False])

oModule = oDesign.GetModule("AnalysisSetup")
oModule.InsertSetup("HfssDriven",
    ["NAME:Setup1", "AdaptMultipleFreqs:=", False, "Frequency:=", "{f0}GHz",
     "MaxDeltaS:=", {ASSUMPTIONS['max_delta_s']}, "MaximumPasses:=", {int(ASSUMPTIONS['max_passes'])},
     "MinimumPasses:=", {int(ASSUMPTIONS['min_passes'])}, "MinimumConvergedPasses:=", {int(ASSUMPTIONS['min_converged_passes'])},
     "PercentRefinement:=", {int(ASSUMPTIONS['percent_refinement'])}, "BasisOrder:=", {int(ASSUMPTIONS['basis_order'])}])
oModule.InsertFrequencySweep("Setup1",
    ["NAME:Sweep", "IsEnabled:=", True, "RangeType:=", "LinearCount",
     "RangeStart:=", "{ASSUMPTIONS['sweep_start_GHz']}GHz", "RangeEnd:=", "{ASSUMPTIONS['sweep_stop_GHz']}GHz",
     "RangeCount:=", {int(npts_sweep)}, "Type:=", "Interpolating",
     "SaveFields:=", False, "SaveRadFields:=", True,
     "InterpTolerance:=", 0.5, "InterpMaxSolns:=", 50, "InterpMinSolns:=", 0, "InterpMinSubranges:=", 1])

oModule = oDesign.GetModule("RadField")
oModule.InsertInfiniteSphereSetup(
    ["NAME:Infinite Sphere1", "UseCustomRadiationSurface:=", False,
     "ThetaStart:=", "0deg", "ThetaStop:=", "180deg", "ThetaStep:=", "5deg",
     "PhiStart:=", "-180deg", "PhiStop:=", "180deg", "PhiStep:=", "10deg", "UseLocalCS:=", False]
)

print("HFSS helical antenna model built. Inspect geometry in the 3D Modeler.")
print("Do not treat unsolved S11/gain/AR as results. Analyze Setup1 when ready.")
'''
    path = repo_root() / "hfss" / "project" / "build_helix_hfss.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(script, encoding="utf-8")
    bat = repo_root() / "hfss" / "project" / "open_in_ansys.bat"
    bat.write_text(
        "@echo off\r\n"
        "set SCRIPT=%~dp0build_helix_hfss.py\r\n"
        "where ansysedt >nul 2>&1\r\n"
        "if %ERRORLEVEL%==0 (\r\n"
        "  echo Opening Ansys Electronics Desktop with helical antenna script...\r\n"
        "  start \"\" ansysedt -RunScript \"%SCRIPT%\"\r\n"
        "  goto :eof\r\n"
        ")\r\n"
        "echo ansysedt.exe not on PATH. Open Electronics Desktop, then:\r\n"
        "echo   Tools ^> Run Script ^> %SCRIPT%\r\n"
        "pause\r\n",
        encoding="utf-8",
    )
    return path


def launch_ansys_script(script: Path, log: LogFn | None = None) -> dict[str, Any]:
    exe = find_ansysedt()
    if exe is None:
        return {"method": "ansysedt", "hfss_available": False, "solved": False, "error": "ansysedt.exe not found"}
    _log(f"Found AEDT: {exe}", log)
    _log("Starting Ansys Electronics Desktop so you can inspect the 3D design...", log)
    subprocess.Popen([str(exe), "-RunScript", str(script)], cwd=str(script.parent))
    return {
        "method": "ansysedt_RunScript",
        "hfss_available": True,
        "solved": False,
        "desktop_open": True,
        "executable": str(exe),
        "script": str(script),
    }


def run(*, solve: bool = False, log: LogFn | None = None) -> dict[str, Any]:
    script = write_ironpython_script()
    _log(f"Wrote AEDT script: {script}", log)
    pyaedt_ok = False
    try:
        _import_hfss()
        pyaedt_ok = True
    except Exception:
        pyaedt_ok = False

    result: dict[str, Any]
    if pyaedt_ok and find_ansysedt() is not None:
        try:
            result = build_with_pyaedt(solve=solve, log=log)
        except Exception as exc:
            _log(f"PyAEDT build failed ({exc}). Falling back to ansysedt -RunScript.", log)
            result = launch_ansys_script(script, log=log)
            result["pyaedt_error"] = str(exc)
    elif find_ansysedt() is not None:
        result = launch_ansys_script(script, log=log)
    else:
        _log("Ansys Electronics Desktop was not found on this computer.", log)
        _log("Install AEDT/HFSS, or open Tools > Run Script on build_helix_hfss.py.", log)
        result = {
            "method": "offline",
            "hfss_available": False,
            "solved": False,
            "desktop_open": False,
            "script": str(script),
            "message": "NOT SIMULATED — Ansys HFSS is not installed or not on PATH.",
        }
    result["ironpython_script"] = str(script)
    write_json(repo_root() / "hfss" / "project" / "last_run.json", result)
    return result


if __name__ == "__main__":
    solve = "--solve" in sys.argv
    print(run(solve=solve))
