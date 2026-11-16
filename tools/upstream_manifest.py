"""Generate or verify the manifest of the imported Claude for Manufacturing baseline (WO-A02, INV-01).

  python3 -I tools/upstream_manifest.py generate --from-git <anthropic clone>   # once, at import time
  python3 -I tools/upstream_manifest.py verify [--evidence evidence/SOURCE_MANIFEST.json]

`generate` reads the upstream git tree at the pinned revision (path, mode, git blob, size) and the imported bytes
(sha256), and refuses to write a manifest if any imported file differs from its upstream blob.
`verify` needs no network: it recomputes git-blob SHA-1 and SHA-256 for every file under upstream/, checks the set
of files is exactly the manifest's, that 17 skill directories exist, and that local references resolve. Broken
references are reported as upstream defects (the baseline is never edited to hide them). Exit 1 on any integrity
failure.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lmfg_common import (MANIFEST_PATH, ROOT, UPSTREAM_DIR, artifact_header, git_blob_sha1, load_json,  # noqa: E402
                         sha256_bytes, write_json)

PIN_REPO = "https://github.com/anthropics/claude-plugins-official"
PIN_SHA = "099387b7a2ea02022bb850becca750246ae12562"
PIN_PREFIX = "plugins/claude-for-manufacturing/"
EXPECTED_SKILLS = 17
# Paths inside the private plant pages that plant_setup.py builds at run time (its docstring lists them),
# e.g. setup/plant-context.txt and the legacy setup/plant-context.md. They name page files, not plugin files.
RUNTIME_PAGE_PREFIXES = ("setup/", "inquiries/", "sourcing/")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
TICK_RE = re.compile(r"`([A-Za-z0-9_./-]+\.(?:md|py|json))`")


def generate(clone: str) -> int:
    out = subprocess.run(["git", "-C", clone, "ls-tree", "-r", "-l", PIN_SHA, "--", PIN_PREFIX],
                         capture_output=True, text=True, check=True).stdout.splitlines()
    files, bad = [], []
    for line in out:
        meta, path = line.split("\t", 1)
        mode, _typ, blob, size = meta.split()
        rel = path[len(PIN_PREFIX):]
        data = (UPSTREAM_DIR / rel).read_bytes()
        if git_blob_sha1(data) != blob or len(data) != int(size):
            bad.append(rel)
        files.append({"path": rel, "mode": mode, "git_blob": blob, "size": int(size), "sha256": sha256_bytes(data)})
    if bad:
        print("REFUSING: imported bytes differ from upstream blobs:", bad, file=sys.stderr)
        return 1
    manifest = {
        "schema": "legion.manufacturing.upstream-manifest.v1",
        "upstream": {"repository": PIN_REPO, "revision": PIN_SHA, "subtree": PIN_PREFIX.rstrip("/"),
                     "imported_to": "upstream/claude-for-manufacturing", "license": "Apache-2.0 (upstream/claude-for-manufacturing/LICENSE)"},
        "file_count": len(files),
        "files": sorted(files, key=lambda f: f["path"]),
    }
    write_json(MANIFEST_PATH, manifest)
    print(f"manifest written: {len(files)} files, 0 mismatches")
    return 0


def _resolve_ref(src: pathlib.Path, ref: str) -> bool:
    ref = ref.split("#", 1)[0].split("?", 1)[0]
    if not ref or "://" in ref or ref.startswith(("mailto:", "#")):
        return True
    rel_src = src.relative_to(UPSTREAM_DIR)
    skill_root = UPSTREAM_DIR / rel_src.parts[0] / rel_src.parts[1] if rel_src.parts[0] == "skills" and len(rel_src.parts) > 2 else None
    bases = [src.parent, UPSTREAM_DIR] + ([skill_root] if skill_root else [])
    return any((b / ref).resolve().exists() for b in bases)


def check_references() -> dict:
    links, ticks, runtime = [], [], []
    for md in sorted(UPSTREAM_DIR.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        for m in LINK_RE.finditer(text):
            if not _resolve_ref(md, m.group(1)):
                links.append({"file": str(md.relative_to(UPSTREAM_DIR)).replace("\\", "/"), "ref": m.group(1)})
        for m in TICK_RE.finditer(text):
            ref = m.group(1)
            if "/" not in ref or ref.startswith(("<", "/")):
                continue  # bare names and placeholders are prose, not paths
            if not _resolve_ref(md, ref):
                item = {"file": str(md.relative_to(UPSTREAM_DIR)).replace("\\", "/"), "ref": ref}
                (runtime if ref.startswith(RUNTIME_PAGE_PREFIXES) else ticks).append(item)
    return {"markdown_links_unresolved": links, "backtick_paths_unresolved": ticks,
            "runtime_page_paths_not_repository_files": runtime}


def verify(evidence: str | None) -> int:
    m = load_json(MANIFEST_PATH)
    expected = {f["path"]: f for f in m["files"]}
    on_disk = {str(p.relative_to(UPSTREAM_DIR)).replace("\\", "/"): p for p in UPSTREAM_DIR.rglob("*") if p.is_file()}
    missing = sorted(set(expected) - set(on_disk))
    extra = sorted(set(on_disk) - set(expected))
    mismatched = []
    for path, f in expected.items():
        if path in on_disk:
            data = on_disk[path].read_bytes()
            if git_blob_sha1(data) != f["git_blob"] or sha256_bytes(data) != f["sha256"] or len(data) != f["size"]:
                mismatched.append(path)
    skills = sorted(p.name for p in (UPSTREAM_DIR / "skills").iterdir() if p.is_dir())
    skills_with_md = [s for s in skills if (UPSTREAM_DIR / "skills" / s / "SKILL.md").is_file()]
    licenses = [p for p in ("LICENSE",) if (UPSTREAM_DIR / p).is_file()]
    refs = check_references()
    ok = not missing and not extra and not mismatched and len(skills) == EXPECTED_SKILLS and len(skills_with_md) == EXPECTED_SKILLS and licenses
    result = artifact_header("python3 -I tools/upstream_manifest.py verify", {"manifest": "manifests/UPSTREAM_MANIFEST.json", "upstream_revision": m["upstream"]["revision"]})
    result.update({
        "schema": "legion.manufacturing.evidence.source-manifest.v1",
        "work_order": "WO-A02",
        "status": "PASS" if ok else "FAIL",
        "counts": {"manifest_files": len(expected), "files_on_disk": len(on_disk), "verified": len(expected) - len(missing) - len(mismatched),
                   "missing": len(missing), "extra": len(extra), "byte_mismatches": len(mismatched),
                   "skill_directories": len(skills), "skills_with_SKILL_md": len(skills_with_md)},
        "missing": missing, "extra": extra, "byte_mismatches": mismatched, "skills": skills,
        "license_files": licenses,
        "references": refs,
        "reference_status": "PASS" if not refs["markdown_links_unresolved"] and not refs["backtick_paths_unresolved"] else "UPSTREAM_DEFECTS_RECORDED",
        "manifest_sha256": sha256_bytes(MANIFEST_PATH.read_bytes()),
    })
    if evidence:
        write_json(ROOT / evidence, result)
    print(f"{result['status']}: {result['counts']} references={result['reference_status']}")
    for k in ("missing", "extra", "byte_mismatches"):
        if result[k]:
            print(k.upper(), result[k])
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate"); g.add_argument("--from-git", required=True)
    v = sub.add_parser("verify"); v.add_argument("--evidence")
    a = ap.parse_args(argv)
    return generate(a.from_git) if a.cmd == "generate" else verify(a.evidence)


if __name__ == "__main__":
    sys.exit(main())
