"""Repository policy checks: no secrets in tracked files, license rules (LICENSE_MATRIX.json).

  python3 -I tools/repo_policy.py [--evidence evidence/LICENSE_REPORT.json]

Secret scan: well-known credential shapes in every tracked text file (git ls-files). License rules: the vendored
Anthropic LICENSE is present and unchanged, and no source tree from a repository marked DO NOT COPY (Commerce,
Marketplace, Federation, Formal-Core) has been copied in. Exit 1 on any finding.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lmfg_common import MANIFEST_PATH, ROOT, UPSTREAM_DIR, artifact_header, load_json, sha256_file, write_json  # noqa: E402

SECRET_PATTERNS = {
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "github_token": r"gh[pousr]_[A-Za-z0-9]{36,}",
    "github_pat": r"github_pat_[A-Za-z0-9_]{40,}",
    "private_key_block": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----",
    "anthropic_key": r"sk-ant-[A-Za-z0-9_-]{20,}",
    "openai_style_key": r"\bsk-[A-Za-z0-9]{32,}\b",
    "nvidia_key": r"nvapi-[A-Za-z0-9_-]{20,}",
    "slack_token": r"xox[abprs]-[A-Za-z0-9-]{10,}",
    "paypal_client_secret_assignment": r"(?i)paypal[_-]?(?:client[_-]?)?secret\s*[:=]\s*['\"]?[A-Za-z0-9_-]{20,}",
    "generic_password_assignment": r"(?i)\bpassword\s*[:=]\s*['\"][^'\"\s]{8,}['\"]",
}
# Signature files of repositories whose code must not be copied here (LICENSE_MATRIX.json "DO NOT COPY").
FORBIDDEN_TREES = ["legion_marketplace", "legion_federation", "commerce_adapter"]
SELF = "tools/repo_policy.py"


def tracked_files():
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True, check=True).stdout
    return [f for f in out.decode().split("\0") if f]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--evidence")
    a = ap.parse_args(argv)
    files = tracked_files()
    secrets = []
    for f in files:
        if f == SELF:
            continue
        p = ROOT / f
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for name, rx in SECRET_PATTERNS.items():
            for m in re.finditer(rx, text):
                secrets.append({"file": f, "pattern": name, "line": text.count("\n", 0, m.start()) + 1})
    manifest = {x["path"]: x for x in load_json(MANIFEST_PATH)["files"]}
    lic_ok = (UPSTREAM_DIR / "LICENSE").is_file() and sha256_file(UPSTREAM_DIR / "LICENSE") == manifest["LICENSE"]["sha256"]
    lic_text = (UPSTREAM_DIR / "LICENSE").read_text(encoding="utf-8") if lic_ok else ""
    forbidden = sorted({f for f in files for t in FORBIDDEN_TREES if f"/{t}/" in "/" + f})
    matrix = load_json(ROOT / "LICENSE_MATRIX.json")
    ok = not secrets and lic_ok and "Apache License" in lic_text and not forbidden
    res = artifact_header("python3 -I tools/repo_policy.py", {"tracked_files": len(files), "license_matrix": "LICENSE_MATRIX.json"})
    res.update({"schema": "legion.manufacturing.evidence.license-report.v1", "work_order": "WO-A01/WO-A02",
                "status": "PASS" if ok else "FAIL",
                "counts": {"tracked_files_scanned": len(files) - 1, "secret_findings": len(secrets), "forbidden_copies": len(forbidden)},
                "secret_findings": secrets, "upstream_license": {"present_and_unchanged": lic_ok, "type": "Apache-2.0" if "Apache License" in lic_text else None},
                "forbidden_copies": forbidden, "license_matrix_sources": [s["source"] + ": " + s["decision"] for s in matrix["sources"]],
                "open_owner_decisions": matrix["open_owner_decisions"]})
    if a.evidence:
        write_json(ROOT / a.evidence, res)
    print(f"{res['status']}: {res['counts']} upstream_license_ok={lic_ok}")
    for s in secrets:
        print("  SECRET?", s)
    for f in forbidden:
        print("  FORBIDDEN COPY", f)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
