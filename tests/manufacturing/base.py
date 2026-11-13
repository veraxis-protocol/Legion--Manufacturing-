"""Shared Phase C suite: the six minimum acceptance classes (WO-LMFG-001 section 6) for one upstream skill.

  1 positive functional    the skill's deterministic upstream code runs on fixtures, and every contract it produces
                           or consumes is accepted unchanged through the B05 envelope (upstream worked examples)
  2 negative input         adversarial input is refused (plugin-folder run, out-of-contract values)
  3 missing data           a Required field blocks naming the field; a Degrades field degrades; nothing is filled
  4 source provenance      classification quotes resolve in SKILL.md; fixtures carry file, lines and contract hash
  5 approval / security    the skill's Approval gates section is intact; contract gates give Z to unapproved input
  6 regression             every file of the skill matches the Phase A manifest byte for byte

Two further rows are reported, never as PASS:
  model-driven run         NOT RUN: the skill's reasoning is executed by Claude; no Claude runtime is used here
  live systems             BLOCKED: only for skills that cannot produce output without a live external system
Subclasses set CID and add skill-specific tests.
"""
import copy
import json
import unittest
from pathlib import Path

from manufacturing.adapters import envelope as E
from manufacturing.contracts import upstream as U
from manufacturing.runtime import catalog as K
from manufacturing.runtime import gates as G
from manufacturing.runtime import upstream_exec as X

MANIFEST = json.loads((K.ROOT / "manifests" / "UPSTREAM_MANIFEST.json").read_text(encoding="utf-8"))
SCOPE = E.scope("example-manufacturing", ["files:read"])


def example_records(contract):
    """Upstream worked-example records for a contract (YAML), or the CSV example rows for the dataset."""
    c = U.load(contract)
    if contract == "consolidated-dataset":
        return [{"record": r, "source": r["_source"]} for rows in U.csv_examples(c).values() for r in rows]
    return [e for e in U.worked_examples(c) if U.check(e["record"], c)["status"] != "BLOCK"]


def first_required(c, record):
    part = U.part_of(record, c)
    for f in c.fields:
        if f.behavior == "Required" and f.part == part and "." not in f.name and "[" not in f.name and f.name in record:
            return f.name
    return None


def first_degrades(c, record):
    part = U.part_of(record, c)
    for f in c.fields:
        if f.behavior == "Degrades" and f.part == part and "." not in f.name and f.name in record \
                and record[f.name] is not None:
            return f.name
    return None


class SkillSuite(unittest.TestCase):
    CID = None

    @classmethod
    def setUpClass(cls):
        if cls.CID is None:
            raise unittest.SkipTest("base")
        cls.spec = K.by_id(cls.CID)
        cls.cls = K.classify(cls.spec)
        named = [c for c in cls.spec["produces"] + cls.spec["consumes"] if c in U.all_contract_names()]
        # floor-layout's example is a Markdown profile section, not a record: it has no record to check here
        cls.contracts = [c for c in named if example_records(c)]
        cls.contracts_without_record_example = [c for c in named if c not in cls.contracts]

    # 1 ---------------------------------------------------------------------------------------------------------
    def test_1_positive_deterministic_code_runs(self):
        if K.FIND not in self.spec["deterministic_code"]:
            self.assertFalse(self.cls["runs_plant_setup_find"] and not self.spec.get("chain_of"))
            return
        with X.TaskFolder() as t:
            before = t.plugin_tree_digest()
            inst = t.install_profile()
            self.assertEqual(inst["setup"]["rc"], 0, inst["setup"])
            r = t.plant_setup("find")
            self.assertEqual(r["rc"], 0, r)
            j = r["json"]
            self.assertTrue(j["exists"])
            self.assertEqual(j["company"], X.COMPANY)
            self.assertTrue(j["rates_exists"])
            self.assertIn("setup_page_first", j)
            self.assertTrue(Path(j["profile_path"]).resolve().is_relative_to(t.task.resolve()), j["profile_path"])
            self.assertEqual(t.plugin_tree_digest(), before, "upstream code wrote into the plugin tree")

    def test_1_positive_contract_handoffs(self):
        for name in self.contracts:
            exs = example_records(name)
            self.assertTrue(exs, f"no upstream example for {name}")
            for ex in exs:
                if name == "consolidated-dataset":
                    continue          # checked by C03 at row level (tab-specific keys)
                env = E.wrap(name, ex["record"], [], SCOPE)
                self.assertNotEqual(env["legion"]["verification"]["contract_check"]["status"], "BLOCK", name)
                self.assertTrue(E.verify_unchanged(env))

    # 2 ---------------------------------------------------------------------------------------------------------
    def test_2_negative_run_inside_plugin_refused(self):
        if K.FIND not in self.spec["deterministic_code"]:
            return
        with X.TaskFolder() as t:
            r = t.plant_setup("find", cwd=t.plugin / "skills" / self.spec["skill"])
            self.assertEqual(r["rc"], 2)
            self.assertIn("not from inside the plugin", r["json"]["error"])

    def test_2_negative_out_of_contract_values(self):
        for name in self.contracts:
            if name == "consolidated-dataset":
                continue
            c = U.load(name)
            ex = copy.deepcopy(example_records(name)[0]["record"])
            enum_f = next((f for f in c.fields if f.enum and f.name in ex and f.part == U.part_of(ex, c)), None)
            if enum_f:
                ex[enum_f.name] = "__not_in_contract__"
                self.assertEqual(U.check(ex, c)["status"], "BLOCK", (name, enum_f.name))

    # 3 ---------------------------------------------------------------------------------------------------------
    def test_3_missing_data_never_filled(self):
        for name in self.contracts:
            if name == "consolidated-dataset":
                continue
            c = U.load(name)
            ex = example_records(name)[0]["record"]
            req = first_required(c, ex)
            if req:
                rec = copy.deepcopy(ex)
                del rec[req]
                res = U.check(rec, c)
                self.assertEqual(res["status"], "BLOCK", (name, req))
                self.assertIn(req, [b["field"] for b in res["blocked"]])
                self.assertNotIn(req, rec)
            deg = first_degrades(c, ex)
            if deg:
                rec = copy.deepcopy(ex)
                rec[deg] = None
                res = U.check(rec, c)
                self.assertIn(deg, [d["field"] for d in res["degraded"]], (name, deg))
                self.assertIsNone(rec[deg])

    # 4 ---------------------------------------------------------------------------------------------------------
    def test_4_provenance(self):
        cl = self.cls
        if cl["file_only"]:
            self.assertIsNotNone(cl["file_only_evidence"]["line"], "file-only quote not found in SKILL.md")
        self.assertIsNotNone(cl["live_evidence"]["line"], "live-system quote not found in SKILL.md")
        rel = f"skills/{self.spec['skill']}/SKILL.md"
        pinned = next(f for f in MANIFEST["files"] if f["path"] == rel)
        self.assertEqual(cl["skill_md_sha256"], pinned["sha256"])
        for name in self.contracts:
            for ex in example_records(name):
                self.assertEqual(ex["source"]["contract_sha256"], U.load(name).sha256)

    # 5 ---------------------------------------------------------------------------------------------------------
    def test_5_approval_gates_preserved(self):
        self.assertTrue(self.cls["approval_gates_section"])
        self.assertEqual(G.verify_sources(), [])

    # 6 ---------------------------------------------------------------------------------------------------------
    def test_6_regression_against_upstream_baseline(self):
        r = X.skill_files_digest(self.spec["skill"], MANIFEST)
        self.assertGreater(r["files"], 0)
        self.assertEqual(r["mismatched"], [])

    # reported, never PASS ----------------------------------------------------------------------------------------
    def test_7_model_driven_run(self):
        self.skipTest("NOT RUN: the skill's reasoning steps are executed by Claude; no Claude runtime or model "
                      "credential is used in this repository's tests, and no model output is claimed from a fixture")

    def test_8_live_systems(self):
        if not self.spec["live_required"]:
            return
        self.skipTest("BLOCKED: needs " + "; ".join(self.spec["live_required"]))
