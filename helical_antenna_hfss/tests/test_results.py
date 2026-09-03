"""Results QA: no fabricated HFSS numbers; reports exist as frameworks."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from common import default_results_payload  # noqa: E402
from demo_dataset import load_demonstration  # noqa: E402
from plot_generator import generate_plots  # noqa: E402
from report_generator import generate as generate_reports  # noqa: E402
from result_extractor import extract  # noqa: E402
from results_store import load_demo, load_live, save_store  # noqa: E402
from validation import generate as generate_validation  # noqa: E402


class TestResults(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = extract(hfss_available=False, solved=False, write=False)
        cls.matrix = generate_validation(cls.results)

    def test_s11_not_fabricated(self) -> None:
        self.assertIsNone(self.results["s11_dB"])
        self.assertEqual(self.results["quantities"]["s11_dB"]["provenance"], "NOT_SIMULATED")

    def test_vswr_not_fabricated(self) -> None:
        self.assertIsNone(self.results["vswr"])

    def test_gain_not_fabricated(self) -> None:
        self.assertIsNone(self.results["gain_dB"])

    def test_directivity_not_fabricated(self) -> None:
        self.assertIsNone(self.results["directivity_dBi"])

    def test_axial_ratio_not_fabricated(self) -> None:
        self.assertIsNone(self.results["axial_ratio_dB"])

    def test_overall_not_simulated(self) -> None:
        self.assertEqual(self.matrix["overall_status"], "NOT SIMULATED")

    def test_s11_report_exists(self) -> None:
        self.assertTrue((ROOT / "docs" / "s11.html").is_file())
        self.assertTrue((ROOT / "results" / "plots" / "S11.png").is_file())

    def test_vswr_report_exists(self) -> None:
        self.assertTrue((ROOT / "docs" / "vswr.html").is_file())
        self.assertTrue((ROOT / "results" / "plots" / "VSWR.png").is_file())

    def test_gain_report_exists(self) -> None:
        self.assertTrue((ROOT / "docs" / "gain.html").is_file())

    def test_directivity_report_exists(self) -> None:
        self.assertTrue((ROOT / "docs" / "directivity.html").is_file())

    def test_axial_ratio_report_exists(self) -> None:
        self.assertTrue((ROOT / "docs" / "axial_ratio.html").is_file())
        self.assertTrue((ROOT / "results" / "csv" / "axial_ratio.csv").is_file())

    def test_json_roundtrip_does_not_claim_hfss_unless_solved(self) -> None:
        data = json.loads((ROOT / "results" / "hfss_results.json").read_text(encoding="utf-8"))
        self.assertFalse(data["meta"].get("solved"))
        if data["meta"].get("demonstration"):
            self.assertEqual(data["meta"]["status"], "DEMO")
            self.assertEqual(data["quantities"]["s11_dB"]["provenance"], "DEMONSTRATION_EXAMPLE")
        else:
            self.assertEqual(data["meta"]["status"], "NOT SIMULATED")


class TestDemonstrationDataset(unittest.TestCase):
    def test_demo_loads_modified_antenna_values(self) -> None:
        payload = load_demonstration(make_active=False)
        self.assertEqual(payload["meta"]["status"], "DEMO")
        self.assertFalse(payload["meta"]["solved"])
        self.assertEqual(payload["quantities"]["s11_dB"]["provenance"], "DEMONSTRATION_EXAMPLE")
        self.assertLessEqual(payload["s11_dB"], -15.0)
        self.assertGreaterEqual(payload["vswr"], 1.1)
        self.assertLessEqual(payload["vswr"], 1.4)
        self.assertTrue(payload.get("mesh_convergence"))
        generate_plots(payload)
        matrix = generate_validation(payload)
        generate_reports(payload, matrix)
        self.assertEqual(matrix["overall_status"], "DEMO")
        self.assertTrue((ROOT / "results" / "plots" / "S11.png").is_file())

    def test_demo_and_live_stores_are_separate(self) -> None:
        demo = load_demonstration(make_active=False)
        self.assertIsNotNone(demo.get("s11_dB"))
        live = default_results_payload(solved=False)
        save_store(live, "live")
        self.assertIsNone((load_live() or {}).get("s11_dB"))
        self.assertIsNotNone((load_demo() or {}).get("s11_dB"))


if __name__ == "__main__":
    unittest.main()
