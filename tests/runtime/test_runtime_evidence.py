"""WO-LMFG-004: integrity of the committed model-driven execution evidence (evidence/SKILL_OUTPUTS).

These tests do not run a model and do not judge a work product (the producer and the independent evaluator did that,
and their transcripts are committed). They check that what is committed is what was recorded:
  - every output file matches the SHA-256 in its run.json
  - every run read the original SKILL.md of its case's skill, and never used a web/MCP/messaging tool
  - the plugin copy and the inputs were unchanged by each run
  - published transcripts are redacted (message content only) and carry no e-mail address outside the synthetic
    .example domains
  - no run is reported PASS without an independent evaluator PASS, and a live-required skill is never PASS
"""
import gzip
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence" / "SKILL_OUTPUTS"
CASES = {c["id"]: c for c in json.loads((ROOT / "tests" / "runtime" / "cases.json").read_text(encoding="utf-8"))["cases"]}
RUNS = sorted(OUT.glob("*/*/run.json"))
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def records():
    for p in RUNS:
        if p.parent.name in ("positive", "negative", "cli-positive", "cli-negative"):
            yield p, json.loads(p.read_text(encoding="utf-8"))


class RuntimeEvidence(unittest.TestCase):
    def test_runs_exist(self):
        self.assertTrue(RUNS, "no model-driven run is committed")

    def test_output_hashes(self):
        for p, r in records():
            for o in r["outputs"]:
                f = p.parent / "out" / o["path"]
                with self.subTest(run=str(p.parent.relative_to(OUT)), file=o["path"]):
                    self.assertTrue(f.exists())
                    self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(), o["sha256"])

    def test_skill_read_and_tools(self):
        for p, r in records():
            with self.subTest(run=str(p.parent.relative_to(OUT))):
                case = CASES[r["case"]]
                self.assertTrue(any(s and (s == case["skill"] or s.endswith(":" + case["skill"]))
                                    for s in r["skills_invoked"]), r["skills_invoked"])
                checks = {c["check"]: c["pass"] for c in r["deterministic_checks"]}
                tool_check = [k for k in checks if k.startswith("only the permitted tools")]
                ext_check = [k for k in checks if k.startswith("no external network")]
                self.assertTrue(tool_check and all(checks[k] for k in tool_check))
                self.assertTrue(ext_check and all(checks[k] for k in ext_check))
                self.assertEqual(r["plugin_copy_modified"], [])

    def test_cli_runs_discovered_the_plugin(self):
        """Route 1 (Claude Code CLI): the plugin was discovered from --plugin-dir and the skill entered through the
        Skill tool, not by reading a path the prompt gave."""
        for p, r in records():
            if r.get("runtime_route") != "cli" or r["status"] == "BLOCKED" and not r.get("deterministic_checks"):
                continue
            with self.subTest(run=str(p.parent.relative_to(OUT))):
                self.assertTrue(p.parent.name.startswith("cli-"))
                self.assertEqual(r["plugin_discovery"]["manufacturing_skills_listed"], 17)
                self.assertTrue(any(c["tool"] == "Skill" for c in r["tool_calls"]))

    def test_status_rules(self):
        for p, r in records():
            with self.subTest(run=str(p.parent.relative_to(OUT))):
                ev = (r.get("evaluator") or {}).get("verdict") or {}
                if r["status"] == "PASS":
                    self.assertEqual(ev.get("verdict"), "PASS")
                    self.assertFalse(ev.get("fabrication"))
                    self.assertTrue(all(c["pass"] for c in r["deterministic_checks"]))
                if CASES[r["case"]].get("live_required") and r["variant"] == "positive":
                    self.assertEqual(r["status"], "BLOCKED")

    def test_transcripts_redacted(self):
        for p, r in records():
            for name in ("transcript.jsonl.gz", "evaluator.jsonl.gz"):
                f = p.parent / name
                if not f.exists():
                    continue
                with self.subTest(file=str(f.relative_to(OUT))):
                    for line in gzip.open(f, "rt", encoding="utf-8"):
                        e = json.loads(line)
                        self.assertEqual(set(e), {"type", "timestamp", "model", "usage", "content"})
                    text = gzip.open(f, "rt", encoding="utf-8").read()
                    bad = [m for m in EMAIL.findall(text) if not re.search(r"\.example\b", m)
                           and not m.endswith((".py", ".md", ".json"))]
                    self.assertEqual(bad, [], "e-mail address outside the synthetic .example domains")


if __name__ == "__main__":
    unittest.main()
