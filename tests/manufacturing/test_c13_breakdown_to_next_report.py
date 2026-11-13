"""C13 breakdown-to-next-report: the handoff from diagnosis to the next report keeps asset, timestamp and downtime
lineage. The LEGION envelope carries the record unchanged and the bindings forward through the join."""
import unittest

from manufacturing.adapters import envelope as E
from manufacturing.contracts import upstream as U
from tests.manufacturing import base

REC = U.worked_example(U.load("downtime-record"))["record"]


class C13BreakdownToNextReport(base.SkillSuite):
    CID = "C13"

    def test_c13_lineage_survives_the_handoff(self):
        scope = E.scope("plant", ["files:read"])
        b = [E.binding("asset_id", "cmms", "plant", "maintenance-export.csv:17", REC["asset_id"]),
             E.binding("started_at", "historian_export", "plant", "sensor-window.csv:1", REC["started_at"])]
        diag = E.wrap("downtime-record", REC, b, scope)
        nxt = E.combine([diag], "downtime-record", REC)
        self.assertEqual((nxt["record"]["asset_id"], nxt["record"]["started_at"]), (REC["asset_id"], REC["started_at"]))
        self.assertEqual([x["record_ref"] for x in nxt["legion"]["source_bindings"]],
                         ["maintenance-export.csv:17", "sensor-window.csv:1"])
        self.assertEqual(nxt["legion"]["derived_from"], [diag["record_sha256"]])

    def test_c13_a_changed_record_breaks_the_chain(self):
        diag = E.wrap("downtime-record", REC, [], E.scope("plant", ["files:read"]))
        diag["record"]["duration_minutes"] = 1
        with self.assertRaises(E.EnvelopeError):
            E.combine([diag], "downtime-record", REC)


if __name__ == "__main__":
    unittest.main()
