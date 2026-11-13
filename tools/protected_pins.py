"""INV-09: every protected LEGION repository must still be at its reviewed pin (read-only check, git ls-remote).

  python3 -I tools/protected_pins.py [--evidence evidence/PROTECTED_REPOS.json]

Exit 1 if any pinned revision no longer resolves or a default-branch HEAD moved. Network required.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lmfg_common import ROOT, artifact_header, load_json, write_json  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--evidence")
    a = ap.parse_args(argv)
    pins = load_json(ROOT / "SOURCE_PINS.json")
    rows = []
    informational = [dict(pins["upstream"], repository=pins["upstream"]["repository"].replace("https://github.com/", ""))]
    informational += pins.get("third_party", [])        # WO-LMFG-003: ZTL repositories (third party, may move)
    for p in pins["protected"] + informational:
        url = "https://github.com/" + p["repository"] + ".git"
        r = subprocess.run(["git", "ls-remote", url, "HEAD"], capture_output=True, text=True, timeout=120)
        head = r.stdout.split()[0] if r.returncode == 0 and r.stdout.strip() else None
        if p not in pins["protected"] and head != p["revision"]:
            # a third-party HEAD may move; the pin itself must still exist (fetchable by its commit id)
            import urllib.request
            req = urllib.request.Request(f"https://api.github.com/repos/{p['repository']}/commits/{p['revision']}",
                                         headers={"User-Agent": "legion-manufacturing-ci",
                                                  "Accept": "application/vnd.github+json"})
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    head = head if resp.status == 200 else None
            except Exception:  # noqa: BLE001 - the pin cannot be shown to exist: reported, never PASS
                head = None
        rows.append({"repository": p["repository"], "pinned": p["revision"], "remote_head": head,
                     "status": "PASS" if head == p["revision"] else ("ERROR" if head is None else "MOVED"),
                     "protected": p in pins["protected"]})
    protected_ok = all(r["status"] == "PASS" for r in rows if r["protected"])
    res = artifact_header("python3 -I tools/protected_pins.py", {"pins": "SOURCE_PINS.json"})
    res.update({"schema": "legion.manufacturing.evidence.protected-repos.v1", "invariant": "INV-09",
                "status": "PASS" if protected_ok else "FAIL", "repositories": rows,
                "note": "upstream (Anthropic) and the third-party ZTL repositories are informational: they may legitimately move; "
                        "this repository uses them only at their pins"})
    if a.evidence:
        write_json(ROOT / a.evidence, res)
    for r in rows:
        print(f"{r['status']:6} {r['repository']} pinned={r['pinned'][:12]} head={(r['remote_head'] or '-')[:12]}{'' if r['protected'] else ' (upstream, informational)'}")
    return 0 if protected_ok else 1


if __name__ == "__main__":
    sys.exit(main())
