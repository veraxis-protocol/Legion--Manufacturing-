"""C06 rfq-to-quote: the drawing-to-quote chain's gates. The LEGION CAD path (WO-D01) feeds step 7 as a path-C1
geometry estimate, which stays draft, so no quote rests on it until the estimator rules at Gate 3."""
import copy
import hashlib
import unittest

from legion.engineering import pinned_source as P
from manufacturing.runtime import gates as G
from tests.manufacturing import base


class C06RfqToQuote(base.SkillSuite):
    CID = "C06"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        P.materialize()
        from legion.engineering import step_intake as S
        from tests.engineering.test_d01_cad import dr_fixture
        dr = dr_fixture()
        cls.cad = S.assemble({"stages": {}}, copy.deepcopy(dr.MINI_XCAF), dr.MINI_README,
                             hashlib.sha256(dr.MINI_README.encode()).hexdigest(), "Fairview", "RFQ-STEP-1")

    def test_c06_legion_cad_handoff_is_contract_valid_and_gated(self):
        env = self.cad["geometry_estimates"][0]
        self.assertNotEqual(env["legion"]["verification"]["contract_check"]["status"], "BLOCK")
        adm = G.admit("geometry-estimate", env["record"])
        self.assertEqual(adm["verdict"], "Z")                     # draft: rung 3 blocked until Gate 3
        self.assertIn("`approval.status` is `draft`", [r["row"] for r in adm["reasons"]])

    def test_c06_c1_is_unverified_and_never_firm(self):
        rec = self.cad["geometry_estimates"][0]["record"]
        self.assertEqual((rec["geometry_path"], rec["drawing_revision_priced_to"]), ("C1", None))
        self.assertIn("unverified", rec["model"]["document_integrity"]["detail"])


if __name__ == "__main__":
    unittest.main()
