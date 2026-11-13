"""C10 daily-production-report: OEE and losses reconcile to source data.

The report's own figures are Claude-computed (NOT RUN). In Chain 3 the figures it prints come from the upstream
pulse engine (pulse_compute.py), which IS executed here, and every component is recomputed independently from the
fixture with the definitions in upstream skills/daily-production-report/reference/oee.md.
"""
import csv
import unittest
from pathlib import Path

from manufacturing.contracts import upstream as U
from manufacturing.runtime import gates as G
from manufacturing.runtime import upstream_exec as X
from tests.manufacturing import base

FX = Path(__file__).resolve().parent / "fixtures" / "pulse_oee"


def oracle():
    rows = lambda n: list(csv.DictReader(open(FX / n, encoding="utf-8")))
    plan, out, down, rout = rows("plan.csv"), rows("output.csv"), rows("downtime.csv"), rows("routing.csv")
    ideal = {r["part_number"]: float(r["run_min_per_unit"]) for r in rout}
    a_num = a_den = p_num = p_den = good = tot = 0.0
    for p in plan:
        asset, pm = p["asset_id"], float(p["planned_hours"]) * 60
        dmin = sum(float(d["duration_minutes"]) for d in down if d["asset_id"] == asset)
        mine = [o for o in out if o["asset_id"] == asset]
        run = pm - dmin
        a_num, a_den = a_num + run, a_den + pm
        p_num += sum(ideal[o["part_number"]] * (float(o["qty_good"]) + float(o["qty_scrap"])) for o in mine)
        p_den += run
        good += sum(float(o["qty_good"]) for o in mine)
        tot += sum(float(o["qty_good"]) + float(o["qty_scrap"]) for o in mine)
    A, P, Q = a_num / a_den, p_num / p_den, good / tot
    return {"availability": round(A, 4), "performance": round(P, 4), "quality": round(Q, 4),
            "oee": round(A * P * Q, 4), "downtime_min": sum(float(d["duration_minutes"]) for d in down)}


class C10DailyProductionReport(base.SkillSuite):
    CID = "C10"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with X.TaskFolder() as t:
            cls.pulse_run = t.pulse(FX, "2026-11-12", env={"MFG_DOWNTIME_COST_PER_HOUR": "120"})
        cls.day = cls.pulse_run["day_records"][0]

    def test_c10_oee_reconciles_to_source(self):
        self.assertEqual(self.pulse_run["rc"], 0, self.pulse_run["stderr"])
        o = oracle()
        for k in ("availability", "performance", "quality", "oee"):
            self.assertAlmostEqual(self.day[k], o[k], places=3, msg=k)

    def test_c10_losses_reconcile(self):
        o = oracle()
        self.assertEqual(self.day["downtime_minutes_total"], o["downtime_min"])
        self.assertEqual(self.day["loss_usd"]["downtime"], round(o["downtime_min"] / 60 * 120, 2))
        self.assertEqual(self.day["rate_source"], "env_variable")
        self.assertIsNone(self.day["loss_usd"]["scrap"])                       # no standard cost: unpriced,
        self.assertTrue(any("scrap" in u for u in self.day["unpriced"]))      # and said so, never zero

    def test_c10_day_record_meets_its_contract(self):
        self.assertNotEqual(U.check(self.day, U.load("pulse-day-record"))["status"], "BLOCK")

    def test_c10_breakdown_input_gate(self):
        rec = dict(U.worked_example(U.load("downtime-record"))["record"])
        self.assertEqual(G.admit("downtime-record", rec)["verdict"], "T")
        rec.pop("safety_flagged")
        self.assertEqual(G.admit("downtime-record", rec)["verdict"], "Z")     # safety unknown, never false


if __name__ == "__main__":
    unittest.main()
