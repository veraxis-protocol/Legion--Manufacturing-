"""C14 ncr-writeup: requirement, affected quantity and containment scope are present and gate the chain."""
import copy
import unittest

from manufacturing.contracts import upstream as U
from manufacturing.runtime import gates as G
from tests.manufacturing import base

NCR = U.worked_example(U.load("ncr"))["record"]


class C14NcrWriteup(base.SkillSuite):
    CID = "C14"

    def test_c14_requirement_quantity_containment(self):
        self.assertTrue(NCR["requirement_cited"])
        names = {f.name for f in U.load("ncr").fields}
        self.assertTrue({"qty_suspect", "scope_reasoning"} & names)
        self.assertTrue([k for k in NCR if k.startswith("containment") or k == "locations" or "location" in k])

    def test_c14_no_requirement_blocks(self):
        for flag in (True, False):
            rec = copy.deepcopy(NCR)
            rec["requirement_cited"] = None
            rec["requirement_not_locatable"] = flag
            self.assertEqual(G.admit("ncr", rec)["verdict"], "Z", flag)

    def test_c14_unapproved_ncr_is_not_customer_facing(self):
        rec = copy.deepcopy(NCR)
        rec["approval_state"] = "draft"
        self.assertEqual(G.admit("ncr", rec, purpose="customer-facing")["verdict"], "Z")

    def test_c14_register_record_meets_contract(self):
        reg = U.worked_example(U.load("quality-register-record"))["record"]
        self.assertNotEqual(U.check(reg, U.load("quality-register-record"))["status"], "BLOCK")


if __name__ == "__main__":
    unittest.main()
