"""WO-D02-A: write or verify manifests/ZTL_SOURCE_PINS.json (ZTL Engineer, ZTL Stand, ZTL) and the WO-D02 additions to
legion/engineering/DEAL_RESCUE_PIN.json.

  python -I tools/ztl_pins.py --freeze     # once, when a pin is chosen: lists + hashes every selected file
  python -I tools/ztl_pins.py --verify     # materialize into _deps/ and check every file (exit 1 on any mismatch)

Repositories are read, never written: blob-less sparse clones of the exact commits in .lmfg_cache/ (git-ignored).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from legion.engineering import pinned_source as P  # noqa: E402

REPOS = [
    {"name": "ztl-engineer", "repository": "https://github.com/inventor1975/ztl-engineer",
     "commit": "91d11672cb1986a7fb185d3ae5110d7209b36b97",
     "license": {"spdx": "Apache-2.0", "file": "LICENSE"},
     "role": "MCP server (stdio JSON-RPC); tool check_design runs `python -m ustand.stand <brick.json>`; "
             "ask_engineer (paid model API) is never called",
     "patterns": ["/mcp_server.py", "/ztl_engineer/", "/LICENSE", "/README.md"],
     "required_files": ["mcp_server.py", "ztl_engineer/runner.py", "ztl_engineer/session.py",
                        "ztl_engineer/report.py", "ztl_engineer/presets.py", "LICENSE"]},
    {"name": "ztl-stand", "repository": "https://github.com/inventor1975/ztl-stand",
     "commit": "0b4d718fa3bd3105ea002105e0d89cdd76b7b573",
     "license": {"spdx": "Apache-2.0 OR MIT", "file": ["LICENSE-APACHE", "LICENSE-MIT", "NOTICE"]},
     "role": "the stand (verdicts EARNED / REFUTED / OPEN) and its independent checker; its own tests and examples",
     "patterns": ["/ustand/", "/tests/", "/examples/", "/bench/", "/redteam/decks/", "/BRICKS.md", "/SPEC.md", "/README.md", "/LICENSE-APACHE",
                  "/LICENSE-MIT", "/NOTICE"],
     "required_files": ["BRICKS.md", "SPEC.md", "ustand/stand.py", "ustand/checker.py", "ustand/judge_ztl.py",
                        "ustand/bricks.py", "ustand/units.py", "tests/test_stand.py",
                        "examples/divider-1pct-req-1pct.json", "examples/divider-1pct-req-0.5pct.json",
                        "examples/tasks/t1-thermal-heatsink.json", "examples/tasks/t6-truss-three-bars.json",
                        "LICENSE-APACHE", "LICENSE-MIT", "NOTICE"]},
    {"name": "ZTL", "repository": "https://github.com/inventor1975/ZTL",
     "commit": "2ba7c209371e90058df4666bb949fc253fe6cc27",
     "license": {"spdx": "Apache-2.0 OR MIT", "file": ["LICENSE", "LICENSE-APACHE", "LICENSE-MIT",
                                                       "LICENSE-DUAL-NOTICE.txt", "NOTICE"]},
     "role": "the numeric judge the stand imports (ustand/judge_ztl.py: znumjudge, znumsolve) via USTAND_ZTL",
     "patterns": ["/*.py", "/LICENSE", "/LICENSE-*", "/NOTICE", "/JUDGE-API.md"],
     "required_files": ["znumsolve.py", "znumjudge.py", "LICENSE", "NOTICE"]},
]

# WO-LMFG-003 section 2.2: further Deal-Rescue paths at the same pinned commit (read-only, verified like the D01 files)
DEAL_RESCUE_ADDITIONS = ["deal_rescue/industrial/admission.py", "tests/test_cad025_ztl_gate.py",
                         "tests/judge_real_cad027.py", "docs/evidence/cad027/ZTL_REVIEW.json",
                         "docs/evidence/cad027/BOM_VERIFIED.json"]


def freeze() -> None:
    repos = []
    for spec in REPOS:
        files = P.freeze_repo(spec)
        repos.append({**spec, "files": files})
        print(spec["name"], len(files), "files")
    doc = {"schema": "legion.pinned-source.v1",
           "purpose": "WO-LMFG-003 (WO-D02): the real ZTL Engineer -> ZTL Stand -> checker route, reused from the "
                      "pinned commits without modification; materialized at test time into git-ignored _deps/",
           "reuse_mode": "blob-less sparse fetch of the pinned commit; every file verified by git blob SHA-1, size "
                         "and SHA-256 before use; never edited, never committed into this repository",
           "runtime": {"ZTL_ENGINEER_STAND": "_deps/ztl-stand (read by ztl_engineer/runner.py)",
                       "USTAND_ZTL": "_deps/ZTL (read by ustand/judge_ztl.py)",
                       "command": "python3 _deps/ztl-engineer/mcp_server.py (stdio); tools/call check_design"},
           "repositories": repos}
    P.ZTL_PINS.parent.mkdir(parents=True, exist_ok=True)
    P.ZTL_PINS.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")

    pin = P.load_pin()
    have = {f["path"] for f in pin["files"]}
    repo = P._source_repo(pin)
    for path in DEAL_RESCUE_ADDITIONS:
        if path in have:
            continue
        data = P._git(repo, "cat-file", "blob", f"{pin['commit']}:{path}")
        pin["files"].append({"path": path, "git_blob": P.git_blob_sha1(data),
                             "sha256": __import__("hashlib").sha256(data).hexdigest(), "bytes": len(data),
                             "added_by": "WO-LMFG-003"})
    P.PIN.write_text(json.dumps(pin, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def verify() -> dict:
    out = {"deal_rescue": P.materialize(), "ztl": P.materialize_all()}
    out["deal_rescue"] = {k: v for k, v in out["deal_rescue"].items() if k != "files"} | {
        "files": len(out["deal_rescue"]["files"])}
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    if a.freeze:
        freeze()
    print(json.dumps(verify(), indent=1))
