"""C03 data-consolidate: join keys, units, counts, freshness and mismatches, on the contract's own CSV example."""
import unittest

from manufacturing.adapters.dataset_rows import can_aggregate
from manufacturing.contracts import upstream as U
from tests.manufacturing import base

DATASET = U.load("consolidated-dataset")
ROWS = U.csv_examples(DATASET)


class C03DataConsolidate(base.SkillSuite):
    CID = "C03"

    def test_c03_example_tabs_and_rows(self):
        self.assertEqual({t: len(r) for t, r in ROWS.items()},
                         {"inventory": 2, "production_output": 3, "routings": 1, "operation_actuals": 1})

    def test_c03_common_columns_and_key_pairs(self):
        js = next(f for f in DATASET.fields if f.name == "join_status")
        for tab, rows in ROWS.items():
            for r in rows:
                for col in ("site", "source_system", "source_ref", "as_of", "join_status"):
                    self.assertTrue(r[col], (tab, col))
                self.assertIn(r["join_status"], js.enum)
                for k in ("part_number", "production_wo", "work_center"):
                    if k in r:
                        self.assertIn(k + "_verbatim", r)

    def test_c03_mismatches_classified_not_dropped(self):
        po = ROWS["production_output"]
        self.assertEqual([(r["join_status"], r["mismatch_class"]) for r in po],
                         [("matched", ""), ("normalized", "2"), ("unmatched", "7")])
        self.assertEqual((po[1]["production_wo_verbatim"], po[1]["part_number_verbatim"]), ("wo 88202", "4471B"))

    def test_c03_units_and_counts(self):
        inv = [{"qty": float(r["qty"]), "uom": r["uom"]} for r in ROWS["inventory"]]
        self.assertEqual(can_aggregate(inv), {"total": 300.0, "uom": "each"})
        inv[1]["uom"] = None
        self.assertIsNone(can_aggregate(inv)["total"])
        r, a = ROWS["routings"][0], ROWS["operation_actuals"][0]
        self.assertEqual((r["run_time_unit"], r["routing_mismatch"]), ("min", "revision_mismatch"))
        self.assertIn("not converted", a["time_unit_flag"])
        self.assertEqual(a["actuals_confidence"], "probable_standard")

    def test_c03_freshness_as_of_carries_a_zone(self):
        for rows in ROWS.values():
            for r in rows:
                self.assertRegex(r["as_of"], r"[+-]\d\d:\d\d$")


if __name__ == "__main__":
    unittest.main()
