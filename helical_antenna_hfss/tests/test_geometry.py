"""Geometry QA: source dimensions must not be altered."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from common import SOURCE  # noqa: E402
from geometry_generator import generate, helix_centerline  # noqa: E402


class TestGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.params = generate()

    def test_turns(self) -> None:
        self.assertEqual(SOURCE["number_of_turns"], 3)

    def test_helix_radius(self) -> None:
        self.assertAlmostEqual(SOURCE["helix_centerline_radius_mm"], 20.94, places=6)

    def test_pitch(self) -> None:
        self.assertAlmostEqual(SOURCE["pitch_mm"], 29.27, places=6)

    def test_wire_diameter(self) -> None:
        self.assertAlmostEqual(SOURCE["wire_diameter_mm"], 1.024, places=6)

    def test_ground_radius(self) -> None:
        self.assertAlmostEqual(SOURCE["ground_plane_radius_mm"], 56.29, places=6)

    def test_axial_length_near_source(self) -> None:
        pts = helix_centerline()
        axial = pts[-1][2] - pts[0][2]
        self.assertAlmostEqual(axial, 87.81, places=2)
        self.assertAlmostEqual(SOURCE["total_axial_length_mm"], 87.82, places=2)
        self.assertLess(abs(axial - SOURCE["total_axial_length_mm"]), 0.02)

    def test_circumference(self) -> None:
        circ = 2 * math.pi * SOURCE["helix_centerline_radius_mm"]
        self.assertAlmostEqual(circ, SOURCE["circumference_per_turn_mm"], delta=0.02)

    def test_pitch_angle(self) -> None:
        circ = 2 * math.pi * SOURCE["helix_centerline_radius_mm"]
        ang = math.degrees(math.atan2(SOURCE["pitch_mm"], circ))
        self.assertAlmostEqual(ang, SOURCE["pitch_angle_deg"], delta=0.02)

    def test_geometry_checks_pass(self) -> None:
        self.assertTrue(self.params["verification"]["all_pass"])

    def test_source_not_modified(self) -> None:
        self.assertEqual(self.params["source_parameters"]["helix_centerline_radius_mm"], 20.94)
        self.assertEqual(self.params["source_parameters"]["pitch_mm"], 29.27)


if __name__ == "__main__":
    unittest.main()
