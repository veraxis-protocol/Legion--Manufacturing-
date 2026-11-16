"""C04 customer-inquiry-intake: the intake form is source-bound demand; unknowns stay unknown; gates hold."""
import copy
import unittest

from manufacturing.adapters import envelope as E
from manufacturing.connectors.m365 import M365
from manufacturing.contracts import upstream as U
from manufacturing.runtime import gates as G
from tests.connectors.fakes import GraphFake
from tests.connectors.test_b02_m365 import ROUTES, TENANT
from tests.manufacturing import base

FORM = U.worked_example(U.load("intake-form"))["record"]


class C04CustomerInquiryIntake(base.SkillSuite):
    CID = "C04"

    def test_c04_every_critical_field_has_provenance(self):
        self.assertTrue(FORM["field_sources"])
        self.assertEqual(G.admit("intake-form", FORM)["verdict"], "T")
        rec = copy.deepcopy(FORM)
        rec["field_sources"] = None
        self.assertEqual(G.admit("intake-form", rec)["verdict"], "Z")

    def test_c04_declined_or_superseded_inquiry_is_Z(self):
        for k, v in (("bid_decision_state", "declined"), ("inquiry_state", "superseded")):
            rec = copy.deepcopy(FORM)
            rec[k] = v
            res = G.admit("intake-form", rec)
            self.assertEqual(res["verdict"], "Z", k)
            self.assertFalse(res["consequential_execution_allowed"])

    def test_c04_rfq_source_identity_from_m365_survives_into_the_envelope(self):
        a = M365(GraphFake(TENANT, dict(ROUTES)), {})
        a.connect({"tenant_id": TENANT, "granted_scopes": ["Mail.Read"]})
        msg = a.rfq_messages("me", "RFQ")[0]
        env = E.wrap("intake-form", FORM, [E.binding("rfq_reference", "m365", TENANT, msg["source_ref"],
                                                     msg["internet_message_id"])], E.scope(TENANT, ["Mail.Read"]))
        self.assertEqual(env["legion"]["source_bindings"][0]["record_ref"], "m365:message/AAMkAD-rfq-1")
        self.assertEqual(env["record"], FORM)


if __name__ == "__main__":
    unittest.main()
