"""WO-B03 contract suite: Oracle NetSuite adapter (REST record service), on scripted responses (fakes.py, SYNTHETIC).
Live acceptance B03-T01..T10 stays BLOCKED until an authorized NetSuite account is configured."""
import unittest

from manufacturing.adapters.dataset_rows import can_aggregate, check_pull_row
from manufacturing.connectors import netsuite as N
from manufacturing.connectors.lifecycle import LifecycleError, NotVerified, WriteRefused
from tests.connectors.fakes import NetSuiteFake

SCOPE = {"subsidiary": "1", "locations": ["FAIRVIEW"]}


def connected(fake=None, cfg=None, scope=SCOPE):
    a = N.NetSuite(fake or NetSuiteFake(), scope)
    a.connect(cfg or {"account": "TSTDRV1234567"})
    return a


class NetSuiteContract(unittest.TestCase):
    def test_record_types_come_from_the_upstream_table(self):
        self.assertTrue({"item", "assemblyitem", "workorder", "salesorder", "itemfulfillment", "purchaseorder",
                         "vendor", "itemreceipt", "inventorynumber", "location"} <= N.RECORD_TYPES)

    def test_t01_t02_connection_and_scope(self):
        a = connected()
        self.assertEqual((a.lc.state, a.lc.tenant), ("VERIFIED", "TSTDRV1234567"))
        self.assertEqual(a.lc.scopes, ("location:FAIRVIEW", "subsidiary:1"))
        with self.assertRaises(LifecycleError):
            a.list("item", {"subsidiary": "2"})
        with self.assertRaises(LifecycleError):
            a.list("item", {"location": "BRANTFORD"})

    def test_t03_t10_item_identity_preserved(self):
        fake = NetSuiteFake(data={"item": [{"id": "1201", "itemId": "PN-4471-B", "displayName": "Bracket",
                                            "stockUnit": "each", "standardCost": "18.40", "currency": "USD",
                                            "lastModifiedDate": "2026-10-01T08:00:00-04:00"}]})
        a = connected(fake)
        rows = a.rows("item", a.list("item", {})["items"], "Fairview")
        self.assertEqual(rows[0]["source_ref"], "netsuite:item/1201")
        self.assertEqual(rows[0]["part_number_verbatim"], "PN-4471-B")
        self.assertEqual(check_pull_row(rows[0], "parts")["status"], "OK")

    def test_t04_supplier(self):
        a = connected(NetSuiteFake(data={"vendor": [{"id": "77", "entityId": "VEND-5120", "companyName": "Example Finishing"}]}))
        row = a.rows("vendor", a.list("vendor", {})["items"], "Fairview")[0]
        self.assertEqual((row["supplier_id"], row["supplier_name"]), ("VEND-5120", "Example Finishing"))

    def test_t05_t07_missing_cost_is_null_never_zero(self):
        a = connected(NetSuiteFake(data={"item": [{"id": "9", "itemId": "PN-9", "stockUnit": "each"}],
                                         "workorder": [{"id": "5", "tranId": "WO-88201", "assemblyItem": "PN-9",
                                                        "quantity": 10, "units": "each"}]}))
        item = a.rows("item", a.list("item", {})["items"], "Fairview")[0]
        wo = a.rows("workorder", a.list("workorder", {})["items"], "Fairview")[0]
        self.assertIsNone(item["amount"])
        self.assertIsNone(item["currency"])
        self.assertIsNone(wo["actual_cost"])
        self.assertIsNone(wo["sales_order"])

    def test_t06_demand_sign_convention_and_paging(self):
        so = [{"id": str(i), "tranId": f"SO-{i}", "item": "PN-1", "quantity": -5, "units": "each"} for i in range(5)]
        fake = NetSuiteFake(data={"salesorder": so}, pages={"salesorder": 2})
        a = connected(fake)
        res = a.list("salesorder", {})
        self.assertEqual(len(res["items"]), 5)
        self.assertEqual(len([c for c in fake.calls if c[1].endswith("/salesorder")]), 3)
        rows = a.rows("salesorder", res["items"], "Fairview")
        self.assertEqual((rows[0]["qty"], rows[0]["qty_verbatim"], rows[0]["integrity_flags"]), (5, -5, ["sign_convention"]))
        self.assertEqual(can_aggregate(rows)["total"], 25)
        rows[1]["uom"] = "box"
        self.assertIsNone(can_aggregate(rows)["total"])

    def test_t08_cross_tenant_denied(self):
        a = connected(NetSuiteFake(account="OTHER999"))
        self.assertEqual(a.lc.state, "UNAVAILABLE")
        self.assertIn("ACCOUNT_MISMATCH", a.lc.history[-1][1])
        with self.assertRaises(NotVerified):
            a.list("item", {})

    def test_t09_writes_refused_before_transport(self):
        fake = NetSuiteFake()
        a = connected(fake)
        n = len(fake.calls)
        for m, p in (("POST", "/services/rest/record/v1/purchaseorder"), ("PATCH", "/services/rest/record/v1/item/1"),
                     ("DELETE", "/services/rest/record/v1/workorder/5"),
                     ("POST", "/services/rest/record/v1/salesorder/1/!transform/itemFulfillment")):
            with self.assertRaises(WriteRefused):
                a.request(m, p)
        self.assertEqual(len(fake.calls), n)
        self.assertEqual(a.log.writes, [])

    def test_unlicensed_feature_is_blocked_not_empty(self):
        a = connected(NetSuiteFake(status={"assemblyitem": 403}))
        res = a.list("assemblyitem", {})
        self.assertTrue(res["denied"] and res["feature_blocked"])

    def test_expiry_mid_read_fails_closed(self):
        a = connected(NetSuiteFake(status={"item": 401}))
        with self.assertRaises(LifecycleError):
            a.list("item", {})
        self.assertEqual(a.lc.state, "UNAVAILABLE")

    def test_undocumented_record_type_refused(self):
        with self.assertRaises(LifecycleError):
            connected().list("employee", {})


if __name__ == "__main__":
    unittest.main()
