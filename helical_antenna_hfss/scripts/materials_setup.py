"""Materials assignment for the helical antenna HFSS model.

The source document does not specify conductor conductivity, surface finish,
or dielectric materials. Defaults below are engineering assumptions.
"""

from __future__ import annotations

from common import ASSUMPTIONS, SOURCE, repo_root, write_json, wavelength_mm


def materials_definition() -> dict:
    use_pec = bool(ASSUMPTIONS["use_pec"])
    conductor = "pec" if use_pec else ASSUMPTIONS["conductor_material"]
    return {
        "source_document_defines_materials": False,
        "pec_is_source_requirement": False,
        "wavelength_mm_at_3035_MHz": wavelength_mm(),
        "objects": {
            "HelixWire": {
                "material": conductor,
                "solve_inside": False,
                "provenance": "ENGINEERING_ASSUMPTION",
                "notes": "18 AWG copper is the usual physical interpretation of the source wire gauge, but the document does not name the metal.",
            },
            "GroundPlane": {
                "material": "pec" if use_pec else ASSUMPTIONS["ground_material"],
                "solve_inside": False,
                "provenance": "ENGINEERING_ASSUMPTION",
            },
            "FeedPost": {
                "material": conductor,
                "solve_inside": False,
                "provenance": "ENGINEERING_ASSUMPTION",
            },
            "RadBox": {
                "material": ASSUMPTIONS["air_material"],
                "solve_inside": True,
                "provenance": "ENGINEERING_ASSUMPTION",
            },
            "PortSheet": {
                "material": ASSUMPTIONS["air_material"],
                "solve_inside": True,
                "notes": "Sheet used only as a port assignment; not a bulk dielectric.",
            },
        },
        "copper_conductivity_S_per_m": ASSUMPTIONS["copper_conductivity_S_per_m"],
        "if_pec_used": {
            "meaning": "Perfect electric conductor. Zero loss. Gain equals directivity in a lossless model.",
            "used_in_this_project": use_pec,
            "not_a_source_requirement": True,
        },
        "operating_frequency_GHz": SOURCE["operating_frequency_GHz"],
    }


def generate() -> dict:
    data = materials_definition()
    write_json(repo_root() / "hfss" / "setup" / "materials.json", data)
    return data


def apply_to_hfss(hfss) -> None:
    data = materials_definition()
    for name, spec in data["objects"].items():
        if name not in hfss.modeler.object_names:
            continue
        try:
            hfss.assign_material(name, spec["material"])
        except Exception:
            pass


if __name__ == "__main__":
    d = generate()
    print("Materials:", {k: v["material"] for k, v in d["objects"].items()})
