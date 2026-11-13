"""WO-B04 contract suite: Infor M3 adapter against the rules in upstream shared/erp-connectors.md.

Contract tests on scripted M3 tool results (tests/connectors/fakes.py, SYNTHETIC). Live acceptance B04-T01..T10 is
tools/connector_acceptance.py and stays BLOCKED until an authorized M3 tenant is configured.
"""
import unittest
from datetime import date

from manufacturing.adapters.dataset_rows import check_pull_row
from manufacturing.connectors import infor_m3 as M
from manufacturing.connectors.lifecycle import LifecycleError, NotVerified, WriteRefused
from tests.connectors.fakes import M3Fake

SCOPE = {"facility": "F01", "warehouses": ["W01"], "m3_time_unit": "min"}
WIN = (date(2026, 10, 1), date(2026, 10, 31))


def connected(fake=None, scope=SCOPE):
    a = M.InforM3(fake or M3Fake(), scope)
    a.connect({"server": "m3-mcp"})
    return a


class AllowList(unittest.TestCase):
    def test_reads_come_from_the_upstream_table(self):
        self.assertIn("MMS060MI_List", M.ALLOWED)
        self.assertIn("PMS100MI_LstOperations", M.ALLOWED)
        self.assertIn(M.CONNECTION_TEST, M.ALLOWED)
        self.assertEqual(len(M.ALLOWED), 20)

    def test_documented_never_called_are_refused_without_a_call(self):
        fake = M3Fake()
        a = connected(fake)
        n = len(fake.calls)
        for call in sorted(M.NEVER) + ["PMS100MI_Release", "OIS100MI_AddHead", "MMS200MI_UpdItmBasic"]:
            with self.assertRaises(WriteRefused):
                a.read(call, {}, WIN)
        self.assertEqual(len(fake.calls), n, "a refused call must not reach the transport")
        self.assertEqual(a.log.writes, [])            # B04-T10


class Lifecycle(unittest.TestCase):
    def test_t01_t02_user_context_and_scope(self):
        a = connected()
        self.assertEqual(a.lc.state, "VERIFIED")
        self.assertEqual(a.lc.tenant, "100/AAA")
        self.assertEqual(a.lc.scopes, ("facility:F01", "warehouse:W01"))
        self.assertFalse(a.lc.grants_execution_authority)

    def test_facility_mismatch_is_unavailable(self):
        a = connected(M3Fake(user={"Company": "100", "Division": "AAA", "Facility": "F99"}))
        self.assertEqual(a.lc.state, "UNAVAILABLE")
        self.assertIn("FACILITY_MISMATCH", a.lc.history[-1][1])

    def test_no_profile_scope_is_unavailable_never_unfiltered(self):
        a = connected(scope={})
        self.assertEqual(a.lc.state, "UNAVAILABLE")

    def test_connection_test_error_is_unavailable(self):
        a = connected(M3Fake(errors={"MNS150MI_GetUserData_CurrentUser": "401 Unauthorized"}))
        self.assertEqual(a.lc.state, "UNAVAILABLE")
        with self.assertRaises(NotVerified):
            a.read("MMS060MI_List", {"Warehouse": "W01"}, WIN)

    def test_expired_credential_fails_closed(self):
        t = {"now": 0}
        a = M.InforM3(M3Fake(), SCOPE, clock=lambda: t["now"])
        a.connect({"server": "m3-mcp", "expires_at": 100})
        t["now"] = 101
        with self.assertRaises(NotVerified):
            a.read("MMS060MI_List", {"Warehouse": "W01"}, WIN)
        self.assertEqual(a.lc.state, "UNAVAILABLE")


class Reads(unittest.TestCase):
    def test_t03_item_master(self):
        fake = M3Fake(data={"MMS200MI_SearchItem": [{"ItemNumber": "PN-4471-B", "ItemName": "Bracket", "Status": "20",
                                                      "BasicUnitOfMeasure": "EA", "MakeBuyCode": "1"}]})
        r = connected(fake).read("MMS200MI_SearchItem", {}, WIN)
        self.assertEqual(r["rows"][0]["ItemNumber"], "PN-4471-B")
        self.assertEqual(fake.calls[-1][1]["Facility"], "F01")

    def test_t04_inspection_status_on_the_balance(self):
        a = connected()
        rows = a.inventory_rows([
            {"ItemNumber": "PN-1", "Location": "QC-HOLD", "BatchNumber": "L7", "BalanceIdStatus": "1",
             "ApprovedOnHandBalance": "40", "BasicUnitOfMeasure": "EA", "Warehouse": "W01"},
            {"ItemNumber": "PN-1", "Location": "FG-A1", "BatchNumber": "L7", "BalanceIdStatus": 2,
             "ApprovedOnHandBalance": "200", "BasicUnitOfMeasure": "EA", "Warehouse": "W01"},
            {"ItemNumber": "PN-1", "Location": "MRB", "BatchNumber": "L6", "BalanceIdStatus": "3",
             "ApprovedOnHandBalance": "5", "BasicUnitOfMeasure": "EA", "Warehouse": "W01"}], "F01", "2026-10-15T06:00:00Z")
        self.assertEqual([r["inspection_status"] for r in rows], ["under_inspection", "approved", "rejected"])
        self.assertEqual([r["available"] for r in rows], [False, True, False])
        self.assertEqual(rows[0]["lot_number_verbatim"], "L7")
        for r in rows:
            self.assertEqual(check_pull_row(r, "inventory")["status"], "OK")

    def test_t05_t06_operations_never_use_runtimehours(self):
        a = connected()
        ops = [{"OperationNumber": "20", "WorkCenter": "VMC-02", "SetupTime": "45", "RunTime": "7",
                "UsedLaborSetupTime": "50", "UsedLaborRunTime": "1400", "RunTimeHours": "23.33",
                "CompletedQuantity": "200", "ReportingDate": "20261015"}]
        row = a.operation_rows(ops, "F01", "4001015937", "PN-4471-B")[0]
        self.assertEqual(row["actual_run_hours"], 1400.0)
        self.assertNotIn(23.33, row.values())
        self.assertEqual((row["time_unit"], row["costable"]), ("min", True))
        self.assertEqual(row["closed_date"], "2026-10-15")
        unk = M.InforM3(M3Fake(), {**SCOPE, "m3_time_unit": None}).operation_rows(ops, "F01", "1", "P")[0]
        self.assertIsNone(unk["time_unit"])
        self.assertFalse(unk["costable"])
        self.assertIn("unit unconfirmed", unk["time_unit_flag"])

    def test_t07_purchase_orders_deleted_out_and_currency_never_assumed(self):
        a = connected()
        rows = a.purchase_rows([
            {"PurchaseOrderNumber": "P1", "LineNumber": 1, "SupplierNumber": "5120", "ItemNumber": "PN-1",
             "PurchasePrice": "12.5", "OrderedQuantity": "100", "BasicUnitOfMeasure": "EA", "HighestStatus": "75",
             "Currency": "USD"},
            {"PurchaseOrderNumber": "P2", "LineNumber": 1, "SupplierNumber": "5120", "ItemNumber": "PN-1",
             "PurchasePrice": "9", "OrderedQuantity": "100", "BasicUnitOfMeasure": "EA", "HighestStatus": "90"},
            {"PurchaseOrderNumber": "P3", "LineNumber": 1, "SupplierNumber": "5121", "ItemNumber": "PN-1",
             "PurchasePrice": "11", "OrderedQuantity": "50", "BasicUnitOfMeasure": "EA", "HighestStatus": "85"}],
            "F01")
        self.assertEqual([r["source_ref"] for r in rows], ["infor_m3:po/P1/1", "infor_m3:po/P3/1"])
        self.assertEqual(check_pull_row(rows[0], "purchase_orders")["status"], "DEGRADED")   # as_of unresolved
        bad = check_pull_row(rows[1], "purchase_orders")
        self.assertEqual(bad["status"], "BLOCK")                                             # amount, no currency
        self.assertIn("currency", [b["field"] for b in bad["blocked"]])

    def test_t08_pagination_slices_and_both_date_formats(self):
        def mos(args):
            a, b = args["FromDate"], args["ToDate"]
            n = 30 if (a, b) == ("20261001", "20261031") else 12
            return [{"ManufacturingOrderNumber": f"{a}-{i}", "ProductNumber": "PN-1", "WorkOrderStatus": "OrderCompleted",
                     "OrderedQuantity": "10", "StartDate": "2026-10-02", "PlannedFinishDate": "20261003"}
                    for i in range(n)]
        a = connected(M3Fake(data={"PMS100MI_SearchMO": mos}))
        r = a.read("PMS100MI_SearchMO", {}, WIN)
        self.assertTrue(r["sliced"])
        self.assertEqual(r["slices"], 3)
        self.assertEqual(len(r["rows"]), 24)
        row = a.work_order_rows(r["rows"][:1], "F01")[0]
        self.assertEqual((row["start_date"], row["due_date"]), ("2026-10-02", "2026-10-03"))
        self.assertTrue(row["closed"])
        self.assertIsNone(row["sales_order"])                  # no WO-to-SO link in the pull: null, not guessed

    def test_t09_none_found_is_empty_not_zero_and_other_errors_fail(self):
        a = connected(M3Fake(errors={"MMS060MI_List": "Record does not exist"}))
        r = a.read("MMS060MI_List", {"Warehouse": "W01"}, WIN)
        self.assertEqual((r["rows"], r["none_found"]), ([], True))
        b = connected(M3Fake(errors={"MMS060MI_List": "Transaction timed out"}))
        with self.assertRaises(M.M3CheckFailed):
            b.read("MMS060MI_List", {"Warehouse": "W01"}, WIN)

    def test_scope_and_filters_are_enforced(self):
        a = connected()
        with self.assertRaises(LifecycleError):
            a.read("MMS060MI_List", {"Warehouse": "W99"}, WIN)
        with self.assertRaises(LifecycleError):
            a.read("MMS060MI_List", {"Facility": "F02", "Warehouse": "W01"}, WIN)
        with self.assertRaises(LifecycleError):
            a.read("MMS060MI_List", {"Warehouse": "W01"}, (None, None))


if __name__ == "__main__":
    unittest.main()
