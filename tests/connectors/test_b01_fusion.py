"""WO-B01 contract suite: the Fusion MCP client and guard, on a scripted endpoint (fakes.py, SYNTHETIC).
B01 GO needs 10/10 on a real Fusion desktop; those live tests stay BLOCKED here (tools/connector_acceptance.py)."""
import unittest

from manufacturing.connectors import fusion as F
from manufacturing.connectors.lifecycle import NotVerified, WriteRefused
from tests.connectors.fakes import FusionFake


def connected(fake=None):
    a = F.Fusion(fake or FusionFake(), {})
    a.connect({"endpoint": F.endpoint({})})
    return a


class FusionContract(unittest.TestCase):
    def test_endpoint_comes_from_upstream_mcp_json(self):
        self.assertEqual(F.endpoint({}), "http://127.0.0.1:27182/mcp")
        self.assertEqual(F.endpoint({"FUSION_MCP_PORT": "30000"}), "http://127.0.0.1:30000/mcp")

    def test_t01_t02_connect_and_document_identity(self):
        a = connected()
        self.assertEqual(a.lc.state, "VERIFIED")
        self.assertEqual(a.base, {"name": "Bracket_Base", "version": 7, "modified": False})

    def test_t03_parameters_driving_vs_not(self):
        p = connected().read_parameters()
        self.assertTrue(p["flange_length"]["driving"])
        self.assertFalse(p["label_text"]["driving"])

    def test_t04_t05_t07_variant_in_new_document_base_untouched(self):
        fake = FusionFake()
        a = connected(fake)
        params = a.read_parameters()
        a.save_as_new("Bracket_V01")
        res = a.apply_parameters({"flange_length": "24 mm"}, params)
        self.assertEqual(res["variant"], "ok")
        self.assertEqual(res["properties"]["bodies"][0]["volume_cm3"], 44.4)
        self.assertEqual([w[1] for w in fake.writes], ["Bracket_V01", "Bracket_V01"])
        self.assertTrue(a.confirm_base_unchanged())

    def test_t05_unhealthy_regeneration_is_a_failed_variant(self):
        a = connected(FusionFake(healthy=False))
        params = a.read_parameters()
        a.save_as_new("Bracket_V02")
        res = a.apply_parameters({"flange_length": "99 mm"}, params)
        self.assertEqual((res["variant"], res["properties"]), ("failed", None))

    def test_t06_invalid_parameter_changes_rejected_before_any_call(self):
        fake = FusionFake()
        a = connected(fake)
        params = a.read_parameters()
        a.save_as_new("Bracket_V03")
        n = len(fake.calls)
        for bad in ({"nope": "1 mm"}, {"label_text": "'B'"}, {"flange_length": "24"}, {"flange_length": 24}):
            with self.assertRaises(F.ScriptRejected):
                a.apply_parameters(bad, params)
        self.assertEqual(len(fake.calls), n)

    def test_writes_only_after_save_as_new(self):
        fake = FusionFake()
        a = connected(fake)
        with self.assertRaises(WriteRefused):
            a.apply_parameters({"flange_length": "24 mm"}, a.read_parameters())
        with self.assertRaises(WriteRefused):
            a.save_as_new("Bracket_Base")
        self.assertEqual(fake.writes, [])

    def test_t07_moved_base_version_stops_the_run(self):
        a = connected(FusionFake(move_base=True))
        params = a.read_parameters()
        a.save_as_new("Bracket_V04")
        a.apply_parameters({"flange_length": "21 mm"}, params)
        self.assertFalse(a.confirm_base_unchanged())
        self.assertEqual(a.lc.state, "UNAVAILABLE")

    def test_t09_scripts_checked_and_reads_are_read_only(self):
        for bad in ("print(1)", "def run(ctx):\n    pass\n", "def run(context):\n    pass\nrun(None)\n", "def run(context:"):
            with self.assertRaises(F.ScriptRejected):
                F.check_script(bad)
        a = connected()
        with self.assertRaises(F.ScriptRejected):
            a._tool(F.READ_TOOL, "def run(context):\n    pass\n", False)
        reads = [c for c in a.log.calls if c["name"] == F.READ_TOOL]
        self.assertTrue(reads and all(c["args"]["readOnly"] for c in reads))

    def test_t10_unreachable_fails_closed(self):
        a = F.Fusion(FusionFake(reachable=False), {})
        a.connect({"endpoint": F.endpoint({})})
        self.assertEqual(a.lc.state, "UNAVAILABLE")
        self.assertIn("FUSION_MCP_UNREACHABLE", a.lc.history[-1][1])
        with self.assertRaises(NotVerified):
            a.read_parameters()

    def test_missing_tools_or_no_open_document(self):
        self.assertEqual(connected(FusionFake(tools=("other",))).lc.state, "UNAVAILABLE")
        self.assertEqual(connected(FusionFake(doc={"name": "", "version": None})).lc.state, "UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
