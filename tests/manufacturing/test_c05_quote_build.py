"""C05 quote-build: no price rests on an unconfirmed model, a failed design step, a declined inquiry or a rate typed
into the run. Costs and dates themselves are computed by the Claude-run skill (NOT RUN here)."""
import copy
import unittest

from manufacturing.contracts import upstream as U
from manufacturing.runtime import gates as G
from manufacturing.runtime import upstream_exec as X
from tests.manufacturing import base

GEO = U.worked_example(U.load("geometry-estimate"))["record"]


class C05QuoteBuild(base.SkillSuite):
    CID = "C05"

    def test_c05_unconfirmed_or_failed_model_never_prices(self):
        self.assertEqual(G.admit("geometry-estimate", GEO)["verdict"], "Z")          # upstream example is draft
        ok = copy.deepcopy(GEO)
        ok["approval"] = {"status": "confirmed", "by": "estimator", "at": "2026-10-13T11:00:00-04:00", "note": None}
        self.assertEqual(G.admit("geometry-estimate", ok)["verdict"], "T")
        bad = copy.deepcopy(ok)
        bad["model"]["document_integrity"]["result"] = "foreign_geometry"
        self.assertEqual(G.admit("geometry-estimate", bad)["verdict"], "Z")

    def test_c05_supplier_bid_examples_are_consumable(self):
        recs = [e["record"] for e in U.worked_examples(U.load("supplier-bid"))]
        self.assertEqual(len(recs), 3)
        for r in recs:
            self.assertNotEqual(U.check(r, U.load("supplier-bid"))["status"], "BLOCK")

    def test_c05_rates_resolved_from_the_rates_file_never_printed_by_setup(self):
        with X.TaskFolder() as t:
            t.install_profile(with_rates=True)
            f = t.plant_setup("find")
            self.assertTrue(f["json"]["rates_exists"])
            self.assertNotIn("71.00", f["stdout"])                 # find names paths, never a rate value


if __name__ == "__main__":
    unittest.main()
