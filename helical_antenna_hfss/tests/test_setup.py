"""Setup QA: frequency, sweep, port, radiation and far-field definitions."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from common import ASSUMPTIONS, SOURCE, SETUP_NAME, sweep_includes_operating_frequency  # noqa: E402
from hfss_setup import generate as generate_setup  # noqa: E402
from port_setup import generate as generate_port  # noqa: E402
from radiation_setup import generate as generate_rad  # noqa: E402
from simulation_runner import write_ironpython_script  # noqa: E402


class TestSetup(unittest.TestCase):
    def test_operating_frequency(self) -> None:
        self.assertAlmostEqual(SOURCE["operating_frequency_GHz"], 3.035, places=6)

    def test_sweep_contains_operating_frequency(self) -> None:
        info = sweep_includes_operating_frequency()
        self.assertTrue(info["operating_frequency_in_span"])
        cfg = generate_setup()
        self.assertEqual(cfg["adaptive_setup"]["frequency_GHz"], 3.035)
        self.assertEqual(cfg["adaptive_setup"]["name"], SETUP_NAME)

    def test_port_exists_in_definition(self) -> None:
        port = generate_port()
        self.assertEqual(port["first_pass_excitation"]["name"], "P1")
        self.assertEqual(port["first_pass_excitation"]["impedance_ohm"], 50.0)
        self.assertFalse(port["source_document_defines_feed"])

    def test_radiation_boundary_defined(self) -> None:
        rad = generate_rad()
        self.assertEqual(rad["boundary_name"], "Rad1")
        self.assertEqual(rad["object_name"], "RadBox")
        self.assertGreater(rad["wavelength_mm"], 90.0)

    def test_solution_setup_exists(self) -> None:
        cfg = generate_setup()
        self.assertEqual(cfg["adaptive_setup"]["maximum_passes"], ASSUMPTIONS["max_passes"])
        self.assertEqual(cfg["far_field"]["name"], "Infinite Sphere1")

    def test_far_field_setup_exists(self) -> None:
        cfg = generate_setup()
        self.assertIn("Infinite Sphere", cfg["far_field"]["name"])

    def test_ironpython_script_contains_objects(self) -> None:
        path = write_ironpython_script()
        text = path.read_text(encoding="utf-8")
        for token in ("HelixWire", "GroundPlane", "PortSheet", "RadBox", "Setup1", "Infinite Sphere1", "3.035"):
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
