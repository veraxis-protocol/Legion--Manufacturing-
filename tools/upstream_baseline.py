"""Reproduce the executable baseline of the imported Claude for Manufacturing plugin (WO-A03).

  python3 -I tools/upstream_baseline.py [--evidence evidence/UPSTREAM_BASELINE.json]

Runs on a temporary COPY of upstream/claude-for-manufacturing, so the imported baseline is never written to.
Discovers every executable entrypoint (Python files, declared MCP servers), then runs what can run locally:
  - byte-compile of every Python entrypoint
  - --help of every Python entrypoint with an argparse main
  - plant_setup.py --selftest (the upstream self-test)
  - pulse_compute.py on a LEGION-authored SYNTHETIC export fixture (upstream ships no fixtures), then
    render_short.py on its output; input and output files are hashed
Each skill is classified from what actually ran. Skills are Markdown instructions executed by Claude; they are
AVAILABLE when present and intact, and their live, model-driven run is BLOCKED in this environment (it needs the
Claude runtime and the plant's connected systems). Any non-zero exit or traceback is FAIL, never PASS.
Exit status: 0 when no check failed, 1 otherwise.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lmfg_common import ROOT, UPSTREAM_DIR, artifact_header, sha256_file, write_json  # noqa: E402

FIXTURE = ROOT / "tests" / "upstream" / "fixtures" / "pulse_minimal"
CONNECTOR_NAMES = ("Autodesk Fusion", "NetSuite", "Infor M3", "Microsoft 365", "Outlook", "SharePoint")
TIMEOUT = 300


def run(cmd, cwd, env=None):
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=TIMEOUT)
    out = (p.stdout or "") + (p.stderr or "")
    return {"command": " ".join(str(c) for c in cmd), "exit_code": p.returncode,
            "traceback": "Traceback (most recent call last)" in out, "output_tail": out[-2500:]}


def status_of(r):
    return "PASS" if r["exit_code"] == 0 and not r["traceback"] else "FAIL"


def hash_dir(d: pathlib.Path):
    return {str(p.relative_to(d)).replace("\\", "/"): sha256_file(p) for p in sorted(d.rglob("*")) if p.is_file()}


def discover(root: pathlib.Path):
    eps = []
    for py in sorted(root.rglob("*.py")):
        text = py.read_text(encoding="utf-8")
        eps.append({"path": str(py.relative_to(root)).replace("\\", "/"), "kind": "python",
                    "has_main": "__main__" in text, "argparse": "argparse" in text,
                    "selftest": "--selftest" in text})
    mcp = root / ".mcp.json"
    if mcp.exists():
        import json
        for name, cfg in json.loads(mcp.read_text(encoding="utf-8")).get("mcpServers", {}).items():
            eps.append({"path": ".mcp.json#" + name, "kind": "mcp_server", "transport": cfg.get("type"), "url": cfg.get("url")})
    return eps


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--evidence")
    a = ap.parse_args(argv)
    py = sys.executable
    checks = []
    with tempfile.TemporaryDirectory(prefix="lmfg-upstream-") as td:
        work = pathlib.Path(td) / "claude-for-manufacturing"
        shutil.copytree(UPSTREAM_DIR, work)
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_DATA"}
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        eps = discover(work)
        for ep in [e for e in eps if e["kind"] == "python"]:
            r = run([py, "-I", "-c", "import py_compile,sys; py_compile.compile(sys.argv[1], cfile=sys.argv[2], doraise=True)",
                     ep["path"], str(pathlib.Path(td) / "compiled.pyc")], work, env)
            checks.append({"id": "compile:" + ep["path"], "status": status_of(r), **r})
            if ep["has_main"] and ep["argparse"]:
                r = run([py, "-I", ep["path"], "--help"], work, env)
                checks.append({"id": "help:" + ep["path"], "status": status_of(r), **r})
        r = run([py, "-I", "shared/scripts/plant_setup.py", "--selftest"], work, env)
        st = status_of(r)
        note = None
        if st == "FAIL" and os.name == "nt" and 'endswith("plant-setup/open-work/open-work.md")' in r["output_tail"]:
            note = ("UPSTREAM_DEFECT (Windows only): _work_selftest asserts a POSIX '/' separator in work_path at "
                    "plant_setup.py line 1113; Windows returns '\\'. install() itself succeeded (changed=True, 2 files).")
        checks.append({"id": "selftest:shared/scripts/plant_setup.py", "status": st, "upstream_defect": note, **r})
        out = pathlib.Path(td) / "pulse-output"
        fx = {"fixture": "tests/upstream/fixtures/pulse_minimal", "label": "LEGION-authored SYNTHETIC, not plant data",
              "files": hash_dir(FIXTURE)}
        r = run([py, "-I", "skills/morning-plant-pulse/scripts/pulse_compute.py", "--exports", str(FIXTURE), "--out", str(out),
                 "--day", "2026-11-12", "--run-time", "2026-11-13T06:00:00", "--tz", "UTC"], work, env)
        m = re.search(r"self-checks: (\d+) run, (\d+) failed", r["output_tail"])
        selfchk = {"run": int(m.group(1)), "failed": int(m.group(2))} if m else None
        st = status_of(r) if selfchk and selfchk["failed"] == 0 else "FAIL"
        checks.append({"id": "run:skills/morning-plant-pulse/scripts/pulse_compute.py", "status": st, "self_checks": selfchk,
                       "input": fx, "outputs": hash_dir(out) if out.exists() else {}, **r})
        r = run([py, "-I", "skills/morning-plant-pulse/scripts/render_short.py", "--out", str(out), "--day", "2026-11-12"], work, env)
        st = status_of(r) if "checks passed" in r["output_tail"] else "FAIL"
        checks.append({"id": "run:skills/morning-plant-pulse/scripts/render_short.py", "status": st,
                       "outputs": hash_dir(out) if out.exists() else {}, **r})
        # The copy must still equal the import: no entrypoint wrote into the plugin tree.
        before, after = hash_dir(UPSTREAM_DIR), hash_dir(work)
        checks.append({"id": "integrity:no-writes-into-plugin-tree", "status": "PASS" if before == after else "FAIL",
                       "changed": sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k)),
                       "command": "compare sha256 of the working copy with upstream/ after all runs", "exit_code": 0, "traceback": False, "output_tail": ""})

    by_id = {c["id"]: c for c in checks}
    skills = []
    for sd in sorted((UPSTREAM_DIR / "skills").iterdir()):
        if not sd.is_dir():
            continue
        text = "\n".join(p.read_text(encoding="utf-8") for p in sd.rglob("*.md"))
        scripts = sorted(str(p.relative_to(UPSTREAM_DIR)).replace("\\", "/") for p in sd.rglob("*.py"))
        script_checks = [c for c in checks if any(c["id"].endswith(s) for s in scripts)]
        tested = bool([c for c in script_checks if c["id"].startswith("run:")])
        uses_setup = "plant_setup.py" in text
        row = {"skill": sd.name, "AVAILABLE": (sd / "SKILL.md").is_file(), "EXECUTABLE": bool(scripts), "local_scripts": scripts,
               "CONFIGURED": False, "TESTED": tested,
               "uses_shared_plant_setup": uses_setup,
               "connectors_named": sorted({n for n in CONNECTOR_NAMES if n.lower() in text.lower()}),
               "script_status": ("PASS" if script_checks and all(c["status"] == "PASS" for c in script_checks) else
                                 "FAIL" if script_checks else "N/A (no local code)"),
               "live_model_driven_run": "BLOCKED",
               "blocked_reason": "skill is Markdown instructions executed by Claude with the plant's systems; no Claude runtime, "
                                 "plant profile or authorized connector in this environment"}
        if uses_setup:
            row["shared_dependency"] = {"plant_setup.py --selftest": by_id["selftest:shared/scripts/plant_setup.py"]["status"]}
        skills.append(row)

    counts = {s: sum(1 for c in checks if c["status"] == s) for s in ("PASS", "FAIL", "BLOCKED")}
    blocked = [{"entrypoint": e["path"], "status": "BLOCKED", "reason": "MCP server at " + str(e.get("url")) +
                " requires a running Autodesk Fusion desktop with its MCP add-in; not available here"}
               for e in eps if e["kind"] == "mcp_server"]
    counts["BLOCKED"] += len(blocked)
    res = artifact_header("python3 -I tools/upstream_baseline.py" + (" --evidence " + a.evidence if a.evidence else ""),
                          {"upstream": "upstream/claude-for-manufacturing (manifests/UPSTREAM_MANIFEST.json)", "fixture": fx})
    res.update({"schema": "legion.manufacturing.evidence.upstream-baseline.v1", "work_order": "WO-A03",
                "status": "PASS" if counts["FAIL"] == 0 else "FAIL",
                "counts": counts, "entrypoints": eps, "checks": checks, "blocked_entrypoints": blocked, "skills": skills})
    if a.evidence:
        write_json(ROOT / a.evidence, res)
    print(f"{res['status']}: {counts} | skills {len(skills)}")
    for c in checks:
        print(f"  {c['status']:5} {c['id']}" + (f"  [{c['upstream_defect']}]" if c.get("upstream_defect") else ""))
    for b in blocked:
        print(f"  BLOCKED {b['entrypoint']}")
    return 0 if counts["FAIL"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
