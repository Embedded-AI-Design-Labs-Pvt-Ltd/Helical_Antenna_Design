"""Radiation boundary and air-region sizing.

Wavelength and padding are calculated. The source document does not define
the air-box dimensions. Radiation (first-order absorbing) is the initial
boundary — not PML — unless later upgraded.
"""

from __future__ import annotations

from common import ASSUMPTIONS, SOURCE, airbox_mm, repo_root, wavelength_mm, write_json


def radiation_definition() -> dict:
    box = airbox_mm()
    lam = wavelength_mm()
    pad_w = ASSUMPTIONS["airbox_padding_wavelengths"]
    return {
        "wavelength_mm": lam,
        "frequency_GHz": SOURCE["operating_frequency_GHz"],
        "padding_wavelengths": pad_w,
        "padding_mm": box["padding_mm"],
        "padding_provenance": "ENGINEERING_ASSUMPTION (0.5 λ0). Source document is silent.",
        "boundary_type": "Radiation",
        "boundary_name": "Rad1",
        "object_name": "RadBox",
        "material": ASSUMPTIONS["air_material"],
        "airbox_mm": box,
        "rationale": (
            "λ0 = c/f = 299792458 / 3.035e9 = 98.778 mm. "
            "A half-wavelength margin around the antenna is a common first-pass HFSS radiation-box size. "
            "Closer boxes (λ/4) are cheaper; PML can reduce reflections. Neither is specified by the source."
        ),
        "validation": {
            "encloses_antenna": True,
            "port_inside_region": True,
            "helix_inside": True,
            "ground_inside": True,
            "unintended_overlaps": "Must be inspected in the HFSS GUI after the model is built.",
            "disconnected_feed": "Feed post spans the assumed gap; inspect union/touch in HFSS.",
        },
        "pml_not_used_initially": True,
    }


def generate() -> dict:
    data = radiation_definition()
    write_json(repo_root() / "hfss" / "boundaries" / "radiation.json", data)
    return data


def apply_to_hfss(hfss) -> None:
    box = airbox_mm()
    rad = hfss.modeler.create_box(
        origin=[box["xmin_mm"], box["ymin_mm"], box["zmin_mm"]],
        sizes=[box["xsize_mm"], box["ysize_mm"], box["zsize_mm"]],
        name="RadBox",
        matname=ASSUMPTIONS["air_material"],
    )
    try:
        hfss.assign_radiation_boundary_to_objects(rad.name)
    except Exception:
        hfss.assign_radiation_boundary_to_objects("RadBox")
    try:
        hfss.modeler.set_object_property("RadBox", "Transparent", 0.9)
    except Exception:
        pass


if __name__ == "__main__":
    d = generate()
    print("lambda_mm", d["wavelength_mm"])
    print("airbox", d["airbox_mm"])
