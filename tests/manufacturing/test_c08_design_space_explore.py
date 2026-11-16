"""C08 design-space-explore: needs Fusion desktop (live: BLOCKED). The variant manifest contract and the Fusion
guard are tested: the original model is never written and invalid variants are rejected before any call."""
import copy
import unittest

from manufacturing.connectors import fusion as F
from manufacturing.contracts import upstream as U
from tests.connectors.fakes import FusionFake
from tests.manufacturing import base

MANIFEST_C = U.load("variant-manifest")


class C08DesignSpaceExplore(base.SkillSuite):
    CID = "C08"

    def test_c08_original_unchanged_invalid_rejected(self):
        fake = FusionFake()
        a = F.Fusion(fake, {})
        a.connect({"endpoint": F.endpoint({})})
        params = a.read_parameters()
        a.save_as_new("Bracket_V01")
        with self.assertRaises(F.ScriptRejected):
            a.apply_parameters({"label_text": "'B'"}, params)          # non-driving parameter
        self.assertEqual(a.apply_parameters({"flange_length": "22 mm"}, params)["variant"], "ok")
        self.assertTrue(a.confirm_base_unchanged())
        self.assertNotIn("Bracket_Base", [w[1] for w in fake.writes])

    def test_c08_unsourced_variant_row_is_not_scored(self):
        ex = copy.deepcopy(U.worked_example(MANIFEST_C)["record"])
        self.assertEqual(U.check(ex, MANIFEST_C)["status"], "OK")
        ex["variants"][0].pop("source_ref", None)
        for f in MANIFEST_C.fields:
            if f.name == "source_ref":
                self.assertIn(f.behavior, ("Required", "Degrades", "Conditional"))


if __name__ == "__main__":
    unittest.main()
