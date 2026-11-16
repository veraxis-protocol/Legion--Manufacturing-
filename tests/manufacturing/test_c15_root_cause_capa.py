"""C15 root-cause-capa: alternatives and disconfirming evidence are retained in the supplier-caused flag, and their
absence blocks the consumer. The pattern checks themselves are Claude-run (NOT RUN)."""
import copy
import unittest

from manufacturing.contracts import upstream as U
from manufacturing.runtime import gates as G
from tests.manufacturing import base

C = U.load("supplier-caused-flag")
FLAG = U.worked_example(C)["record"]


class C15RootCauseCapa(base.SkillSuite):
    CID = "C15"

    def test_c15_alternatives_and_disconfirming_evidence_retained(self):
        self.assertTrue(FLAG["competing_candidates"])
        self.assertIn("evidence_against", FLAG)
        for k in ("competing_candidates", "evidence_against"):
            rec = copy.deepcopy(FLAG)
            del rec[k]
            res = U.check(rec, C)
            self.assertEqual(res["status"], "BLOCK", k)
            self.assertIn(k, [b["field"] for b in res["blocked"]])

    def test_c15_ncr_without_requirement_blocks_the_8d(self):
        ncr = copy.deepcopy(U.worked_example(U.load("ncr"))["record"])
        ncr["requirement_cited"] = None
        ncr["requirement_not_locatable"] = True
        self.assertEqual(G.admit("ncr", ncr)["verdict"], "Z")

    def test_c15_pattern_checks(self):
        self.skipTest("NOT RUN: SPC drift and clustering checks are written and run by the Claude-run skill")


if __name__ == "__main__":
    unittest.main()
