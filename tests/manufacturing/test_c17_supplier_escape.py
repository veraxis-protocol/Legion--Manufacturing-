"""C17 supplier-escape-to-alternate-source: the supplier-caused claim must be approved before any sourcing starts."""
import copy
import unittest

from manufacturing.contracts import upstream as U
from manufacturing.runtime import gates as G
from tests.manufacturing import base

FLAG = U.worked_example(U.load("supplier-caused-flag"))["record"]


class C17SupplierEscape(base.SkillSuite):
    CID = "C17"

    def test_c17_claim_authorized_before_sourcing(self):
        self.assertEqual(FLAG["approval_state"], "approved")
        self.assertTrue(G.admit("supplier-caused-flag", FLAG, "sourcing")["consequential_execution_allowed"])
        for state in ("draft", "rejected", None):
            rec = copy.deepcopy(FLAG)
            rec["approval_state"] = state
            res = G.admit("supplier-caused-flag", rec, "sourcing")
            self.assertEqual(res["verdict"], "Z", state)
            self.assertFalse(res["consequential_execution_allowed"])

    def test_c17_no_supplier_message_is_sent(self):
        from manufacturing.connectors.m365 import M365
        from manufacturing.connectors.lifecycle import WriteRefused
        from tests.connectors.fakes import GraphFake
        a = M365(GraphFake(), {})
        a.connect({"granted_scopes": ["Mail.Read", "Mail.Send"]})
        with self.assertRaises(WriteRefused):
            a.request("POST", "/me/sendMail", {"to": "supplier@example.test"})
        self.assertEqual(a.log.writes, [])


if __name__ == "__main__":
    unittest.main()
