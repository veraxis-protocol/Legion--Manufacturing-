"""SHA-256 manifest of the evidence files, plus the upstream baseline and the pinned-source manifests they rest on.

  python -I tools/evidence_manifest.py [--dir evidence] [--check]

Writes evidence/SHA256SUMS (sha256sum format) and evidence/EVIDENCE_MANIFEST.json. With --check it verifies the
committed SHA256SUMS against the files and exits 1 on any difference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from lmfg_common import artifact_header, write_json  # noqa: E402

EXTRA = ["manifests/UPSTREAM_MANIFEST.json", "manifests/ZTL_SOURCE_PINS.json", "legion/engineering/DEAL_RESCUE_PIN.json",
         "SOURCE_PINS.json",
         "LICENSE_MATRIX.json"]


def files(d: Path):
    out = sorted(p for p in d.glob("*.json") if p.name != "EVIDENCE_MANIFEST.json")
    return out + [ROOT / e for e in EXTRA if (ROOT / e).exists()]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="evidence")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    d = ROOT / a.dir
    rows = [(hashlib.sha256(p.read_bytes()).hexdigest(), str(p.relative_to(ROOT)).replace("\\", "/")) for p in files(d)]
    sums = "".join(f"{h}  {p}\n" for h, p in rows)
    if a.check:
        have = (d / "SHA256SUMS").read_text(encoding="utf-8") if (d / "SHA256SUMS").exists() else ""
        if have != sums:
            sys.stderr.write("SHA256SUMS differs from the files\n")
            return 1
        print("SHA256SUMS verified:", len(rows), "files")
        return 0
    (d / "SHA256SUMS").write_bytes(sums.encode("utf-8"))
    write_json(d / "EVIDENCE_MANIFEST.json", {**artifact_header("python -I tools/evidence_manifest.py", {}),
                                               "files": [{"path": p, "sha256": h} for h, p in rows]})
    print(len(rows), "files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
