"""WO-D01: LEGION CAD reuse (pinned LEGION-Deal-Rescue) into Anthropic's geometry-estimate contract.

Offline class: always runs. Uses Deal-Rescue's own sample files and its own offline CAD-027 fixture (MINI_XCAF /
MINI_README in its tests/test_cad027_demo.py), materialized from the pinned commit and hash-verified.

RealStep class: the reBot STEP through OpenCascade. It needs cadquery-ocp and the pinned STEP (34.8 MB). With
LMFG_REAL_CAD=1 (the CI engineering job) a missing input is an ERROR, never a skip. Without it, the class is skipped
and reported NOT RUN by tools/skill_matrix.py, never PASS.
"""
import copy
import hashlib
import importlib.util
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from legion.engineering import pinned_source as P

P.materialize()
from legion.engineering import step_intake as S  # noqa: E402
from manufacturing.contracts import upstream as U  # noqa: E402

REAL = os.environ.get("LMFG_REAL_CAD") == "1"
SAMPLES = P.DEPS / "deal_rescue" / "industrial" / "samples"


def dr_fixture():
    P.import_path()
    if str(P.DEPS) not in __import__("sys").path:
        raise RuntimeError("pinned copy not on path")
    spec = importlib.util.spec_from_file_location("dr_test_cad027_demo", P.DEPS / "tests" / "test_cad027_demo.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Offline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dr = dr_fixture()
        readme = cls.dr.MINI_README
        cls.res = S.assemble({"stages": {}, "engineering_verdict": "Z"}, copy.deepcopy(cls.dr.MINI_XCAF), readme,
                             hashlib.sha256(readme.encode()).hexdigest(), "Fairview", "REBOT-MINI")

    def test_pinned_files_verified_and_licensed(self):
        pin = P.load_pin()
        self.assertEqual(pin["license"]["spdx"], "Apache-2.0")
        for f in pin["files"]:
            data = (P.DEPS / f["path"]).read_bytes()
            self.assertEqual(P.git_blob_sha1(data), f["git_blob"])
            self.assertEqual(hashlib.sha256(data).hexdigest(), f["sha256"])

    def test_tampered_pin_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            bad = json.loads(P.PIN.read_text(encoding="utf-8"))
            bad["files"][2]["sha256"] = "0" * 64
            pin = Path(td, "pin.json")
            pin.write_text(json.dumps(bad), encoding="utf-8")
            old = P.PIN
            P.PIN = pin
            try:
                with self.assertRaises(P.SourceMismatch):
                    P.materialize(Path(td, "deps"))
            finally:
                P.PIN = old

    def test_t03_bom_reconciled_on_the_existing_fixture(self):
        b = self.res["stages"]["bom"]
        self.assertEqual((b["status"], b["mandatory_positions"], b["mandatory_positions_matched"]), ("T", 2, 2))
        self.assertEqual(b["mandatory_instances_step"], b["mandatory_instances_readme"])

    def test_t03_quantity_change_is_F(self):
        x = copy.deepcopy(self.dr.MINI_XCAF)
        x["instances"]["02_Rack"] = 3
        r = S.assemble({"stages": {}}, x, self.dr.MINI_README, "b" * 64, "Fairview", "REBOT-MINI")
        self.assertEqual(r["stages"]["bom"]["status"], "F")
        self.assertIn({"part_id": "02_RACK", "readme": 2, "step": 3}, r["stages"]["bom"]["mismatches"])

    def test_t04_materials_and_tolerances_only_from_sources(self):
        req = self.res["stages"]["requirements"]
        self.assertEqual((req["materials_from_geometry"], req["tolerances_from_geometry"]), (0, 0))
        by = {p["part_id"]: p for p in req["parts"]}
        self.assertEqual(by["02_RACK"]["material"], "Aluminum Alloy 5052")
        self.assertTrue(by["02_RACK"]["material_source"].startswith("readme.md line "))
        self.assertIn("±0.02 mm", by["02_RACK"]["tolerance"])
        self.assertIsNone(by["01_FINGER"]["tolerance"])                    # printed part: no tolerance stated
        self.assertIn("dimensional_tolerances", by["01_FINGER"]["missing_requirements"])

    def test_t05_t06_revision_and_missing_requirements_recorded(self):
        rev = self.res["revision_evidence"]
        self.assertIsNone(rev["drawing_revision"])
        self.assertIsNone(rev["source_commit"])                            # not the pinned reBot file
        self.assertIn("independent Ed25519 attestation (CAD-025)",
                      self.res["stages"]["requirements"]["missing_for_engineering_T"])
        self.assertEqual(self.res["stages"]["verification"]["status"], "Z")
        self.assertEqual(self.res["engineering_verdict"], "Z")

    def test_handoff_is_a_valid_c1_geometry_estimate(self):
        envs = self.res["geometry_estimates"]
        self.assertEqual(len(envs), 1)
        env = envs[0]
        chk = env["legion"]["verification"]["contract_check"]
        self.assertNotEqual(chk["status"], "BLOCK", chk)
        rec = env["record"]
        self.assertEqual((rec["geometry_path"], rec["model"]["origin"], rec["model"]["cad_backend"]),
                         ("C1", "customer_step", "none"))
        self.assertEqual(rec["model"]["document_integrity"]["result"], "not_applicable")
        self.assertEqual(rec["approval"]["status"], "draft")
        self.assertEqual((rec["features"], rec["operations"]), ([], []))
        self.assertTrue(any(u["what"] == "feature list" for u in rec["unreadables"]))
        def keys(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    yield k
                    yield from keys(v)
            elif isinstance(o, list):
                for v in o:
                    yield from keys(v)
        # contract: "It carries no hours, no rates and no prices"
        self.assertFalse([k for k in keys(rec) if set(k.lower().split("_")) & {"hours", "hour", "price", "rate", "rates", "cost"}])
        self.assertEqual(U.load("geometry-estimate").version, rec["contract_version"])

    def test_t07_unsupported_inputs_are_Z(self):
        self.assertEqual(S.drawing_intake("part.stl", b"solid x\nendsolid x\n")["extraction"], "Z")
        self.assertEqual(S.drawing_intake("part.iges", b"x")["extraction"], "Z")
        self.assertEqual(S.drawing_intake("part.step", b"ISO-10303-21;")["extraction"], "Z")
        self.assertEqual(S.drawing_intake("../evil.csv", b"part_no,qty\nA,1\n")["extraction"], "Z")

    def test_t08_existing_samples_reproduce(self):
        dxf = S.drawing_intake("BRACKET-20-ANNOTATED.dxf", (SAMPLES / "BRACKET-20-ANNOTATED.dxf").read_bytes())
        js = S.drawing_intake("DEMO-BRACKET-20.json", (SAMPLES / "DEMO-BRACKET-20.json").read_bytes())
        self.assertEqual([(r["part_no"], r["quantity"]) for r in dxf["bom"]], [("SLS-BRACKET-REV-C", 20)])
        self.assertEqual([(r["part_no"], r["quantity"]) for r in js["bom"]], [("SLS-BRACKET-REV-C", 20)])
        self.assertEqual((dxf["engineering_verdict"], js["engineering_verdict"]), ("Z", "Z"))
        self.assertEqual(dxf["bom"][0]["part_no"], "SLS-BRACKET-REV-C")   # revision kept verbatim in the part id


@unittest.skipUnless(REAL, "NOT RUN: needs cadquery-ocp and the pinned reBot STEP (LMFG_REAL_CAD=1, CI engineering job)")
class RealStep(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import OCP  # noqa: F401  (with LMFG_REAL_CAD=1 an ImportError is an error, not a skip)
        cls.files = P.fetch_reference_cad()
        cls.pin = P.load_pin()
        sha = cls.pin["reference_cad"]["files"]["step"]["sha256"]
        cls.res = S.step_intake(cls.files["step"]["path"], cls.files["readme"]["path"], sha, "Reference", "REBOT-B601")

    def test_t01_t02_hash_and_structure(self):
        i = self.res["stages"]["intake"]
        base = self.pin["recorded_baseline"]["xcaf"]
        self.assertEqual(i["status"], "T")
        self.assertEqual(i["sha256"], self.pin["reference_cad"]["files"]["step"]["sha256"])
        self.assertEqual((i["assemblies"], i["leaf_definitions"], i["leaf_instances"], i["length_unit"]),
                         (base["assemblies"], base["leaf_definitions"], base["leaf_instances"], base["length_unit"]))
        self.assertEqual(i["inferred_fields"], [])

    def test_t03_t08_bom_40_of_40_and_53_of_53(self):
        b = self.res["stages"]["bom"]
        base = self.pin["recorded_baseline"]["bom"]
        self.assertEqual((b["mandatory_positions_matched"], b["mandatory_positions"]),
                         (base["mandatory_positions_matched"], base["mandatory_positions"]))
        self.assertEqual((b["mandatory_instances_step"], b["mandatory_instances_readme"]),
                         (base["mandatory_instances"], base["mandatory_instances"]))
        self.assertEqual(b["purchased_readme_positions"], base["purchased_readme_positions"])
        self.assertEqual(b["status"], "T")

    def test_t04_t05_t06_requirements_revision_handoff(self):
        req = self.res["stages"]["requirements"]
        self.assertEqual((req["materials_from_geometry"], req["tolerances_from_geometry"]), (0, 0))
        self.assertEqual(self.res["revision_evidence"]["source_commit"], self.pin["reference_cad"]["commit"])
        envs = self.res["geometry_estimates"]
        self.assertGreater(len(envs), 0)
        for env in envs:
            self.assertNotEqual(env["legion"]["verification"]["contract_check"]["status"], "BLOCK")
            self.assertEqual(env["record"]["geometry_path"], "C1")
        self.assertEqual(self.res["engineering_verdict"], "Z")

    def test_tampered_and_unreadable_step(self):
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td, "tampered.step")
            shutil.copyfile(self.files["step"]["path"], bad)
            with open(bad, "ab") as fp:
                fp.write(b"\n")
            r = S.step_intake(bad, self.files["readme"]["path"], self.pin["reference_cad"]["files"]["step"]["sha256"],
                              "Reference", "X")
            self.assertEqual(r["stages"]["intake"]["status"], "F")
            junk = Path(td, "junk.step")
            junk.write_bytes(b"ISO-10303-21;\nHEADER;\nENDSEC;\nEND-ISO-10303-21;\n")
            r = S.step_intake(junk, self.files["readme"]["path"], hashlib.sha256(junk.read_bytes()).hexdigest(),
                              "Reference", "X")
            self.assertEqual(r["stages"]["intake"]["status"], "Z")
            self.assertNotIn("geometry_estimates", r)


if __name__ == "__main__":
    unittest.main()
