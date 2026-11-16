"""WO-D02-E: genuine positive and negative proofs through MCP -> stand -> checker.

D02-04 a fully supported positive predicate -> scoped T; D02-05 the same model with a deliberately violated
requirement -> scoped F. Offline: Deal-Rescue's CAD-027 fixture as input. RealStep (LMFG_REAL_CAD=1): the pinned reBot
STEP through OpenCascade as input. Either way the tolerance window is an identified assumption, so neither result is
reBot compliance (controlled_case, admissible_for_rebot False).
"""
import unittest

from tests.engineering import d02_common as C


class ProofChecks:
    REAL = False

    def cases(self):
        return {c["predicate_id"].split("_")[-1]: c for c in C.controlled(self.REAL)}

    def test_d02_04_positive_predicate_is_scoped_T(self):
        p = self.cases()["positive"]
        self.assertEqual((p["stand_verdict"], p["verdict"]), ("EARNED", "T"), p["why"])
        self.assertTrue(p["stand_called"])
        dev = p["checker_result"]["independent_checker_dev_mode"]
        self.assertEqual(dev["verdict"], "EARNED")
        self.assertIn("independent checker", dev["checked_by"])
        self.assertTrue(p["controlled_case"])
        self.assertFalse(p["admissible_for_rebot"])
        self.assertTrue(p["assumptions"])
        self.assertTrue(p["binding"]["brick_sha256"])

    def test_d02_05_violated_predicate_is_scoped_F(self):
        n = self.cases()["negative"]
        self.assertEqual((n["stand_verdict"], n["verdict"]), ("REFUTED", "F"), n["why"])
        self.assertTrue(n["deliberate_change"])
        sr = n["mcp"]["stand_result"]
        self.assertEqual(sr["value_there"]["dL"], "20")
        self.assertEqual(n["checker_result"]["independent_checker_dev_mode"]["verdict"], "REFUTED")

    def test_d02_e_positive_and_negative_bound_to_different_requirements(self):
        c = self.cases()
        self.assertNotEqual(c["positive"]["binding"]["requirements_digest"], c["negative"]["binding"]["requirements_digest"])
        self.assertNotEqual(c["positive"]["binding"]["brick_sha256"], c["negative"]["binding"]["brick_sha256"])


class D02ProofsFixture(ProofChecks, unittest.TestCase):
    REAL = False


@unittest.skipUnless(C.REAL, "NOT RUN: needs cadquery-ocp and the pinned reBot STEP (LMFG_REAL_CAD=1, CI verifier job)")
class D02ProofsRealStep(ProofChecks, unittest.TestCase):
    REAL = True

    def test_d02_04_input_is_the_real_step(self):
        p = self.cases()["positive"]
        self.assertEqual(p["binding"]["source_sha256"], C.P.load_pin()["reference_cad"]["files"]["step"]["sha256"])
        self.assertEqual(p["binding"]["source_commit"], C.P.load_pin()["reference_cad"]["commit"])


if __name__ == "__main__":
    unittest.main()
