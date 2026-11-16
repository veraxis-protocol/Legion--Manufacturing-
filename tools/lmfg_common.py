"""Shared helpers for LEGION Manufacturing tooling. Standard library only."""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import pathlib
import platform
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
UPSTREAM_DIR = ROOT / "upstream" / "claude-for-manufacturing"
MANIFEST_PATH = ROOT / "manifests" / "UPSTREAM_MANIFEST.json"
EVIDENCE_DIR = ROOT / "evidence"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: pathlib.Path) -> str:
    return sha256_bytes(p.read_bytes())


def git_blob_sha1(b: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def load_json(p: pathlib.Path):
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(p: pathlib.Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=False) + "\n", encoding="utf-8", newline="\n")


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def source_commit() -> str | None:
    """Commit of this repository being tested (GITHUB_SHA in CI, else git rev-parse)."""
    if os.environ.get("GITHUB_SHA"):
        return os.environ["GITHUB_SHA"]
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return None


def environment() -> dict:
    return {
        "python": sys.version.split()[0],
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "os_name": os.name,
        "ci": bool(os.environ.get("CI")),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_workflow": os.environ.get("GITHUB_WORKFLOW"),
        "github_job": os.environ.get("GITHUB_JOB"),
    }


def artifact_header(command: str, inputs: dict) -> dict:
    """Fields every evidence artifact carries (WO-LMFG-001 section 13)."""
    return {
        "source_commit": source_commit(),
        "executed_at_utc": utc_now(),
        "environment": environment(),
        "command": command,
        "inputs": inputs,
    }
