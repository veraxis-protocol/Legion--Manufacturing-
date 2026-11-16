"""C09 trade-study-report: runs from a hand-authored manifest (cad_backend none is a complete input). Scoring and
sensitivity are computed by the Claude-run skill: NOT RUN here, never claimed from a fixture."""
import copy
import unittest

from manufacturing.contracts import upstream as U
from tests.manufacturing import base

C = U.load("variant-manifest")


class C09TradeStudyReport(base.SkillSuite):
    CID = "C09"

    def test_c09_hand_authored_manifest_is_a_complete_input(self):
        names = {f.name: f for f in C.fields}
        self.assertIn("cad_backend", names)
        self.assertIn("none", names["cad_backend"].enum)
        ex = copy.deepcopy(U.worked_example(C)["record"])
        ex["cad_backend"] = "none"
        self.assertEqual(U.check(ex, C)["status"], "OK")

    def test_c09_unknown_backend_rejected(self):
        ex = copy.deepcopy(U.worked_example(C)["record"])
        ex["cad_backend"] = "solidworks"
        self.assertEqual(U.check(ex, C)["status"], "BLOCK")

    def test_c09_sensitivity_reproducibility(self):
        self.skipTest("NOT RUN: weighted scoring and the sensitivity sweep are computed by the Claude-run skill; "
                      "reproducibility needs two model-driven runs on the same matrix")


if __name__ == "__main__":
    unittest.main()
