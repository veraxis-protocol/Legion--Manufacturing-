"""C11 morning-plant-pulse: the upstream compute engine and short-page renderer run on two export drops; the day
record is checked against its contract; a day with no data produces no record, never a stale one."""
import hashlib
import unittest
from pathlib import Path

from manufacturing.contracts import upstream as U
from manufacturing.runtime import upstream_exec as X
from tests.manufacturing import base

HERE = Path(__file__).resolve().parent
DROPS = {"pulse_minimal": HERE.parent / "upstream" / "fixtures" / "pulse_minimal", "pulse_oee": HERE / "fixtures" / "pulse_oee"}


class C11MorningPlantPulse(base.SkillSuite):
    CID = "C11"

    def test_c11_engine_and_renderer_on_both_drops(self):
        for name, drop in DROPS.items():
            with X.TaskFolder() as t:
                before = t.plugin_tree_digest()
                r = t.pulse(drop, "2026-11-12")
                self.assertEqual(r["rc"], 0, (name, r["stderr"]))
                self.assertRegex(r["stdout"], r"self-checks: \d+ run, 0 failed")
                s = t.run("skills/morning-plant-pulse/scripts/render_short.py", "--out", r["out"], "--day", "2026-11-12")
                self.assertEqual(s["rc"], 0, (name, s["stderr"]))
                self.assertEqual(t.plugin_tree_digest(), before)
                d = r["day_records"][0]
                self.assertEqual((d["site"], d["production_day"]), ("SITE-1", "2026-11-12"))
                self.assertEqual(d["actual_qty"], {"unit": 1000})
                self.assertEqual(d["planned_qty"], {"unit": 1050})
                self.assertNotEqual(U.check(d, U.load("pulse-day-record"))["status"], "BLOCK")

    def test_c11_absent_oee_is_absent_not_zero(self):
        with X.TaskFolder() as t:
            d = t.pulse(DROPS["pulse_minimal"], "2026-11-12")["day_records"][0]
        self.assertIsNone(d["oee"])          # no planned production time in that drop: not computable, not 0
        self.assertIsNone(d["availability"])

    def test_c11_no_stale_record_for_a_day_without_data(self):
        with X.TaskFolder() as t:
            r = t.pulse(DROPS["pulse_oee"], "2026-11-15")
        self.assertEqual(r["rc"], 0, r["stderr"])
        self.assertIn("has no rows for 2026-11-15", r["stdout"])
        self.assertNotIn("2026-11-15", [d["production_day"] for d in r["day_records"] or []])

    def test_c11_fixture_inputs_hashed(self):
        for drop in DROPS.values():
            for f in sorted(drop.glob("*.csv")):
                self.assertEqual(len(hashlib.sha256(f.read_bytes()).hexdigest()), 64)
            self.assertIn("SYNTHETIC", (drop / "README.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
