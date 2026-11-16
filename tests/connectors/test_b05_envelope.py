"""WO-B05: the LEGION envelope around Anthropic's contracts. Fixtures are the upstream contracts' own worked examples,
read from the vendored Markdown with their line ranges (source-bound)."""
import copy
import unittest

from manufacturing.adapters import envelope as E
from manufacturing.contracts import upstream as U

SCOPE = E.scope("fairview-tenant", ["erp:read", "docs:read"])


def example(name):
    return U.worked_example(U.load(name))


class B05(unittest.TestCase):
    def test_every_upstream_worked_example_is_accepted_unchanged(self):
        seen = 0
        for name in U.all_contract_names():
            ex = example(name)
            if not ex:
                continue
            seen += 1
            env = E.wrap(name, ex["record"], [E.binding("*", "upstream-example", "fairview-tenant",
                                                       f"{ex['source']['file']}:{ex['source']['lines']}", None)], SCOPE)
            self.assertIn(env["legion"]["verification"]["contract_check"]["status"], ("OK", "DEGRADED"), name)
            self.assertEqual(env["record"], ex["record"])
            self.assertTrue(E.verify_unchanged(env))
        self.assertEqual(seen, 9)

    def test_source_references_survive_and_tampering_is_detected(self):
        ex = example("geometry-estimate")
        b = E.binding("part_number", "netsuite", "fairview-tenant", "netsuite:item/1201", "4471-B")
        env = E.wrap("geometry-estimate", ex["record"], [b], SCOPE)
        self.assertEqual(env["record"]["part_number_verbatim"], "4471-B")
        self.assertEqual(env["legion"]["source_bindings"][0]["record_ref"], "netsuite:item/1201")
        env["record"]["stock"]["material"] = "6061"
        self.assertFalse(E.verify_unchanged(env))
        with self.assertRaises(E.EnvelopeError):
            E.combine([env], "geometry-estimate", ex["record"])

    def test_tenant_isolation(self):
        ex = example("ncr")["record"]
        with self.assertRaises(E.TenantIsolationError):
            E.wrap("ncr", ex, [E.binding("ncr_id", "m365", "other-tenant", "m365:message/1", "x")], SCOPE)
        a = E.wrap("ncr", ex, [], SCOPE)
        b = E.wrap("ncr", ex, [], E.scope("other-tenant", ["docs:read"]))
        with self.assertRaises(E.TenantIsolationError):
            E.combine([a, b], "ncr", ex)

    def test_permission_scope_survives_and_only_narrows(self):
        ex = example("supplier-caused-flag")["record"]
        a = E.wrap("supplier-caused-flag", ex, [], E.scope("t", ["erp:read", "docs:read"]))
        b = E.wrap("supplier-caused-flag", ex, [], E.scope("t", ["erp:read"]))
        out = E.combine([a, b], "supplier-caused-flag", ex)
        self.assertEqual(out["legion"]["permission_scope"], {"tenant": "t", "scopes": ["erp:read"], "mode": "read"})
        self.assertEqual(out["legion"]["derived_from"], [a["record_sha256"], b["record_sha256"]])
        with self.assertRaises(E.EnvelopeError):
            E.scope("t", ["erp:write"], mode="write")

    def test_missing_fields_are_never_filled(self):
        rec = copy.deepcopy(example("geometry-estimate")["record"])
        del rec["stock"]["material"]
        rec["approval"].pop("status")
        env = E.wrap("geometry-estimate", rec, [], SCOPE)
        chk = env["legion"]["verification"]["contract_check"]
        self.assertEqual(chk["status"], "BLOCK")
        self.assertEqual({b["field"] for b in chk["blocked"]}, {"material", "approval.status"})
        self.assertNotIn("material", env["record"]["stock"])
        E.absent(env, "stock.material", "drawing not supplied")
        self.assertEqual(env["legion"]["absent"], [{"field_path": "stock.material", "why": "drawing not supplied"}])

    def test_enum_outside_contract_is_blocked(self):
        rec = copy.deepcopy(example("geometry-estimate")["record"])
        rec["geometry_path"] = "C3"
        chk = E.wrap("geometry-estimate", rec, [], SCOPE)["legion"]["verification"]["contract_check"]
        self.assertEqual(chk["enum_violations"][0]["field"], "geometry_path")

    def test_disconnected_source_is_not_success(self):
        for state in ("DISCONNECTED", "CONFIGURED", "AUTHENTICATED", "SCOPED", "UNAVAILABLE"):
            env = E.wrap("ncr", example("ncr")["record"], [], SCOPE, connector_state=state)
            self.assertEqual((env["status"], env["record"]), ("UNAVAILABLE", None))
        with self.assertRaises(E.EnvelopeError):
            E.combine([env], "ncr", {})


if __name__ == "__main__":
    unittest.main()
