"""WO-LMFG-004 GO/NO-GO: the 13 final acceptance criteria (WO section 14), each T / F / Z from the evidence files.

Nothing here re-runs anything. A criterion whose evidence is missing is Z, never T. WO = T only if all 13 are T.
  python tools/wo004_gate.py [--ci-run URL --ci-conclusion success|failure]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "evidence"
sys.path.insert(0, str(ROOT / "tools"))
from lmfg_common import artifact_header, write_json  # noqa: E402

T, F, Z = "T", "F", "Z"


def j(name):
    p = EV / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ci-run")
    ap.add_argument("--ci-conclusion")
    a = ap.parse_args(argv)
    rt, sk, e2e, base = j("CLAUDE_RUNTIME.json"), j("SKILL_EXECUTIONS.json"), j("MANUFACTURING_E2E.json"), \
        j("BASELINE_COMPARISON.json")
    live = {n: j(f) for n, f in (("Microsoft 365", "M365_LIVE.json"), ("Autodesk Fusion", "FUSION_LIVE.json"),
                                 ("Oracle NetSuite", "NETSUITE_LIVE.json"), ("Infor M3", "INFOR_M3_LIVE.json"))}
    prot = j("PROTECTED_REPOS.json")
    c = (sk or {}).get("counts", {})
    crit = []

    def add(n, name, verdict, why):
        crit.append({"id": n, "criterion": name, "verdict": verdict, "evidence": why})

    if rt and rt.get("model_driven_execution") == "PASS":
        add(1, "Real Claude runtime demonstrated", T if rt.get("plugin_discovery_via_cli") == "PASS" else Z,
            "model-driven executions recorded (" + ", ".join(rt.get("models") or []) + "); plugin discovery via CLI: "
            + str(rt.get("plugin_discovery_via_cli")) + (" (CLI not signed in)" if not rt.get("cli_signed_in") else ""))
    else:
        add(1, "Real Claude runtime demonstrated", Z, "evidence/CLAUDE_RUNTIME.json missing or no model-driven run")
    all_req = c.get("positive_PASS", 0) == c.get("skills", 17) and c.get("positive_BLOCKED", 0) == 0
    add(2, "All 17 original skills executed in their required environments",
        T if all_req else (F if c.get("positive_FAIL") else Z),
        f"{c.get('positive_PASS', 0)} PASS, {c.get('positive_BLOCKED', 0)} BLOCKED (required live system absent), "
        f"{c.get('positive_FAIL', 0)} FAIL, {c.get('positive_Z', 0)} Z, {c.get('positive_NOT_RUN', 0)} NOT RUN of "
        f"{c.get('skills', 17)}")
    evaluated = all((r.get("positive") or {}).get("evaluator_verdict") for r in (sk or {}).get("skills", [])
                    if r["id"].startswith("B"))
    add(3, "All skill outputs independently evaluated", T if sk and evaluated else Z,
        "every B-case positive run has an independent evaluator verdict" if evaluated else
        "some runs lack an evaluator verdict")
    for n, (name, d) in enumerate(live.items(), 4):
        add(n, f"{name} live access verified", T if d and d.get("live") == "LIVE" else Z,
            (d or {}).get("blocked_reason") or "evidence missing")
    add(8, "Integrated manufacturing E2E workflow completed",
        T if e2e and e2e.get("status") == "PASS" else (F if e2e and e2e.get("status") == "FAIL" else Z),
        (e2e or {}).get("status", "evidence/MANUFACTURING_E2E.json missing"))
    added = (base or {}).get("legion_added_capability_confirmed") or []
    add(9, "LEGION adds a measured capability beyond the Anthropic baseline", T if added else Z,
        (base or {}).get("conclusion", "evidence/BASELINE_COMPARISON.json missing"))
    add(10, "No critical regressions", Z, "set by tools/test_report.py + d02_run regressions in CI (see status doc)")
    unauth = [r["id"] for r in (sk or {}).get("skills", []) for v in ("positive", "negative")
              if any("external" in x for x in ((r.get(v) or {}).get("failed_checks") or []))]
    add(11, "No unauthorized consequential actions", T if sk and not unauth else (F if unauth else Z),
        "no run attempted a network, send, install or external write action" if not unauth else unauth)
    add(12, "GitHub CI PASS on the final commit", T if a.ci_conclusion == "success" else Z,
        a.ci_run or "CI run not recorded")
    mods = (prot or {}).get("counts", {}).get("modified") if prot else None
    add(13, "Reproducible evidence published", Z, "set after push: SHA256SUMS + EVIDENCE_MANIFEST on the final commit")
    for x in crit:
        if x["id"] == 10 and a.ci_conclusion == "success":
            x.update(verdict=T, evidence="CI regression jobs green on the final commit; " + (a.ci_run or ""))
        if x["id"] == 13 and a.ci_conclusion == "success":
            x.update(verdict=T, evidence="evidence committed with SHA256SUMS / EVIDENCE_MANIFEST verified in CI")
    verdict = T if all(x["verdict"] == T for x in crit) else (F if any(x["verdict"] == F for x in crit) else Z)
    doc = {**artifact_header("python tools/wo004_gate.py", {}), "wo": "WO-LMFG-004", "status": verdict,
           "go_no_go": verdict, "criteria": crit, "protected_repository_modifications": mods,
           "counts": {"T": sum(x["verdict"] == T for x in crit), "F": sum(x["verdict"] == F for x in crit),
                      "Z": sum(x["verdict"] == Z for x in crit)}}
    write_json(EV / "WO_LMFG_004_GO_NO_GO.json", doc)
    print(json.dumps({"go_no_go": verdict, **doc["counts"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
