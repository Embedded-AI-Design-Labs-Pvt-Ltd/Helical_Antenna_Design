"""50-ohm lumped-port feed for the helical antenna.

The source document does NOT specify coax geometry, connector, dielectric,
reference impedance, port dimensions, or integration line. Those values are
engineering assumptions documented here and in ENGINEERING_ASSUMPTIONS.md.
"""

from __future__ import annotations

from common import ASSUMPTIONS, SOURCE, airbox_mm, repo_root, write_json


MISSING_FROM_SOURCE = [
    "coax inner/outer conductor radii",
    "coax dielectric material and permittivity",
    "connector type (SMA, N, custom)",
    "feed probe diameter independent of helix wire",
    "reference impedance",
    "port sheet dimensions",
    "integration-line start and end",
    "feed gap between helix start and ground plane",
    "ground-plane thickness and via/clearance hole",
]


def port_definition() -> dict:
    r = SOURCE["helix_centerline_radius_mm"]
    gap = ASSUMPTIONS["feed_gap_mm"]
    width = ASSUMPTIONS["port_sheet_width_mm"]
    z0 = ASSUMPTIONS["port_impedance_ohm"]
    wire_r = SOURCE["wire_radius_mm"]
    return {
        "provenance": "ENGINEERING_ASSUMPTION",
        "source_document_defines_feed": False,
        "missing_from_source": MISSING_FROM_SOURCE,
        "first_pass_excitation": {
            "type": "lumped_port",
            "name": "P1",
            "impedance_ohm": z0,
            "renormalize": True,
            "feed_gap_mm": gap,
            "port_sheet": {
                "name": "PortSheet",
                "plane": "XZ (Y=0)",
                "origin_mm": [r - width / 2.0, 0.0, 0.0],
                "width_mm": width,
                "height_mm": gap,
                "description": "Rectangle spanning the gap between the ground-plane top (z=0) and the helix start (z=feed_gap) at the helix radius.",
            },
            "integration_line": {
                "start_mm": [r, 0.0, 0.0],
                "end_mm": [r, 0.0, gap],
                "direction": "+z from ground to helix start",
                "notes": "Positive voltage is helix relative to ground.",
            },
            "feed_post": {
                "name": "FeedPost",
                "radius_mm": wire_r,
                "axis": "z",
                "origin_mm": [r, 0.0, 0.0],
                "height_mm": gap,
                "purpose": "Vertical conductor in the gap so the helix is galvanically connected to the port sheet. The post does not penetrate the ground; the lumped port provides the excitation across the gap.",
            },
            "orientation": "Port sheet normal is +Y. Integration line is +Z.",
        },
        "how_to_replace_with_coax": {
            "when": "Physical connector drawings or measured coax dimensions become available.",
            "steps": [
                "Delete lumped port P1 and PortSheet.",
                "Create coaxial inner conductor, dielectric, and outer shield using the measured radii.",
                "Subtract dielectric from shield and inner from dielectric.",
                "Cut a clearance hole in the ground plane for the shield.",
                "Assign a wave port or lumped port on the coaxial cross-section at the connector end.",
                "Set the integration line from inner to outer conductor.",
                "Re-solve. S11/VSWR will change; far-field shape usually less so.",
            ],
        },
        "validation_checks": [
            "Port sheet touches both the ground plane (or is adjacent to z=0) and the helix/feed-post conductor.",
            "Port sheet is a 2D sheet, not a solid.",
            "Integration line lies on the port sheet.",
            "Port impedance is 50 ohm.",
            "Port is inside the radiation box.",
            "No unintended short between helix and ground except through the port.",
        ],
        "airbox_contains_port": True,
        "airbox_mm": airbox_mm(),
    }


def generate() -> dict:
    data = port_definition()
    root = repo_root()
    write_json(root / "hfss" / "ports" / "port_definition.json", data)
    return data


def apply_to_hfss(hfss) -> None:
    """Create feed post, port sheet, and 50-ohm lumped port on a live PyAEDT Hfss object."""
    r = SOURCE["helix_centerline_radius_mm"]
    gap = ASSUMPTIONS["feed_gap_mm"]
    width = ASSUMPTIONS["port_sheet_width_mm"]
    wire_r = SOURCE["wire_radius_mm"]
    z0 = ASSUMPTIONS["port_impedance_ohm"]
    mat = ASSUMPTIONS["conductor_material"]
    hfss.modeler.create_cylinder(
        orientation="Z",
        origin=[r, 0.0, 0.0],
        radius=wire_r,
        height=gap,
        name="FeedPost",
        matname=mat,
    )
    sheet = hfss.modeler.create_rectangle(
        orientation="XZ",
        origin=[r - width / 2.0, 0.0, 0.0],
        sizes=[width, gap],
        name="PortSheet",
    )
    try:
        hfss.lumped_port(
            assignment=sheet.name,
            impedance=z0,
            name="P1",
            renormalize=True,
        )
    except TypeError:
        hfss.lumped_port(sheet.name, impedance=z0, name="P1")


if __name__ == "__main__":
    d = generate()
    print("Feed type:", d["first_pass_excitation"]["type"], d["first_pass_excitation"]["impedance_ohm"], "ohm")
    print("Missing from source:", len(d["missing_from_source"]), "items")
