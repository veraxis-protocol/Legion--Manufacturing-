"""Run a test package and publish a machine-readable result per test, per class and per module.

  python -I tools/test_report.py skills      --evidence evidence/SKILL_MATRIX.json
  python -I tools/test_report.py connectors  --evidence evidence/CONNECTOR_CONTRACTS.json
  python -I tools/test_report.py engineering --evidence evidence/CAD_INTEGRATION.json   (D01 only)
  python -I tools/test_report.py verifier    --evidence <file>                         (D02, see tools/d02_run.py)

A skipped test is never PASS: its reason must start with "NOT RUN:" or "BLOCKED:" and it is counted under that
name; any other skip reason is counted as FAIL (an unexplained skip hides a result). Exit 1 on any FAIL or ERROR.
For `skills`, each of the 17 skills also carries its classification (manufacturing/runtime/catalog.py).
"""
from __future__ import annotations

import argparse
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT / "tools"))

from lmfg_common import artifact_header, write_json  # noqa: E402

SUITES = {"skills": ("tests/manufacturing", "test_*.py"), "connectors": ("tests/connectors", "test_*.py"),
          "engineering": ("tests/engineering", "test_d01_*.py"), "verifier": ("tests/engineering", "test_d02_*.py"),
          "runtime": ("tests/runtime", "test_*.py"),
          "all": ("tests", "test_*.py")}
CLASS_OF = {"test_1_": "1_positive", "test_2_": "2_negative", "test_3_": "3_missing_data", "test_4_": "4_provenance",
            "test_5_": "5_approval_boundary", "test_6_": "6_regression", "test_7_": "model_driven_run",
            "test_8_": "live_systems"}


class Recorder(unittest.TextTestResult):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.rows = []

    def _row(self, test, status, detail=""):
        tid = test.id()
        parts = tid.split(".")
        self.rows.append({"id": tid, "module": parts[-3] if len(parts) >= 3 else tid, "class": parts[-2],
                          "test": parts[-1], "status": status, "detail": detail[-1500:]})

    def addSuccess(self, test):
        super().addSuccess(test)
        self._row(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._row(test, "FAIL", self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self._row(test, "ERROR", self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if reason.startswith("NOT RUN:"):
            self._row(test, "NOT_RUN", reason)
        elif reason.startswith("BLOCKED:"):
            self._row(test, "BLOCKED", reason)
        else:
            self._row(test, "FAIL", "unexplained skip: " + reason)


def run(suite_dir: str, pattern: str = "test_*.py") -> list:
    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / suite_dir), pattern=pattern, top_level_dir=str(ROOT))
    runner = unittest.TextTestRunner(resultclass=Recorder, verbosity=1, stream=sys.stderr)
    return runner.run(suite).rows


def skills_view(rows):
    from manufacturing.runtime import catalog as K
    out = []
    for s in K.SKILLS:
        mod = [r for r in rows if r["module"].startswith(f"test_{s['id'].lower()}_")]
        by_class = {}
        for r in mod:
            key = next((v for k, v in CLASS_OF.items() if r["test"].startswith(k)), "skill_specific")
            by_class.setdefault(key, Counter())[r["status"]] += 1
        out.append({**K.classify(s), "tests": len(mod), "counts": dict(Counter(r["status"] for r in mod)),
                    "by_class": {k: dict(v) for k, v in sorted(by_class.items())},
                    "verdict": ("FAIL" if any(r["status"] in ("FAIL", "ERROR") for r in mod) or not mod else
                                "PASS_WITH_BLOCKED" if any(r["status"] == "BLOCKED" for r in mod) else "PASS"),
                    "results": [{k: r[k] for k in ("test", "status", "detail") if r[k]} for r in mod]})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("suite", choices=sorted(SUITES))
    ap.add_argument("--evidence", required=True)
    a = ap.parse_args(argv)
    rows = run(*SUITES[a.suite])
    counts = Counter(r["status"] for r in rows)
    doc = {**artifact_header(f"python -I tools/test_report.py {a.suite}", {"suite": SUITES[a.suite][0], "pattern": SUITES[a.suite][1]}),
           "status": "FAIL" if counts["FAIL"] or counts["ERROR"] or not rows else "PASS",
           "counts": {"tests": len(rows), **{k: counts.get(k, 0) for k in ("PASS", "FAIL", "ERROR", "NOT_RUN", "BLOCKED")}},
           "rule": "NOT_RUN and BLOCKED are never counted as PASS; an unexplained skip is a FAIL"}
    if a.suite == "skills":
        doc["skills"] = skills_view(rows)
        modes = Counter(s["mode"] for s in doc["skills"])
        doc["classification_counts"] = dict(modes)
        doc["skills_passing"] = sum(s["verdict"] != "FAIL" for s in doc["skills"])
    else:
        doc["modules"] = {}
        for r in rows:
            m = doc["modules"].setdefault(r["module"], Counter())
            m[r["status"]] += 1
        doc["modules"] = {k: dict(v) for k, v in sorted(doc["modules"].items())}
        doc["results"] = rows
    write_json(Path(a.evidence), doc)
    print(json.dumps(doc["counts"]))
    return 1 if doc["status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
