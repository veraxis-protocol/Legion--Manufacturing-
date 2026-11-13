"""Materialize the pinned LEGION-Deal-Rescue CAD files and the pinned reBot reference CAD, verified, into _deps/.

Deal-Rescue is read, never written: files are taken from its git objects at the pinned commit
(`git cat-file blob <commit>:<path>`), from an existing clone when LMFG_DEAL_RESCUE_GIT points at one, else from a
blob-less fetch of exactly that commit. Each file must match the pin's git blob SHA-1, size and SHA-256 before it is
written; a mismatch stops everything (SourceMismatch), it is never used.

The reBot STEP and readme are downloaded from the pinned commit's raw URL and checked against size and SHA-256 the
same way (they are CERN-OHL-W-2.0 and are not redistributed: _deps/ and .lmfg_cache/ are git-ignored).
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PIN = ROOT / "legion" / "engineering" / "DEAL_RESCUE_PIN.json"
DEPS = ROOT / "_deps" / "deal-rescue"
CACHE = ROOT / ".lmfg_cache"


class SourceMismatch(RuntimeError):
    pass


def load_pin() -> dict:
    return json.loads(PIN.read_text(encoding="utf-8"))


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _git(repo: Path, *args) -> bytes:
    return subprocess.run(["git", "-c", "core.autocrlf=false", "-C", str(repo), *args], check=True,
                          capture_output=True).stdout


def _source_repo(pin) -> Path:
    local = os.environ.get("LMFG_DEAL_RESCUE_GIT")
    if local and Path(local, ".git").exists():
        return Path(local)
    repo = CACHE / "deal-rescue.git"
    if not (repo / "HEAD").exists():
        repo.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init", "--bare", "-q", str(repo)], check=True)
    have = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", pin["commit"] + "^{commit}"],
                          capture_output=True).returncode == 0
    if not have:
        subprocess.run(["git", "-C", str(repo), "fetch", "-q", "--depth", "1", "--filter=blob:none",
                        pin["repository"], pin["commit"]], check=True)
    return repo


def materialize(dest: Path = DEPS) -> dict:
    pin = load_pin()
    repo = _source_repo(pin)
    if dest.exists():
        shutil.rmtree(dest)
    out = []
    for f in pin["files"]:
        data = _git(repo, "cat-file", "blob", f"{pin['commit']}:{f['path']}")
        got = {"git_blob": git_blob_sha1(data), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
        for k in ("git_blob", "sha256", "bytes"):
            if got[k] != f[k]:
                raise SourceMismatch(f"{f['path']}: {k} expected {f[k]} got {got[k]}")
        p = dest / f["path"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        out.append({"path": f["path"], **got, "verified": True})
    return {"repository": pin["repository"], "commit": pin["commit"], "dest": str(dest), "files": out,
            "license": pin["license"]["spdx"]}


def import_path(dest: Path = DEPS) -> Path:
    """Put the verified copy first on sys.path (and nothing else from Deal-Rescue)."""
    if str(dest) not in sys.path:
        sys.path.insert(0, str(dest))
    return dest


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        while block := fp.read(1 << 20):
            h.update(block)
    return h.hexdigest()


def fetch_reference_cad(cache: Path = CACHE / "rebot") -> dict:
    ref = load_pin()["reference_cad"]
    cache = cache / ref["commit"]
    cache.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, spec in ref["files"].items():
        dest = cache / Path(spec["path"]).name
        ok = dest.is_file() and dest.stat().st_size == spec["bytes"] and sha256_file(dest) == spec["sha256"]
        if not ok:
            dest.unlink(missing_ok=True)
            url = ref["raw_url"].format(commit=ref["commit"], path=spec["path"])
            tmp = dest.with_suffix(dest.suffix + ".part")
            req = urllib.request.Request(url, headers={"User-Agent": "legion-manufacturing-ci"})
            with urllib.request.urlopen(req, timeout=180) as r, open(tmp, "wb") as fp:
                shutil.copyfileobj(r, fp, 1 << 20)
            if tmp.stat().st_size != spec["bytes"] or sha256_file(tmp) != spec["sha256"]:
                bad = sha256_file(tmp)
                tmp.unlink()
                raise SourceMismatch(f"{name}: downloaded file does not match the pin (sha256 {bad})")
            tmp.replace(dest)
        out[name] = {"path": str(dest), "sha256": spec["sha256"], "bytes": spec["bytes"], "cached": ok,
                     "source": ref["raw_url"].format(commit=ref["commit"], path=spec["path"])}
    return out


if __name__ == "__main__":
    print(json.dumps(materialize(), indent=1))
