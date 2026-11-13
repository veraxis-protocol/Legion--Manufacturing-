"""WO-D02-C: engineering evidence binding. A proof is valid only for the exact context it was obtained for.

D02-08 altered source SHA-256 -> binding rejected; D02-09 changed revision -> old proof invalid;
D02-10 altered requirement digest -> old proof invalid. Proofs are real stand results (controlled cases).
"""
import copy
import hashlib
import unittest

from tests.engineering import d02_common as C

REQUIRED = ("source_repository", "source_commit", "source_file", "source_sha256", "drawing_revision", "part_id",
            "spec_digest", "requirements_digest", "predicate_id", "predicate_inputs", "units", "tolerances",
            "tolerance_sources", "brick_sha256", "ztl_engineer_commit", "ztl_stand_commit", "ztl_commit",
            "stand_verdict", "checker_result", "execution_timestamp")


class D02Binding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = C.A()
        cls.proof = C.controlled(False)[0]                  # real EARNED result
        cls.ctx = {k: cls.proof["binding"][k] for k in (*cls.a.CONTEXT_FIELDS, "policy_sha256")}

    def test_d02_c_every_binding_field_is_recorded_or_declared_missing(self):
        b = self.proof["binding"]
        for k in REQUIRED:
            self.assertIn(k, b)
        rt = C.runtime()
        self.assertEqual((b["ztl_engineer_commit"], b["ztl_stand_commit"], b["ztl_commit"]),
                         (rt.commits["ztl-engineer"], rt.commits["ztl-stand"], rt.commits["ZTL"]))
        absent = [k for k in REQUIRED if b[k] in (None, "")]
        self.assertEqual(set(absent) - set(self.proof["missing_blocks_admission"]), set(),
                         "a missing binding field must be declared, never filled in")
        self.assertIn("drawing_revision", self.proof["missing_blocks_admission"])  # no drawing exists: not invented

    def test_d02_08_altered_source_sha256_rejects_binding(self):
        rt = C.runtime()
        ex = C.stand_examples()[0]
        data = (rt.stand / ex["example"]).read_bytes()
        ctx = self.a.engineering_context(source_repository=ex["source_repository"], source_commit=ex["source_commit"],
                                         source_file=ex["example"], source_sha256=hashlib.sha256(data).hexdigest(),
                                         drawing_revision=None, spec_digest=None, requirements_digest=None)
        self.assertTrue(self.a.bind_source(ctx, data)["source_bytes_verified"])
        with self.assertRaises(self.a.BindingRejected):
            self.a.bind_source(ctx, data + b" ")
        with self.assertRaises(self.a.BindingRejected):
            self.a.bind_source(dict(ctx, source_sha256="0" * 64), data)

    def test_d02_08_proof_under_altered_source_is_not_used(self):
        ctx = dict(self.ctx, source_sha256="0" * 64)
        ok, why = self.a.proof_valid_for(self.proof, ctx)
        self.assertFalse(ok)
        self.assertIn("SOURCE_SHA256_CHANGED", why)
        agg = self.a.aggregate([self.proof], ctx, receipt={"verdict": "T", "code": "SYNTHETIC_CLAIM_FOR_TEST"})
        self.assertEqual(agg["ENGINEERING_VERDICT"], "Z")
        self.assertIn(self.proof["predicate_id"], agg["stale_proofs"])

    def test_d02_09_changed_revision_invalidates_old_proof(self):
        for k, v in (("drawing_revision", "v1.2_20261113"), ("source_commit", "f" * 40)):
            ok, why = self.a.proof_valid_for(self.proof, dict(self.ctx, **{k: v}))
            self.assertFalse(ok, k)
            self.assertIn(k.upper() + "_CHANGED", why)

    def test_d02_10_altered_requirement_digest_invalidates_old_proof(self):
        R, _, _ = self.a._deal_rescue()
        xcaf, readme, _ = C.fixture_inputs()
        d0 = R.requirements_digest(R.production_predicates(xcaf, readme, None))
        d1 = R.requirements_digest(R.production_predicates(xcaf, readme.replace("MGN9-170mm", "MGN9-150mm"), None))
        self.assertEqual(self.ctx["requirements_digest"], d0)
        self.assertNotEqual(d0, d1)
        ok, why = self.a.proof_valid_for(self.proof, dict(self.ctx, requirements_digest=d1))
        self.assertFalse(ok)
        self.assertIn("REQUIREMENTS_DIGEST_CHANGED", why)

    def test_d02_10_changed_policy_or_brick_invalidates_old_proof(self):
        ok, why = self.a.proof_valid_for(self.proof, dict(self.ctx, policy_sha256="1" * 64))
        self.assertIn("POLICY_SHA256_CHANGED", why)
        brick = copy.deepcopy(self.proof["mcp"]["request"]["params"]["arguments"]["brick"])
        brick["requirements"][0]["value"] = ["-0.5", "0.5"]
        ok, why = self.a.proof_valid_for(self.proof, self.ctx, brick)
        self.assertFalse(ok)
        self.assertIn("BRICK_CHANGED", why)

    def test_d02_c_same_context_keeps_the_proof(self):
        self.assertEqual(self.a.proof_valid_for(self.proof, self.ctx), (True, []))


if __name__ == "__main__":
    unittest.main()
