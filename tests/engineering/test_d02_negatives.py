"""WO-D02-D / F: missing requirements, partial proofs, receipts and the reBot case.

D02-06 missing manufacturing tolerance -> Z; D02-07 missing material evidence -> Z; D02-15 one mandatory T + one Z
-> global Z; D02-16 one T + one F -> global F; D02-17 replayed or unauthenticated receipt -> no admission;
D02-18 the reBot reference case -> engineering Z (fixture always; the real STEP with LMFG_REAL_CAD=1).
"""
import unittest

from tests.engineering import d02_common as C

NO_EXECUTION = {"procurement_authorized": False, "payment_authorized": False, "manufacturing_release": False,
                "supplier_requests_sent": 0, "paypal_calls": 0}


class D02Missing(unittest.TestCase):
    def test_d02_06_missing_manufacturing_tolerance_is_Z(self):
        r = C.missing_rail_tolerance()
        p = r["predicate"]
        self.assertEqual((p["verdict"], p["stand_called"]), ("Z", False))
        self.assertIsNone(p["binding"]["tolerances"])
        self.assertTrue(any("tolerance" in m.lower() for m in p["missing_blocks_stand_call"]))
        f = r["deal_rescue_tolerance_finding"]
        self.assertFalse(f["only_tolerance_in_sources"]["applies_to_purchased_rail"])   # CNC tolerance not applied

    def test_d02_07_missing_material_evidence_is_Z(self):
        r = C.missing_material()
        for key in ("cnc_material_evidence", "material_input_removed"):
            self.assertEqual(r[key]["verdict"], "Z", key)
            self.assertFalse(r[key]["stand_called"], key)
        self.assertIn("input material", r["material_input_removed"]["missing_blocks_stand_call"])


class D02Aggregation(unittest.TestCase):
    def test_d02_15_one_T_one_Z_is_global_Z(self):
        m = C.mixed("Z")
        self.assertEqual([r["verdict"] for r in m["results"]], ["T", "Z"])
        for agg in (m["aggregate"], m["aggregate_with_synthetic_receipt_claim"]):
            self.assertEqual(agg["ENGINEERING_VERDICT"], "Z")
            self.assertEqual(agg["production_admission"]["verdict"] in ("Z", "F"), True)
            for k, v in NO_EXECUTION.items():
                self.assertEqual(agg[k], v)

    def test_d02_16_one_T_one_F_is_global_F(self):
        m = C.mixed("F")
        self.assertEqual([r["stand_verdict"] for r in m["results"]], ["EARNED", "REFUTED"])
        self.assertEqual([r["verdict"] for r in m["results"]], ["T", "F"])
        for agg in (m["aggregate"], m["aggregate_with_synthetic_receipt_claim"]):
            self.assertEqual(agg["ENGINEERING_VERDICT"], "F")
            self.assertNotEqual(agg["production_admission"]["verdict"], "T")

    def test_d02_d_deal_rescue_partial_aggregation_is_not_used(self):
        demo = C.deal_rescue_partial_proof_demo()
        self.assertEqual(demo["deal_rescue_production_verdict"], "EARNED")   # the reason for the LEGION boundary
        m = C.mixed("Z")
        self.assertEqual(m["aggregate"]["ENGINEERING_VERDICT"], "Z")

    def test_d02_d_all_T_without_authenticated_receipt_is_Z(self):
        a = C.A()
        p = C.controlled(False)[0]
        ctx = {k: p["binding"][k] for k in (*a.CONTEXT_FIELDS, "policy_sha256")}
        agg = a.aggregate([p], ctx)
        self.assertEqual((agg["predicate_layer_verdict"], agg["ENGINEERING_VERDICT"]), ("T", "Z"))
        self.assertTrue(any("authenticated_receipt" in b for b in agg["blocking"]))


class D02Receipts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = C.receipts()

    def test_d02_17_no_or_unauthenticated_receipt_is_not_admitted(self):
        self.assertEqual(self.r["no_verifier_configured"]["code"], "TRUSTED_ZTL_SERVICE_NOT_CONFIGURED")
        for k in ("no_verifier_configured", "no_verifier_configured_partial_env", "unsigned_receipt",
                  "local_mcp_result_as_receipt", "three_part_garbage"):
            self.assertEqual(self.r[k]["verdict"], "Z", k)
            self.assertFalse(self.r[k]["admitted"], k)

    def test_d02_17_replayed_signed_receipts_are_refused(self):
        if not C.have_cryptography():
            if C.STRICT:
                self.fail("cryptography must be installed in the verifier job")
            self.skipTest("NOT RUN: cryptography is not installed here (it is in the CI verifier job)")
        self.assertEqual(self.r["fresh_test_signed_receipt_POSITIVE_CONTROL"]["verdict"], "T")
        self.assertFalse(self.r["fresh_test_signed_receipt_POSITIVE_CONTROL"]["detail"]["procurement_authorized"])
        want = {"replayed_from_previous_epoch": "CERTIFICATE_EPOCH_INVALID",
                "replayed_after_expiry": "CERTIFICATE_EXPIRED_OR_INVALID",
                "replayed_onto_changed_spec": "CERTIFICATE_BINDING_MISMATCH",
                "signed_by_untrusted_key": "CERTIFICATE_SIGNATURE_INVALID"}
        for k, code in want.items():
            self.assertEqual((self.r[k]["verdict"], self.r[k]["code"]), ("Z", code), k)


class RebotChecks:
    REAL = False

    def test_d02_18_rebot_engineering_is_Z(self):
        res = C.rebot(self.REAL)
        v = res["stages"]["verification"]
        agg = v["verdict"]
        self.assertEqual(res["stages"]["bom"]["status"], "T")
        self.assertEqual(agg["mandatory_predicates"]["cad_bom_extraction"], "T")
        for pid in ("rail_length_tolerance", "joint2_load_torque", "cnc_material_evidence"):
            self.assertEqual(agg["mandatory_predicates"][pid], "Z", pid)
        self.assertEqual(agg["ENGINEERING_VERDICT"], "Z")
        self.assertEqual(res["engineering_verdict"], "Z")
        self.assertEqual(v["status"], "Z")
        for p in v["predicates"]:
            self.assertFalse(p["stand_called"], p["predicate_id"])           # nothing invented is sent to the stand
            self.assertNotEqual(p["verdict"], "F", p["predicate_id"])
        self.assertNotEqual(agg["production_admission"]["verdict"], "T")
        for k, val in NO_EXECUTION.items():
            self.assertEqual(agg[k], val)
        self.assertIsNone(v["context"]["drawing_revision"])


class D02RebotFixture(RebotChecks, unittest.TestCase):
    REAL = False


@unittest.skipUnless(C.REAL, "NOT RUN: needs cadquery-ocp and the pinned reBot STEP (LMFG_REAL_CAD=1, CI verifier job)")
class D02RebotRealStep(RebotChecks, unittest.TestCase):
    REAL = True

    def test_d02_18_real_step_baseline_unchanged(self):
        res = C.rebot(True)
        pin = C.P.load_pin()
        b, base = res["stages"]["bom"], pin["recorded_baseline"]["bom"]
        self.assertEqual(res["stages"]["intake"]["sha256"], pin["reference_cad"]["files"]["step"]["sha256"])
        self.assertEqual((b["mandatory_positions_matched"], b["mandatory_positions"]),
                         (base["mandatory_positions_matched"], base["mandatory_positions"]))
        self.assertEqual(b["mandatory_instances_step"], base["mandatory_instances"])
        ctx = res["stages"]["verification"]["context"]
        self.assertEqual((ctx["source_repository"], ctx["source_commit"]),
                         (pin["reference_cad"]["repository"], pin["reference_cad"]["commit"]))


if __name__ == "__main__":
    unittest.main()
