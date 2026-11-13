"""C02 custom-connector: a scoped connector is accepted, an untrusted one is rejected, and mapped rows meet the
consolidated-dataset's mapping requirements. Connecting a real third system stays BLOCKED."""
import unittest
from datetime import date

from manufacturing.adapters.dataset_rows import check_pull_row
from manufacturing.connectors import infor_m3 as M
from manufacturing.connectors.lifecycle import Lifecycle, LifecycleError, WriteRefused
from tests.connectors.fakes import M3Fake
from tests.manufacturing import base

SCOPE = {"facility": "F01", "warehouses": ["W01"]}


class C02CustomConnector(base.SkillSuite):
    CID = "C02"

    def test_c02_valid_scoped_connector_accepted(self):
        a = M.InforM3(M3Fake(), SCOPE)
        self.assertEqual(a.connect({"server": "m3"}), "VERIFIED")
        self.assertFalse(a.lc.grants_execution_authority)

    def test_c02_untrusted_connector_rejected(self):
        a = M.InforM3(M3Fake(), SCOPE)
        a.connect({"server": "m3"})
        with self.assertRaises(WriteRefused):
            a.read("PMS100MI_Release", {}, (date(2026, 1, 1), date(2026, 1, 2)))
        lc = Lifecycle("unknown-system")
        lc.configure({"url": "https://example.test"})
        self.assertEqual(lc.state, "CONFIGURED")               # a config file is not connectivity (INV-03)
        with self.assertRaises(LifecycleError):
            lc.require_verified()
        lc2 = Lifecycle("no-scope")
        lc2.configure({"x": 1})
        lc2.authenticated("tenant", None)
        lc2.scoped([])
        self.assertEqual(lc2.state, "UNAVAILABLE")

    def test_c02_mapping_requirements(self):
        a = M.InforM3(M3Fake(), SCOPE)
        row = a.inventory_rows([{"ItemNumber": "pn 4471b", "Location": "FG", "BatchNumber": "L1",
                                 "BalanceIdStatus": "2", "ApprovedOnHandBalance": "5",
                                 "BasicUnitOfMeasure": "EA", "Warehouse": "W01"}], "F01", "2026-10-01T00:00:00Z")[0]
        self.assertEqual(check_pull_row(row, "inventory")["status"], "OK")       # 1: the every-row columns
        self.assertEqual(row["part_number_verbatim"], "pn 4471b")                  # 2: the pair, verbatim kept
        for col in ("source_ref", "part_number_verbatim"):
            bad = dict(row)
            del bad[col]
            self.assertEqual(check_pull_row(bad, "inventory")["status"], "BLOCK", col)


if __name__ == "__main__":
    unittest.main()
