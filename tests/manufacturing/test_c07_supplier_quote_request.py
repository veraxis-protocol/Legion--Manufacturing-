"""C07 supplier-quote-request: revision, MOQ, lead time, terms and missing fields preserved in the bid; sourcing
blocks on an unapproved or revision-less supplier-caused flag."""
import copy
import unittest

from manufacturing.contracts import upstream as U
from manufacturing.runtime import gates as G
from tests.manufacturing import base

BID = U.load("supplier-bid")
FLAG = U.worked_example(U.load("supplier-caused-flag"))["record"]


class C07SupplierQuoteRequest(base.SkillSuite):
    CID = "C07"

    def test_c07_bid_fields_preserved(self):
        names = {f.name for f in BID.fields}
        for k in ("fields_missing", "supplier_id", "supplier_id_verbatim"):
            self.assertIn(k, names)
        bid = next(e["record"] for e in U.worked_examples(BID) if "bid_ref" in e["record"])
        for k in ("fields_missing", "supplier_id_verbatim"):
            self.assertIn(k, bid)

    def test_c07_sourcing_blocked_on_unapproved_or_revisionless_flag(self):
        self.assertEqual(G.admit("supplier-caused-flag", FLAG)["verdict"], "T")
        for k, v in (("approval_state", "draft"), ("part_revision", None), ("supplier_id", None)):
            rec = copy.deepcopy(FLAG)
            rec[k] = v
            self.assertEqual(G.admit("supplier-caused-flag", rec)["verdict"], "Z", k)


if __name__ == "__main__":
    unittest.main()
