"""Materialize the pinned LEGION-Deal-Rescue CAD files and the pinned reBot reference CAD, verified, into _deps/.

Deal-Rescue is read, never written: files are taken from its git objects at the pinned commit
(`git cat-file blob <commit>:<path>`), from an existing clone when LMFG_DEAL_RESCUE_GIT points at one, else from a
blob-less fetch of exactly that commit. Each file must match the pin's git blob SHA-1, size and SHA-256 before it is
written; a mismatch stops everything (SourceMismatch), it is never used.

The reBot STEP and readme are downloaded from the pinned commit's raw URL and checked against size and SHA-256 the
same way (they are CERN-OHL-W-2.0 and are not redistributed: _deps/ and .lmfg_cache/ are git-ignored).
"""
from __future__ import annotations

import fnmatch
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


# ---------------------------------------------------------------- WO-D02: other pinned repositories (ZTL)
# Same rule as above, for any repository listed in a pin manifest (manifests/ZTL_SOURCE_PINS.json): a blob-less,
# sparse clone of exactly the pinned commit in .lmfg_cache/<name>, every file read from git objects at that commit and
# checked against git blob SHA-1, size and SHA-256 before it is written to _deps/<name>. Nothing is ever written back.

ZTL_PINS = ROOT / "manifests" / "ZTL_SOURCE_PINS.json"


def load_manifest(path: Path = ZTL_PINS) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sparse_clone(name: str, url: str, commit: str, patterns: list, cache: Path = CACHE) -> Path:
    repo = cache / name
    if not (repo / ".git").exists():
        repo.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
    g = ["git", "-c", "core.autocrlf=false", "-C", str(repo)]
    have = subprocess.run(g + ["cat-file", "-e", commit + "^{commit}"], capture_output=True).returncode == 0
    if not have:
        subprocess.run(g + ["fetch", "-q", "--depth", "1", "--filter=blob:none", url, commit], check=True)
    # the sparse checkout batches the blob download for exactly the pinned paths
    subprocess.run(g + ["sparse-checkout", "set", "--no-cone", *patterns], check=True)
    subprocess.run(g + ["checkout", "-q", "--detach", commit], check=True)
    return repo


def _match(path: str, patterns: list) -> bool:
    """git sparse (no-cone) semantics for the forms used in the manifest: 'dir/' = everything under dir;
    otherwise a glob anchored at the root that never crosses a '/' (so '/*.py' is top-level only)."""
    for p in patterns:
        p = p.lstrip("/")
        if p.endswith("/"):
            if path.startswith(p):
                return True
        elif path.count("/") == p.count("/") and fnmatch.fnmatchcase(path, p):
            return True
    return False


def freeze_repo(spec: dict, cache: Path = CACHE) -> list:
    """List and hash every file of the pinned commit that the spec's patterns select (used once, to write the pin)."""
    repo = _sparse_clone(spec["name"], spec["repository"], spec["commit"], spec["patterns"], cache)
    names = _git(repo, "ls-tree", "-r", "--name-only", spec["commit"]).decode("utf-8").splitlines()
    out = []
    for path in sorted(n for n in names if _match(n, spec["patterns"])):
        data = _git(repo, "cat-file", "blob", f"{spec['commit']}:{path}")
        out.append({"path": path, "git_blob": git_blob_sha1(data), "sha256": hashlib.sha256(data).hexdigest(),
                    "bytes": len(data)})
    return out


def _cat_batch(repo: Path, commit: str, paths: list) -> dict:
    """All blobs `<commit>:<path>` through one `git cat-file --batch` process (one subprocess, not one per file)."""
    req = "".join(f"{commit}:{p}\n" for p in paths).encode("utf-8")
    raw = subprocess.run(["git", "-C", str(repo), "cat-file", "--batch"], input=req, capture_output=True,
                         check=True).stdout
    out, i = {}, 0
    for p in paths:
        nl = raw.index(b"\n", i)
        head = raw[i:nl].split()
        if len(head) != 3 or head[1] != b"blob":
            raise SourceMismatch(f"{p}: not a blob at {commit} ({raw[i:nl][:120]!r})")
        size = int(head[2])
        out[p] = raw[nl + 1:nl + 1 + size]
        i = nl + 1 + size + 1
    return out


def materialize_repo(spec: dict, deps_root: Path = ROOT / "_deps", cache: Path | None = None) -> dict:
    """_deps/<name> is a sparse checkout of exactly the pinned commit (a real git checkout, so tools that ask git for
    their own version, e.g. ustand/judge_ztl.ztl_commit, report the pinned commit and not this repository's HEAD).
    Every pinned file is checked twice: the git object at the commit and the bytes on disk, each against git blob
    SHA-1, size and SHA-256. Any difference stops everything."""
    dest = deps_root / spec["name"]
    if dest.exists() and not (dest / ".git").exists():
        shutil.rmtree(dest)                          # an older plain copy: replace it by the checkout
    repo = _sparse_clone(spec["name"], spec["repository"], spec["commit"], spec["patterns"], deps_root)
    subprocess.run(["git", "-c", "core.autocrlf=false", "-C", str(repo), "checkout", "-q", "-f", "--detach",
                    spec["commit"]], check=True)
    head = _git(repo, "rev-parse", "HEAD").decode().strip()
    if head != spec["commit"]:
        raise SourceMismatch(f"{spec['name']}: checkout is at {head}, pin is {spec['commit']}")
    # paths that differ only by letter case cannot both exist on a case-insensitive file system (Windows, macOS):
    # their git objects are still verified; on disk they are reported, never counted as verified
    folded: dict = {}
    for f in spec["files"]:
        folded.setdefault(f["path"].lower(), []).append(f["path"])
    case_insensitive = os.name == "nt" or sys.platform == "darwin"
    clash = {p for v in folded.values() if len(v) > 1 for p in v} if case_insensitive else set()
    objects = _cat_batch(repo, spec["commit"], [f["path"] for f in spec["files"]])
    for f in spec["files"]:
        data = objects[f["path"]]
        disk = (dest / f["path"]).read_bytes() if (dest / f["path"]).is_file() else b""
        checks = (("git object", data),) if f["path"] in clash else (("git object", data), ("checked-out file", disk))
        for label, blob in checks:
            got = {"git_blob": git_blob_sha1(blob), "sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)}
            for k in ("git_blob", "sha256", "bytes"):
                if got[k] != f[k]:
                    raise SourceMismatch(f"{spec['name']}:{f['path']} ({label}): {k} expected {f[k]} got {got[k]}")
    paths = {f["path"] for f in spec["files"]}
    missing = [r for r in spec["required_files"] if r not in paths]
    if missing:
        raise SourceMismatch(f"{spec['name']}: required files not in the pin: {missing}")
    return {"name": spec["name"], "repository": spec["repository"], "commit": spec["commit"], "head": head,
            "dest": str(dest), "files": len(spec["files"]), "required_files": len(spec["required_files"]),
            "verified": True, "license": spec["license"]["spdx"],
            "not_representable_on_this_file_system": sorted(clash)}


def verify_tree(spec: dict, deps_root: Path = ROOT / "_deps") -> list:
    """Re-hash the materialized copy; return the files that no longer match the pin (empty = unchanged)."""
    bad = []
    folded: dict = {}
    for f in spec["files"]:
        folded.setdefault(f["path"].lower(), []).append(f["path"])
    clash = {p for v in folded.values() if len(v) > 1 for p in v} if os.name == "nt" else set()
    for f in spec["files"]:
        if f["path"] in clash:
            continue
        p = deps_root / spec["name"] / f["path"]
        if not p.is_file() or sha256_file(p) != f["sha256"]:
            bad.append(f["path"])
    return bad


def materialize_all(manifest: dict | None = None, deps_root: Path = ROOT / "_deps") -> dict:
    manifest = manifest or load_manifest()
    return {r["name"]: materialize_repo(r, deps_root) for r in manifest["repositories"]}


if __name__ == "__main__":
    print(json.dumps(materialize(), indent=1))
