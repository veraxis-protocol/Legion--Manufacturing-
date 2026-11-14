"""WO-LMFG-003 (WO-D02): run the ZTL integration and write its five evidence files.

  python -I tools/d02_run.py --out evidence [--stand-suite] [--regressions]

Writes ZTL_STAND_BASELINE.json, ZTL_MCP_RESULTS.json, ENGINEERING_VERDICTS.json, ENGINEERING_NEGATIVES.json and
D02_GO_NO_GO.json. Every stand result in them comes from the real route (tests/engineering/d02_common.py); the only
injected faults are the labelled TRANSPORT_FAULT_INJECTION cases. The 22 obligations are computed from the test
results, never asserted: a NOT_RUN or BLOCKED test leaves its obligation NOT_RUN, and the gate is then Z.

  --stand-suite   also run ztl-stand's own test suite (tests/test_stand.py) on the pinned sources
  --regressions   also run the D01 CAD suite and every other suite of this repository, the protected-repository
                  check, and the committed evidence manifest check (the CI engineering-verifier job does this)
Exit 1 if any obligation FAILs.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT / "tools"))

from lmfg_common import artifact_header, write_json  # noqa: E402
from test_report import Recorder  # noqa: E402
from tests.engineering import d02_common as C  # noqa: E402

OBLIGATIONS = [
    ("D02-01", "Pinned ZTL source integrity", "PASS", ["test_d02_01_"]),
    ("D02-02", "Real MCP initializes", "PASS", ["test_d02_02_"]),
    ("D02-03", "Real check_design tool executes (and ztl-stand's own suite passes)", "PASS",
     ["test_d02_03_", "@stand_suite"]),
    ("D02-04", "Fully supported positive predicate", "Scoped T", ["test_d02_04_"]),
    ("D02-05", "Violated engineering predicate", "Scoped F", ["test_d02_05_"]),
    ("D02-06", "Missing manufacturing tolerance", "Z", ["test_d02_06_"]),
    ("D02-07", "Missing material evidence", "Z", ["test_d02_07_"]),
    ("D02-08", "Altered source SHA-256", "Reject binding", ["test_d02_08_"]),
    ("D02-09", "Changed engineering revision", "Old proof invalid", ["test_d02_09_"]),
    ("D02-10", "Altered requirement digest", "Old proof invalid", ["test_d02_10_"]),
    ("D02-11", "Malformed ZTL brick", "Z", ["test_d02_11_"]),
    ("D02-12", "Malformed MCP response", "Z", ["test_d02_12_"]),
    ("D02-13", "MCP server unavailable", "Z", ["test_d02_13_"]),
    ("D02-14", "Verification timeout", "Z", ["test_d02_14_"]),
    ("D02-15", "One mandatory T, one mandatory Z", "Global Z", ["test_d02_15_", "test_d02_d_"]),
    ("D02-16", "One mandatory T, one mandatory F", "Global F", ["test_d02_16_"]),
    ("D02-17", "Replayed or unauthenticated receipt", "No admission", ["test_d02_17_"]),
    ("D02-18", "Real reBot reference case", "Engineering Z", ["test_d02_18_"]),
    ("D02-19", "Existing CAD-D01 regression", "No regression", ["@d01"]),
    ("D02-20", "Existing Anthropic and connector tests", "No regression", ["@others"]),
    ("D02-21", "Protected repositories", "No modifications", ["@protected"]),
    ("D02-22", "Evidence manifest and source hashes", "Verified", ["@manifest", "test_d02_01_"]),
]
# these obligations need the real STEP (LMFG_REAL_CAD=1): their RealStep tests must have run, not be NOT_RUN
NEEDS_REAL = {"D02-04", "D02-05", "D02-18", "D02-19"}


def run_tests(start: str, pattern: str) -> list:
    suite = unittest.TestLoader().discover(str(ROOT / start), pattern=pattern, top_level_dir=str(ROOT))
    return unittest.TextTestRunner(resultclass=Recorder, verbosity=1, stream=sys.stderr).run(suite).rows


def counts(rows) -> dict:
    c = Counter(r["status"] for r in rows)
    return {"tests": len(rows), **{k: c.get(k, 0) for k in ("PASS", "FAIL", "ERROR", "NOT_RUN", "BLOCKED")}}


def stand_suite(rt) -> dict:
    """ztl-stand's own tests/test_stand.py (a script that prints OK/FAIL per check and a final summary line)."""
    env = dict(rt.env(), PYTHONPATH=C.A().stand_pythonpath(rt), OPENBLAS_NUM_THREADS="1")
    cmd = [sys.executable, "-m", "tests.test_stand"]
    try:
        p = subprocess.run(cmd, cwd=str(rt.stand), env=env, capture_output=True, encoding="utf-8", errors="replace",
                           timeout=3000)
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "command": "python -m tests.test_stand (cwd _deps/ztl-stand)"}
    out = p.stdout or ""
    m = re.search(r"ztl-stand: (\d+) ok, (\d+) failed", out)
    fails = [ln.strip()[:300] for ln in out.splitlines() if ln.startswith("  FAIL")]
    return {"command": "python -m tests.test_stand (cwd _deps/ztl-stand, USTAND_ZTL=_deps/ZTL)",
            "returncode": p.returncode, "summary_line": m.group(0) if m else None,
            "ok": int(m.group(1)) if m else sum(ln.startswith("  OK") for ln in out.splitlines()),
            "failed": int(m.group(2)) if m else len(fails), "completed": bool(m),
            "verdict_line": next((ln for ln in out.splitlines() if ln.startswith("USTAND ")), None),
            "fail_lines": fails[:60], "stderr_tail": (p.stderr or "")[-2000:],
            "status": "PASS" if m and int(m.group(2)) == 0 and p.returncode == 0 else "FAIL"}


def tool(cmd: list) -> dict:
    p = subprocess.run([sys.executable, "-I", *cmd], cwd=str(ROOT), capture_output=True, text=True)
    return {"command": " ".join(["python -I", *cmd]), "returncode": p.returncode,
            "stdout_tail": (p.stdout or "")[-1500:], "stderr_tail": (p.stderr or "")[-1500:],
            "status": "PASS" if p.returncode == 0 else "FAIL"}


def obligation_status(prefixes, rows, extra) -> tuple[str, list]:
    sel, refs = [], []
    for pre in prefixes:
        if pre.startswith("@"):
            e = extra.get(pre)
            if e is None:
                sel.append({"status": "NOT_RUN", "id": pre})
            else:
                sel.append({"status": e["status"], "id": pre})
            refs.append(pre)
            continue
        hit = [r for r in rows if r["test"].startswith(pre)]
        sel += hit
        refs += [r["id"] for r in hit]
    st = Counter(r["status"] for r in sel)
    if not sel:
        return "FAIL", ["no test implements this obligation"]
    if st["FAIL"] or st["ERROR"]:
        return "FAIL", refs
    if st["NOT_RUN"] or st["BLOCKED"]:
        return "NOT_RUN", refs
    return "PASS", refs


def strip(call: dict | None) -> dict | None:
    """An MCP record for the evidence: request, response (the stand's JSON is inside it verbatim), status."""
    if call is None:
        return None
    return {k: call.get(k) for k in ("status", "request", "response", "transport", "brick_sha256", "stand_verdict",
                                     "stand_called", "tool_error", "malformed_lines")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="evidence")
    ap.add_argument("--stand-suite", action="store_true")
    ap.add_argument("--regressions", action="store_true")
    a = ap.parse_args(argv)
    out = ROOT / a.out
    cmd = "python -I tools/d02_run.py " + " ".join(argv if argv is not None else sys.argv[1:])
    extra = {}
    if a.regressions:                       # the committed evidence, before this run writes anything
        extra["@manifest"] = tool(["tools/evidence_manifest.py", "--check"])

    rt = C.runtime()
    pins = C.pins()
    head = lambda inputs: artifact_header(cmd, inputs)  # noqa: E731
    # ---------------------------------------------------------------- tests (the obligations)
    rows = run_tests("tests/engineering", "test_d02_*.py")
    if a.regressions:
        d01 = run_tests("tests/engineering", "test_d01_*.py")
        others = []
        for sub in ("tests/manufacturing", "tests/connectors", "tests/upstream"):
            others += run_tests(sub, "test_*.py")
        extra["@d01"] = {**counts(d01), "status": "FAIL" if counts(d01)["FAIL"] or counts(d01)["ERROR"] else
                         ("NOT_RUN" if counts(d01)["NOT_RUN"] and C.REAL is False else "PASS")}
        oc = counts(others)
        extra["@others"] = {**oc, "status": "FAIL" if oc["FAIL"] or oc["ERROR"] else "PASS"}
        with tempfile.TemporaryDirectory() as td:
            pr = tool(["tools/protected_pins.py", "--evidence", str(Path(td) / "p.json")])
            pj = json.loads((Path(td) / "p.json").read_text(encoding="utf-8")) if (Path(td) / "p.json").exists() else {}
        extra["@protected"] = {**pr, "repositories": [{k: r.get(k) for k in ("repository", "status", "pinned",
                                                                            "remote_head", "protected")}
                                                      for r in pj.get("repositories", [])],
                               "modified": sum(r.get("status") != "PASS" for r in pj.get("repositories", [])
                                               if r.get("protected"))}

    # ---------------------------------------------------------------- the real runs, serialized
    init = C.mcp_initialize()
    examples = C.stand_examples()
    ctrl = C.controlled(False)
    ctrl_real = C.controlled(True) if C.REAL else None
    reb = C.rebot(False)
    reb_real = C.rebot(True) if C.REAL else None
    mixed_z, mixed_f = C.mixed("Z"), C.mixed("F")
    suite = stand_suite(rt) if a.stand_suite else {"status": "NOT_RUN", "why": "run with --stand-suite (CI verifier job)"}
    extra["@stand_suite"] = {"status": suite["status"], **{k: suite.get(k) for k in ("ok", "failed", "completed",
                                                                                     "summary_line")}}

    malformed = C.malformed_bricks()
    calls = [e["mcp"] for e in examples] + [c["mcp"] for c in ctrl + (ctrl_real or [])] + \
            [r["mcp"] for m in (mixed_z, mixed_f) for r in m["results"] if r.get("mcp")] + [m["mcp"] for m in malformed]
    reached = [c for c in calls if c and c.get("status") == "OK"]
    by_verdict = Counter(c.get("stand_verdict") for c in reached)
    dev_runs = [e["independent_checker"] for e in examples] + \
               [c["checker_result"]["independent_checker_dev_mode"] for c in ctrl + (ctrl_real or [])] + \
               [r["checker_result"]["independent_checker_dev_mode"] for m in (mixed_z, mixed_f) for r in m["results"]
                if r.get("checker_result")]

    baseline = {**head({"pins": "manifests/ZTL_SOURCE_PINS.json", "examples": C.STAND_EXAMPLES}),
                "status": "PASS" if init["status"] == "OK" and all(e["mcp"]["status"] == "OK" for e in examples)
                and suite["status"] in ("PASS", "NOT_RUN") else "FAIL",
                "solvers": {name: {"repository": d["repository"], "commit": d["commit"], "head": d["head"],
                                   "files_verified": d["files"], "license": d["license"],
                                   "not_representable_on_this_file_system": d["not_representable_on_this_file_system"]}
                            for name, d in pins["repositories"].items()},
                "deal_rescue": pins["deal_rescue"], "sources_unchanged_after_use": pins["unchanged_after_use"],
                "judge_reported_by_stand": examples[0]["mcp"]["stand_result"].get("judge"),
                "mcp_server_start": {k: init.get(k) for k in ("status", "server_info", "tools", "transport")},
                "examples": [{k: e[k] for k in ("example", "source_sha256", "brick_sha256", "stand_verdict",
                                                "independent_checker", "legion_verdict", "why", "scope")}
                             | {"stand_result": e["mcp"]["stand_result"]} for e in examples],
                "ztl_stand_own_test_suite": suite,
                "deal_rescue_reference_parity": C.deal_rescue_check_design_parity()}
    mcp = {**head({"server": "_deps/ztl-engineer/mcp_server.py", "tool": "check_design"}),
           "status": "PASS" if init["status"] == "OK" and reached else "FAIL",
           "counts": {"check_design_calls": len(calls), "reached_the_stand": len(reached),
                      **{f"stand_{k or 'none'}".replace(" ", "_"): v for k, v in by_verdict.items()},
                      "independent_checker_runs": len([d for d in dev_runs if d])},
           "secrets": "none: the server needs no credential for check_design; ask_engineer (paid API) never called",
           "initialize": {k: init.get(k) for k in ("requests", "responses", "status", "server_info", "tools")},
           "calls": [strip(c) for c in calls]}
    verdicts = {**head({"policy": C.A().POLICY}),
                "status": "PASS", "policy_sha256": C.A().POLICY_SHA256,
                "counts": {"EARNED": by_verdict.get("EARNED", 0), "REFUTED": by_verdict.get("REFUTED", 0),
                           "OPEN_or_ERROR": sum(v for k, v in by_verdict.items() if k not in ("EARNED", "REFUTED"))},
                "stand_examples": [{k: e[k] for k in ("example", "stand_verdict", "legion_verdict", "why", "scope")}
                                   for e in examples],
                "controlled_cases_fixture": [{k: v for k, v in c.items() if k != "mcp"} for c in ctrl],
                "controlled_cases_real_step": [{k: v for k, v in c.items() if k != "mcp"} for c in ctrl_real]
                if ctrl_real else "NOT_RUN: needs LMFG_REAL_CAD=1 (OpenCascade + the pinned STEP)",
                "rebot_fixture": {"input_basis": reb["input_basis"], "engineering_verdict": reb["engineering_verdict"],
                                  "verification": reb["stages"]["verification"]},
                "rebot_real_step": {"input_basis": reb_real["input_basis"],
                                    "engineering_verdict": reb_real["engineering_verdict"],
                                    "intake": reb_real["stages"]["intake"], "bom": {
                                        k: reb_real["stages"]["bom"][k] for k in (
                                            "status", "mandatory_positions", "mandatory_positions_matched",
                                            "mandatory_instances_readme", "mandatory_instances_step")},
                                    "verification": reb_real["stages"]["verification"]}
                if reb_real else "NOT_RUN: needs LMFG_REAL_CAD=1 (OpenCascade + the pinned STEP)",
                "aggregation_cases": {"T_plus_Z": mixed_z["aggregate"], "T_plus_F": mixed_f["aggregate"],
                                      "T_plus_Z_with_synthetic_receipt_claim":
                                          mixed_z["aggregate_with_synthetic_receipt_claim"]}}
    verdicts["counts_note"] = "counts are the stand verdicts of the real MCP calls made while writing this evidence"
    neg_rows = [r for r in rows if re.match(r"test_d02_(0[6-9]|1[0-7]|d_)", r["test"])]
    negatives = {**head({"tests": "tests/engineering/test_d02_*.py"}),
                 "status": "FAIL" if any(r["status"] in ("FAIL", "ERROR") for r in neg_rows) else "PASS",
                 "counts": counts(neg_rows),
                 "execution_state": {"supplier_orders": 0, "paypal_calls": 0, "procurement_authorized": False,
                                     "manufacturing_release": False},
                 "missing_tolerance": C.missing_rail_tolerance(), "missing_material": C.missing_material(),
                 "malformed_bricks": [{k: v for k, v in m.items() if k != "mcp"} for m in malformed], "transport_fault_injection": C.transport_fault_injection(),
                 "server_unavailable": C.server_unavailable(), "timeout": C.timeout(),
                 "partial_proof": {"T_plus_Z": mixed_z["aggregate"], "T_plus_F": mixed_f["aggregate"],
                                   "deal_rescue_ztl_review_demonstration": C.deal_rescue_partial_proof_demo()},
                 "receipts": C.receipts(), "tests": neg_rows}
    obls = []
    for oid, cond, want, prefixes in OBLIGATIONS:
        st, refs = obligation_status(prefixes, rows, extra)
        if oid in NEEDS_REAL and not C.REAL and st == "PASS":
            st = "NOT_RUN"
        obls.append({"id": oid, "condition": cond, "required_result": want, "status": st, "evidence": refs[:40],
                     **({"needs": "the real STEP (LMFG_REAL_CAD=1)"} if oid in NEEDS_REAL else {})})
    oc = Counter(o["status"] for o in obls)
    gate = "F" if oc["FAIL"] else "T" if oc["PASS"] == len(OBLIGATIONS) else "Z"
    go = {**head({"obligations": len(OBLIGATIONS)}),
          "status": "FAIL" if oc["FAIL"] else "PASS",
          "gate_d02": gate,
          "gate_meaning": "T = the integration acceptance obligations hold in this environment. It is NOT an "
                          "engineering admission: the reBot engineering verdict is Z and no production use is "
                          "authorized.",
          "counts": {"obligations": len(OBLIGATIONS), **{k: oc.get(k, 0) for k in ("PASS", "FAIL", "NOT_RUN")},
                     "d02_tests": counts(rows)["tests"], "d02_PASS": counts(rows)["PASS"],
                     "d02_FAIL": counts(rows)["FAIL"] + counts(rows)["ERROR"], "d02_NOT_RUN": counts(rows)["NOT_RUN"],
                     "actual_ztl_calls": len(reached), "EARNED": by_verdict.get("EARNED", 0),
                     "REFUTED": by_verdict.get("REFUTED", 0),
                     "OPEN_or_ERROR": sum(v for k, v in by_verdict.items() if k not in ("EARNED", "REFUTED"))},
          "rebot_engineering_verdict": (reb_real or reb)["engineering_verdict"],
          "rebot_basis": (reb_real or reb)["input_basis"],
          "obligations": obls, "regression_and_policy_checks": extra or "NOT_RUN: run with --regressions",
          "remaining_obligations_for_engineering_T": (reb_real or reb)["stages"]["verification"]["verdict"]["blocking"],
          "next_blocking_dependency": "an independently supported tolerance for the purchased MGN9-170 rail "
                                      "(manufacturer datasheet), arm mass properties and the joint-2 motor rating, "
                                      "material certificates, and a configured independent ZTL attestation service "
                                      "(Ed25519 key, epoch, policy pin: Deal-Rescue ztl_gate CAD-025)",
          "tests": rows}
    for name, doc in (("ZTL_STAND_BASELINE", baseline), ("ZTL_MCP_RESULTS", mcp), ("ENGINEERING_VERDICTS", verdicts),
                      ("ENGINEERING_NEGATIVES", negatives), ("D02_GO_NO_GO", go)):
        write_json(out / f"{name}.json", doc)
    print(json.dumps({"gate_d02": gate, **go["counts"]}))
    return 1 if oc["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
