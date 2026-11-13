"""WO-A03: the upstream executable baseline reproduces (scripts run on a copy, never write into the plugin tree)."""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


class UpstreamBaseline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as td:
            ev = pathlib.Path(td) / "baseline.json"
            cls.proc = subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "upstream_baseline.py"), "--evidence", str(ev)],
                                      capture_output=True, text=True, cwd=ROOT)
            cls.res = json.loads(ev.read_text(encoding="utf-8"))
        cls.by = {c["id"]: c for c in cls.res["checks"]}

    def test_entrypoints_inventoried(self):
        paths = {e["path"] for e in self.res["entrypoints"]}
        for p in ("shared/scripts/plant_setup.py", "skills/morning-plant-pulse/scripts/pulse_compute.py",
                  "skills/morning-plant-pulse/scripts/render_short.py", ".mcp.json#fusion"):
            self.assertIn(p, paths)

    def test_compile_and_help(self):
        for c in self.res["checks"]:
            if c["id"].startswith(("compile:", "help:")):
                self.assertEqual(c["status"], "PASS", c["id"])

    def test_pulse_engine_self_checks(self):
        c = self.by["run:skills/morning-plant-pulse/scripts/pulse_compute.py"]
        self.assertEqual(c["status"], "PASS", c["output_tail"])
        self.assertGreater(c["self_checks"]["run"], 0)
        self.assertEqual(c["self_checks"]["failed"], 0)
        self.assertIn("figures.csv", c["outputs"])

    def test_absent_is_not_zero(self):
        # The fixture has no planned hours: OEE must be reported absent (None), never 0.
        self.assertIn("composite None", self.by["run:skills/morning-plant-pulse/scripts/pulse_compute.py"]["output_tail"])

    def test_render_short_checks(self):
        c = self.by["run:skills/morning-plant-pulse/scripts/render_short.py"]
        self.assertEqual(c["status"], "PASS", c["output_tail"])
        self.assertTrue(any(k.startswith("operations-short-") and k.endswith(".html") for k in c["outputs"]))

    def test_no_writes_into_plugin_tree(self):
        self.assertEqual(self.by["integrity:no-writes-into-plugin-tree"]["status"], "PASS")

    def test_fusion_blocked_not_passed(self):
        self.assertEqual([b["entrypoint"] for b in self.res["blocked_entrypoints"]], [".mcp.json#fusion"])

    def test_all_17_skills_classified_honestly(self):
        self.assertEqual(len(self.res["skills"]), 17)
        for s in self.res["skills"]:
            self.assertTrue(s["AVAILABLE"], s["skill"])
            self.assertEqual(s["live_model_driven_run"], "BLOCKED", s["skill"])
            self.assertFalse(s["CONFIGURED"], s["skill"])

    @unittest.skipIf(os.name == "nt", "upstream self-test asserts a POSIX path separator (recorded upstream defect)")
    def test_plant_setup_selftest(self):
        c = self.by["selftest:shared/scripts/plant_setup.py"]
        self.assertEqual(c["status"], "PASS", c["output_tail"])
        self.assertIn("plant_setup selftest: ok", c["output_tail"])


if __name__ == "__main__":
    unittest.main()
