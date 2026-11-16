"""C12 breakdown-diagnosis: the emitted downtime record keeps its evidence and safety fields; ranking candidate causes
is Claude-run (NOT RUN). An unknown safety flag blocks the consumer, never reads as safe."""
import copy
import unittest

from manufacturing.contracts import upstream as U
from manufacturing.runtime import gates as G
from tests.manufacturing import base

C = U.load("downtime-record")
REC = U.worked_example(C)["record"]


class C12BreakdownDiagnosis(base.SkillSuite):
    CID = "C12"

    def test_c12_record_carries_asset_time_and_safety(self):
        for k in ("asset_id", "started_at", "production_day", "safety_flagged"):
            self.assertIn(k, REC)
        self.assertEqual(G.admit("downtime-record", REC)["verdict"], "T")

    def test_c12_naive_or_missing_day_blocks(self):
        rec = copy.deepcopy(REC)
        rec["production_day"] = None
        self.assertEqual(G.admit("downtime-record", rec)["verdict"], "Z")

    def test_c12_candidate_ranking(self):
        self.skipTest("NOT RUN: ranking causes against sensor, history, photos and manual is Claude-run")


if __name__ == "__main__":
    unittest.main()
