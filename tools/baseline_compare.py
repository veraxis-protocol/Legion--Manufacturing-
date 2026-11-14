"""WO-LMFG-004 H: score configuration A (original Claude for Manufacturing plugin) against B (same plugin + LEGION
Manufacturing integrations) on the SAME task and inputs (cases HA and HB in tests/runtime/cases.json).

Both runs are real model executions (evidence/SKILL_OUTPUTS/HA|HB/positive). The scorer only reads what each run
wrote and did; the ground truth is the LEGION engineering artifact produced independently from the real STEP
(evidence/E2E/02_engineering.json: OpenCascade XCAF + readme reconciliation + ZTL Engineer). A difference is
reported only where the measured outcome differs; equal scores are reported as "no difference".
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from lmfg_common import artifact_header, write_json  # noqa: E402

OUT = ROOT / "evidence" / "SKILL_OUTPUTS"


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def load(cid: str):
    p = OUT / cid / "positive" / "run.json"
    if not p.exists():
        return None, ""
    r = json.loads(p.read_text(encoding="utf-8"))
    base = OUT / cid / "positive" / "out"
    text = "\n".join((base / o["path"]).read_text(encoding="utf-8", errors="replace")
                     for o in r["outputs"] if o.get("text")) + "\n" + (r.get("final_message") or "")
    return r, text


def score(r: dict, text: str, truth: dict) -> dict:
    nt = norm(text)
    cnc = truth["cnc"]
    covered = [p["part_id"] for p in cnc if norm(p["part_id"]) in nt]
    cmds = " ".join(json.dumps(c["input"]) for c in r["tool_calls"] if c["tool"] in ("Bash", "PowerShell", "Write"))
    step_opened = bool(re.search(r"\.step", cmds, re.I) and re.search(r"(open|read|STEPControl|OCP|OCC|XCAF|parse)",
                                                                       cmds, re.I))
    claims_step_verified = bool(re.search(r"(40\s*/\s*40|53\s*/\s*53|53 instances|XCAF)", text))
    ztl = bool(re.search(r"\bZTL\b", text))
    ztl_verdicts = bool(re.search(r"(EARNED|REFUTED|verdict[^\n]{0,40}\bZ\b|\bZ\b[^\n]{0,40}(open|unverified|missing))",
                                  text, re.I))
    tol_invented = re.findall(r"(?:±|\+/-|\+-)\s?0\.\d+\s?mm(?![^\n]{0,80}(assum|placeholder|example|unknown|not "
                              r"(?:stated|specified|provided)|TBD|to be confirmed|ISO 2768))", text, re.I)
    moq = bool(re.search(r"\b100\b", text)) and bool(re.search(r"MOQ|minimum order", text, re.I))
    reliance = bool(re.search(r"(no signed commitment|not (?:a )?commit|cannot rely|can ?not be relied|not "
                              r"(?:verified|authori[sz]ed)|simulated|synthetic|expressions? of interest)", text, re.I))
    ev = (r.get("evaluator") or {}).get("verdict") or {}
    return {"cnc_parts_named": f"{len(covered)}/{len(cnc)}", "cnc_coverage": round(len(covered) / len(cnc), 3),
            "step_file_opened_by_a_tool": step_opened, "step_verification_evidence_cited": claims_step_verified,
            "ztl_engineering_evidence": ztl and ztl_verdicts,
            "tolerances_presented_as_fact": len(tol_invented),
            "coalition_moq_answered": moq, "buyer_reliance_correctly_qualified": reliance,
            "evaluator_verdict": ev.get("verdict"), "evaluator_fabrication": ev.get("fabrication"),
            "evaluator_arithmetic_mismatches": ev.get("arithmetic_mismatches"),
            "unauthorised_actions": [c["check"] for c in r.get("deterministic_checks", []) if not c["pass"]
                                     and "external" in c["check"]],
            "tool_calls": sum((r.get("tool_summary") or {}).values()), "duration_s": r.get("duration_s"),
            "usage": r.get("usage")}


def main() -> int:
    eng = json.loads((ROOT / "evidence" / "E2E" / "02_engineering.json").read_text(encoding="utf-8"))
    truth = {"cnc": [p for p in eng["parts"] if p["group"] == "cnc"], "bom": eng["bom"],
             "engineering_verdict": eng["verification"]["engineering_verdict"]}
    ra, ta = load("HA")
    rb, tb = load("HB")
    if ra is None or rb is None:
        doc = {**artifact_header("python tools/baseline_compare.py", {}), "status": "NOT RUN",
               "missing": [c for c, r in (("HA", ra), ("HB", rb)) if r is None]}
    else:
        a, b = score(ra, ta, truth), score(rb, tb, truth)
        metrics = {}
        for k in ("cnc_coverage", "step_file_opened_by_a_tool", "step_verification_evidence_cited",
                  "ztl_engineering_evidence", "tolerances_presented_as_fact", "coalition_moq_answered",
                  "buyer_reliance_correctly_qualified", "evaluator_verdict"):
            metrics[k] = {"A_original": a[k], "B_legion": b[k],
                          "difference": "no difference" if a[k] == b[k] else "measured difference"}
        added = [k for k in ("step_verification_evidence_cited", "ztl_engineering_evidence")
                 if b[k] and not a[k]]
        doc = {**artifact_header("python tools/baseline_compare.py", {}),
               "status": "PASS" if a["evaluator_verdict"] and b["evaluator_verdict"] else "Z",
               "same_task": "tests/runtime/cases.json HA and HB: identical prompt and inputs; B additionally receives "
                            "LEGION's engineering (02_engineering.json, 02_bom_handoff.json) and coalition "
                            "(06_commercial.json) artifacts",
               "ground_truth": {"source": "evidence/E2E/02_engineering.json", "cnc_parts": len(truth["cnc"]),
                                "cnc_instances_per_arm": sum(p["quantity"] for p in truth["cnc"]),
                                "bom_positions": f"{truth['bom']['mandatory_positions_matched']}/"
                                                 f"{truth['bom']['mandatory_positions']}",
                                "engineering_verdict": truth["engineering_verdict"]},
               "A_original": a, "B_legion": b, "metrics": metrics,
               "legion_added_capability_confirmed": added,
               "conclusion": ("LEGION adds a measured capability: " + ", ".join(added)) if added else
                             "No measured difference in outcome; no LEGION superiority is claimed.",
               "limits": "One task, one run per configuration (no repetition, so no variance estimate). Both runs use "
                         "the same model through the desktop-subagent route."}
    write_json(ROOT / "evidence" / "BASELINE_COMPARISON.json", doc)
    print(json.dumps({k: doc.get(k) for k in ("status", "legion_added_capability_confirmed", "conclusion")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
