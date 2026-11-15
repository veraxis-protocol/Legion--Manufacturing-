"""WO-LMFG-004: collect evidence/SKILL_OUTPUTS/*/*/run.json into evidence/SKILL_EXECUTIONS.json and CLAUDE_RUNTIME.json.

Model-driven executions are reported separately from the deterministic unit/contract tests (tools/test_report.py);
nothing here re-runs or re-judges a skill. A case with no run.json is NOT RUN.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from lmfg_common import artifact_header, write_json  # noqa: E402

OUT = ROOT / "evidence" / "SKILL_OUTPUTS"


def load(case: str, variant: str):
    p = OUT / case / variant / "run.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cli-status", help="JSON from `python tools/skill_run.py --status`")
    a = ap.parse_args(argv)
    cases = json.loads((ROOT / "tests" / "runtime" / "cases.json").read_text(encoding="utf-8"))["cases"]
    cli_runs = []
    rows, models, routes, tokens = [], set(), set(), {"input_tokens": 0, "output_tokens": 0,
                                                      "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
    for c in cases:
        row = {"id": c["id"], "skill": c["skill"], "chain": c.get("chain", []), "e2e_stage": c.get("e2e_stage")}
        for variant in ("positive", "negative"):
            if variant not in c:
                continue
            r = load(c["id"], variant)
            if r is None:
                row[variant] = {"status": "NOT RUN"}
                continue
            rt = r.get("runtime") or {}
            models.add(rt.get("model"))
            routes.add(rt.get("runtime_route", "cli"))
            for k in tokens:
                tokens[k] += ((r.get("usage") or (r.get("result") or {}).get("usage") or {}).get(k) or 0)
            ev = (r.get("evaluator") or {}).get("verdict") or {}
            row[variant] = {
                "status": r["status"], "reason": r.get("blocked_reason") or r.get("z_reason"),
                "behaviour_without_live_system": r.get("behaviour_without_live_system"),
                "runtime_route": rt.get("runtime_route", "cli"), "model": rt.get("model"),
                "skills_read_or_invoked": r.get("skills_invoked"), "tool_summary": r.get("tool_summary"),
                "duration_s": r.get("duration_s"), "outputs": [o["path"] for o in r.get("outputs", [])],
                "deterministic_checks": f"{sum(x['pass'] for x in r.get('deterministic_checks', []))}/"
                                        f"{len(r.get('deterministic_checks', []))}",
                "failed_checks": [x["check"] for x in r.get("deterministic_checks", []) if not x["pass"]],
                "evaluator_verdict": ev.get("verdict"), "evaluator_fabrication": ev.get("fabrication"),
                "evaluator_arithmetic_mismatches": ev.get("arithmetic_mismatches"), "evaluator_notes": ev.get("notes"),
                "run_record": f"evidence/SKILL_OUTPUTS/{c['id']}/{variant}/run.json"}
        for variant in ("positive", "negative"):
            r = load(c["id"], f"cli-{variant}")
            if r is None:
                continue
            ev = (r.get("evaluator") or {}).get("verdict") or {}
            cli_runs.append({
                "case": c["id"], "variant": variant, "status": r["status"],
                "reason": r.get("blocked_reason") or r.get("z_reason"), "model": (r.get("runtime") or {}).get("model"),
                "claude_code_version": (r.get("runtime") or {}).get("claude_code_version"),
                "manufacturing_skills_discovered": (r.get("plugin_discovery") or {}).get("manufacturing_skills_listed"),
                "skill_tool_invocations": r.get("skills_invoked"),
                "deterministic_checks": f"{sum(x['pass'] for x in r.get('deterministic_checks', []))}/"
                                        f"{len(r.get('deterministic_checks', []))}",
                "failed_checks": [x["check"] for x in r.get("deterministic_checks", []) if not x["pass"]],
                "evaluator_verdict": ev.get("verdict"), "evaluator_fabrication": ev.get("fabrication"),
                "evaluator_notes": ev.get("notes"), "duration_s": r.get("duration_s"),
                "usage": (r.get("result") or {}).get("usage"),
                "run_record": f"evidence/SKILL_OUTPUTS/{c['id']}/cli-{variant}/run.json"})
        rows.append(row)
    skills = [r for r in rows if r["id"].startswith("B")]

    def count(variant, status):
        return sum(1 for r in skills if r.get(variant, {}).get("status") == status)
    executed = sum(1 for r in skills if r.get("positive", {}).get("status") not in (None, "NOT RUN"))
    counts = {"skills": len(skills), "executed": executed,
              "positive_PASS": count("positive", "PASS"), "positive_FAIL": count("positive", "FAIL"),
              "positive_BLOCKED": count("positive", "BLOCKED"), "positive_Z": count("positive", "Z"),
              "positive_NOT_RUN": count("positive", "NOT RUN"),
              "negative_PASS": count("negative", "PASS"), "negative_FAIL": count("negative", "FAIL"),
              "negative_Z": count("negative", "Z"), "negative_NOT_RUN": count("negative", "NOT RUN"),
              "e2e_stages_PASS": sum(1 for r in rows if r["id"].startswith("E") and r["positive"].get("status") == "PASS")}
    cli = json.loads(Path(a.cli_status).read_text(encoding="utf-8")) if a.cli_status else None
    status = "PASS" if counts["positive_PASS"] + counts["positive_BLOCKED"] == len(skills) and \
        counts["positive_FAIL"] == 0 and counts["negative_FAIL"] == 0 else ("FAIL" if counts["positive_FAIL"] or
                                                                             counts["negative_FAIL"] else "Z")
    doc = {**artifact_header("python tools/skill_report.py", {}), "status": status, "counts": counts,
           "runtime_routes": sorted(routes), "models": sorted(m for m in models if m), "tokens_total": tokens,
           "note": "Model-driven executions only. Deterministic contract/unit tests are reported separately "
                   "(evidence/SKILL_MATRIX*.json) and are not counted here.",
           "skills": rows}
    write_json(ROOT / "evidence" / "SKILL_EXECUTIONS.json", doc)
    # plugin discovery via the CLI is PASS only for a CLI run that listed all 17 skills from --plugin-dir, entered its
    # skill through the Skill tool and passed (deterministic checks + independent evaluator)
    discovery = "PASS" if any(x["status"] in ("PASS", "BLOCKED") and x["evaluator_verdict"] == "PASS"
                              and x["manufacturing_skills_discovered"] == 17 and x["skill_tool_invocations"]
                              for x in cli_runs) else ("FAIL" if any(x["status"] == "FAIL" for x in cli_runs)
                                                       else "BLOCKED")
    runtime = {**artifact_header("python tools/skill_report.py", {}),
               "cli": cli, "cli_signed_in": bool(cli and (cli.get("auth") or {}).get("loggedIn")),
               "routes_used": sorted(routes), "models": sorted(m for m in models if m),
               "plugin_discovery_via_cli": discovery,
               "cli_runs": cli_runs,
               "model_driven_execution": "PASS" if executed else "NOT RUN",
               "status": "PASS" if executed and discovery == "PASS" else ("PARTIAL" if executed else "BLOCKED"),
               "explanation": ("Skills ran through subagents of the signed-in Claude Code desktop session (real model, "
                               "real tool calls, transcripts in evidence/SKILL_OUTPUTS/*/*/transcript.jsonl.gz). The "
                               "plugin was loaded by path: each run read the original SKILL.md from a byte-identical "
                               "copy of upstream/claude-for-manufacturing. Plugin discovery through `claude -p "
                               "--plugin-dir` (tools/skill_run.py route 1) is reported in cli_runs: each such run used the "
                               "standalone CLI with its own sign-in (host-session variables removed), discovered the plugin "
                               "and entered the skill through the Skill tool."
                               if "desktop-subagent" in routes else None)}
    write_json(ROOT / "evidence" / "CLAUDE_RUNTIME.json", runtime)
    print(json.dumps(counts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
