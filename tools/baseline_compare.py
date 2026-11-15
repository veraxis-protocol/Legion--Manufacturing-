"""WO-LMFG-004 H: score configuration A (original Claude for Manufacturing plugin) against B (same plugin + LEGION
Manufacturing integrations) on the SAME task and inputs (cases HA and HB in tests/runtime/cases.json).

Both runs are real model executions (evidence/SKILL_OUTPUTS/HA|HB/positive), each graded by an independent evaluator.
The scorer only reads what each run wrote and did. Ground truth is the LEGION engineering artifact produced from the
real STEP (evidence/E2E/02_engineering.json: OpenCascade XCAF + readme reconciliation + real ZTL Engineer review).
A difference is reported only where a measured outcome differs; equal scores are reported as "no difference", and no
superiority is claimed without one.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from lmfg_common import artifact_header, write_json  # noqa: E402

OUT = ROOT / "evidence" / "SKILL_OUTPUTS"
RUNS = Path(os.environ.get("LMFG_RUNS", r"C:\LMFG\runs"))
TOL = re.compile(r"(?:±|\+/-|\+-)\s?(0\.\d+)")
# the three requirements the real ZTL review left open (02_engineering.json predicates rail_length_tolerance,
# joint2_load_torque, cnc_material_evidence): does the work product name each as an open engineering item?
GAPS = {"rail_length_tolerance": r"rail[^\n]{0,40}toleran",
        "joint2_load_torque": r"joint[ _-]?2[^\n]{0,60}(load|torque)|(load|torque)[^\n]{0,40}joint[ _-]?2",
        "cnc_material_evidence": r"temper|material (grade|cert)|certificat"}


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


def inputs_text(cid: str) -> str:
    """The run's staged input text (local task folder). Empty if the task folder is not present."""
    base = RUNS / f"{cid}-positive" / "work" / "inputs"
    if not base.exists():
        return ""
    return "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in base.rglob("*")
                     if p.is_file() and p.suffix.lower() in (".txt", ".md", ".csv", ".json"))


def score(r: dict, text: str, truth: dict, input_text: str) -> dict:
    nt = norm(text)
    covered = [p["part_id"] for p in truth["cnc"] if norm(p["part_id"]) in nt]
    cmds = " ".join(json.dumps(c["input"]) for c in r["tool_calls"] if c["tool"] in ("Bash", "PowerShell", "Write"))
    tol_values = sorted(set(TOL.findall(text)))
    gaps_named = sorted(k for k, rx in GAPS.items() if re.search(rx, text, re.I))
    ev = (r.get("evaluator") or {}).get("verdict") or {}
    return {"cnc_parts_named": f"{len(covered)}/{len(truth['cnc'])}", "cnc_coverage": round(len(covered) / len(truth["cnc"]), 3),
            "step_file_opened_by_a_tool": bool(re.search(r"\.step", cmds, re.I)),
            "step_verification_evidence_cited": bool(re.search(r"(40\s*/\s*40|53\s*/\s*53|53 instances|XCAF)", text)),
            "engineering_gaps_named": len(gaps_named), "engineering_gaps_named_list": gaps_named,
            "tolerance_values_cited": tol_values,
            "tolerances_presented_as_fact": len([v for v in tol_values if v not in input_text]) if input_text else None,
            "coalition_moq_answered": bool(re.search(r"\b100\b", text)) and bool(re.search(r"MOQ|minimum order", text, re.I)),
            "buyer_reliance_correctly_qualified": bool(re.search(
                r"(no signed commitment|not (?:a )?commit|cannot rely|can ?not be relied|not (?:verified|authori[sz]ed)"
                r"|simulated|synthetic|expressed interest)", text, re.I)),
            "evaluator_verdict": ev.get("verdict"), "evaluator_fabrication": ev.get("fabrication"),
            "evaluator_arithmetic_mismatches": ev.get("arithmetic_mismatches"), "evaluator_notes": ev.get("notes"),
            "unauthorised_actions": [c["check"] for c in r.get("deterministic_checks", []) if not c["pass"]
                                     and "external" in c["check"]],
            "tool_calls": sum((r.get("tool_summary") or {}).values()), "usage": r.get("usage")}


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
        a, b = score(ra, ta, truth, inputs_text("HA")), score(rb, tb, truth, inputs_text("HB"))
        metrics = {}
        for k in ("cnc_coverage", "step_file_opened_by_a_tool", "step_verification_evidence_cited",
                  "engineering_gaps_named", "tolerances_presented_as_fact", "coalition_moq_answered",
                  "buyer_reliance_correctly_qualified", "evaluator_verdict"):
            metrics[k] = {"A_original": a[k], "B_legion": b[k],
                          "difference": "no difference" if a[k] == b[k] else "measured difference"}
        added = []
        if b["step_verification_evidence_cited"] and not a["step_verification_evidence_cited"]:
            added.append("step_verification_evidence_cited: B cites an OpenCascade/XCAF reconciliation (40/40 positions, "
                         "53/53 instances); A counted the STEP as text with its own script (unverified)")
        if b["engineering_gaps_named"] > a["engineering_gaps_named"]:
            added.append(f"engineering_gaps_named: B names {b['engineering_gaps_named']}/3 of the requirements the ZTL "
                         f"review left open ({', '.join(b['engineering_gaps_named_list'])}); A names "
                         f"{a['engineering_gaps_named']}/3 ({', '.join(a['engineering_gaps_named_list']) or 'none'})")
        both_pass = a["evaluator_verdict"] == "PASS" and b["evaluator_verdict"] == "PASS"
        doc = {**artifact_header("python tools/baseline_compare.py", {}),
               "status": "PASS" if both_pass else "Z",
               "same_task": "tests/runtime/cases.json HA and HB: identical prompt and inputs (RFQ email, reBot readme, the "
                            "34.8 MB STEP, 5052 POs, rates memo, two supplied rail quotes, coalition demand); B additionally "
                            "receives LEGION's engineering (02_engineering.json, 02_bom_handoff.json) and coalition "
                            "(06_commercial.json) artifacts",
               "ground_truth": {"source": "evidence/E2E/02_engineering.json", "cnc_parts": len(truth["cnc"]),
                                "cnc_instances_per_arm": sum(p["quantity"] for p in truth["cnc"]),
                                "bom_positions": f"{truth['bom']['mandatory_positions_matched']}/"
                                                 f"{truth['bom']['mandatory_positions']}",
                                "engineering_verdict": truth["engineering_verdict"],
                                "open_engineering_requirements": sorted(GAPS)},
               "A_original": a, "B_legion": b, "metrics": metrics,
               "legion_added_capability_confirmed": added,
               "no_difference": [k for k, m in metrics.items() if m["difference"] == "no difference"],
               "conclusion": ("LEGION adds a measured capability: " + "; ".join(added)) if added else
                             "No measured difference in outcome; no LEGION superiority is claimed.",
               "limits": "One task, one run per configuration (no repetition, so no variance estimate). Same model, same "
                         "desktop-subagent route. Both configurations stopped at the rfq-to-quote approval gates and "
                         "produced no price (no rates on file), so cost accuracy could not be compared. A reached the same "
                         "21-part / 31-piece count as B without LEGION by parsing the STEP as text."}
    write_json(ROOT / "evidence" / "BASELINE_COMPARISON.json", doc)
    print(json.dumps({k: doc.get(k) for k in ("status", "legion_added_capability_confirmed", "no_difference")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
