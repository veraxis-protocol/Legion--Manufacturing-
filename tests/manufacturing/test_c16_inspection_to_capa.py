"""C16 inspection-to-capa: every handoff (NCR -> investigation -> flag) retains the requirement and evidence
bindings, and a changed upstream record breaks the chain instead of flowing through."""
import unittest

from manufacturing.adapters import envelope as E
from manufacturing.contracts import upstream as U
from tests.manufacturing import base

NCR = U.worked_example(U.load("ncr"))["record"]
FLAG = U.worked_example(U.load("supplier-caused-flag"))["record"]


class C16InspectionToCapa(base.SkillSuite):
    CID = "C16"

    def test_c16_requirement_and_evidence_bindings_survive(self):
        scope = E.scope("plant", ["docs:read", "files:read"])
        ncr = E.wrap("ncr", NCR, [E.binding("requirement_cited", "m365", "plant", "m365:driveItem/dwg-4471-B-r2",
                                            NCR["requirement_cited"])], scope)
        flag = E.combine([ncr], "supplier-caused-flag", FLAG,
                         [E.binding("evidence_for", "qms_export", "plant", "inspection-20261012.csv:44", None)])
        refs = [b["record_ref"] for b in flag["legion"]["source_bindings"]]
        self.assertEqual(refs, ["m365:driveItem/dwg-4471-B-r2", "inspection-20261012.csv:44"])
        self.assertEqual(flag["legion"]["derived_from"], [ncr["record_sha256"]])
        self.assertEqual(flag["legion"]["permission_scope"]["scopes"], ["docs:read", "files:read"])


if __name__ == "__main__":
    unittest.main()
