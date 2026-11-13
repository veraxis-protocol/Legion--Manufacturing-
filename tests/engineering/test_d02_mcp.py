"""WO-D02-A / B: pinned ZTL sources, the real ZTL Engineer MCP server, the real stand, and transport faults.

D02-01 source integrity, D02-02 MCP initializes, D02-03 check_design executes, D02-11 malformed brick -> Z,
D02-12 malformed MCP response -> Z (TRANSPORT_FAULT_INJECTION, labelled), D02-13 server unavailable -> Z,
D02-14 timeout -> Z. Real processes everywhere except the labelled D02-12 transport.
"""
import json
import tempfile
import unittest
from pathlib import Path

from legion.engineering import pinned_source as P
from tests.engineering import d02_common as C


class D02Sources(unittest.TestCase):
    def test_d02_01_pinned_ztl_sources_verified(self):
        pins = C.pins()
        manifest = P.load_manifest()
        self.assertEqual({r["name"] for r in manifest["repositories"]}, {"ztl-engineer", "ztl-stand", "ZTL"})
        for r in manifest["repositories"]:
            done = pins["repositories"][r["name"]]
            self.assertTrue(done["verified"])
            self.assertEqual(done["head"], r["commit"])
            self.assertEqual(pins["unchanged_after_use"][r["name"]], [], r["name"])
            paths = {f["path"] for f in r["files"]}
            for req in r["required_files"]:
                self.assertIn(req, paths)
                self.assertTrue((P.ROOT / "_deps" / r["name"] / req).is_file(), req)
        self.assertIn("Apache-2.0", manifest["repositories"][0]["license"]["spdx"])
        self.assertIn("Apache License", (P.ROOT / "_deps" / "ztl-engineer" / "LICENSE").read_text(encoding="utf-8"))
        self.assertIn("MIT", (P.ROOT / "_deps" / "ztl-stand" / "NOTICE").read_text(encoding="utf-8"))
        self.assertEqual(pins["deal_rescue"]["commit"], "6d5563af9a0eb838297933a8ae6b128defa9f69e")

    def test_d02_01_tampered_pin_is_refused(self):
        spec = json.loads(json.dumps(next(r for r in P.load_manifest()["repositories"] if r["name"] == "ZTL")))
        f = next(x for x in spec["files"] if x["path"] == "znumjudge.py")
        f["sha256"] = "0" * 64
        with self.assertRaises(P.SourceMismatch):
            P.materialize_repo(spec)
        P.materialize_repo(next(r for r in P.load_manifest()["repositories"] if r["name"] == "ZTL"))  # restore

    def test_d02_01_stand_reports_the_pinned_judge(self):
        rt = C.runtime()
        ex = C.stand_examples()[0]
        self.assertEqual(ex["mcp"]["stand_result"]["judge"], "ZTL " + rt.commits["ZTL"][:7])


class D02Mcp(unittest.TestCase):
    def test_d02_02_real_mcp_initializes(self):
        init = C.mcp_initialize()
        self.assertEqual(init["status"], "OK", init)
        self.assertTrue(init["initialized"])
        self.assertEqual(init["server_info"]["name"], "ztl-engineer")
        self.assertIn("check_design", init["tools"])

    def test_d02_03_real_check_design_executes(self):
        """The four existing ztl-stand examples: each verdict as the stand produced it, nothing predetermined."""
        a = C.A()
        for ex in C.stand_examples():
            self.assertEqual(ex["mcp"]["status"], "OK", ex["example"])
            self.assertTrue(ex["mcp"]["stand_called"])
            self.assertIn(ex["stand_verdict"], ("EARNED", "REFUTED", "OPEN", "BRICK ERROR", "STAND ERROR",
                                                "STAND FAULT"))
            self.assertEqual(ex["mcp"]["request"]["params"]["name"], "check_design")
            self.assertEqual(ex["legion_verdict"], a.VERDICT_MAP.get(ex["stand_verdict"], "Z")
                             if ex["independent_checker"]["verdict"] == ex["stand_verdict"] else "Z")

    def test_d02_03_same_result_as_the_deal_rescue_reference(self):
        par = C.deal_rescue_check_design_parity()
        self.assertEqual(par["deal_rescue_verdict"], par["legion_adapter_verdict"])
        self.assertEqual(par["deal_rescue_judge"], par["legion_judge"])

    def test_d02_11_malformed_brick_is_Z(self):
        for case in C.malformed_bricks():
            self.assertEqual(case["legion_verdict"], "Z", case)
            self.assertNotIn(case.get("stand_verdict"), ("EARNED", "REFUTED"), case)

    def test_d02_12_malformed_mcp_response_is_Z_TRANSPORT_FAULT_INJECTION(self):
        cases = C.transport_fault_injection()
        self.assertEqual(len(cases), 6)
        for case in cases:
            self.assertEqual(case["legion_verdict"], "Z", case)
            self.assertNotEqual(case["status"], "OK", case)

    def test_d02_13_server_unavailable_is_Z(self):
        r = C.server_unavailable()
        self.assertEqual((r["check_design_status"], r["initialize_status"], r["legion_verdict"]),
                         ("MCP_UNAVAILABLE", "MCP_UNAVAILABLE", "Z"))

    def test_d02_13_evaluate_with_unavailable_server_never_F(self):
        a = C.A()
        rt = C.runtime()
        with tempfile.TemporaryDirectory() as d:
            gone = a.Runtime(engineer=Path(d), stand=rt.stand, ztl=rt.ztl, commits=rt.commits)
            p = C.controlled(False)[1]                          # a predicate the real stand REFUTES
            brick = json.loads(json.dumps(p["mcp"]["request"]["params"]["arguments"]["brick"]))
            q = a.predicate(predicate_id="x", part_id="x", requirement="x", inputs={"a": {"value": "1", "source": "s"}},
                            units={"a": "mm"}, tolerances={"a": "t"}, tolerance_sources={"a": "s"}, brick=brick)
            r = a.evaluate(q, {"policy_sha256": a.POLICY_SHA256}, gone)
        self.assertEqual(r["verdict"], "Z")
        self.assertEqual(r["why"], "MCP_UNAVAILABLE")

    def test_d02_14_timeout_is_Z(self):
        r = C.timeout()
        self.assertEqual((r["status"], r["legion_verdict"]), ("MCP_TIMEOUT", "Z"))


if __name__ == "__main__":
    unittest.main()
