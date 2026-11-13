"""Print a GitHub Actions ::notice:: with an evidence file's status, counts and SHA-256.

Annotations are readable through the public API without signing in (job logs, summaries and artifacts are not), so
this line is how anyone can check a run's numbers and match them to the committed evidence.
"""
import hashlib
import json
import pathlib
import sys


def main(path: str) -> int:
    p = pathlib.Path(path)
    if not p.exists():
        print(f"::error title={p.name}::evidence file was not produced")
        return 0
    d = json.loads(p.read_text(encoding="utf-8"))
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    counts = " ".join(f"{k}={v}" for k, v in (d.get("counts") or {}).items() if not isinstance(v, (dict, list)))
    gate = f" gate_d02={d['gate_d02']}" if "gate_d02" in d else ""
    print(f"::notice title={p.name}::status={d.get('status')}{gate} {counts} sha256={sha} "
          f"source_commit={d.get('source_commit')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
