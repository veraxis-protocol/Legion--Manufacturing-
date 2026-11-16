"""WO-A02 / INV-01: the imported Claude for Manufacturing baseline is complete and byte-identical to its pin."""
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from lmfg_common import MANIFEST_PATH, UPSTREAM_DIR, git_blob_sha1, sha256_bytes  # noqa: E402

PIN = "099387b7a2ea02022bb850becca750246ae12562"
SKILLS = ["breakdown-diagnosis", "breakdown-to-next-report", "custom-connector", "customer-inquiry-intake",
          "daily-production-report", "data-consolidate", "design-space-explore", "inspection-to-capa",
          "morning-plant-pulse", "ncr-writeup", "onboarding", "quote-build", "rfq-to-quote", "root-cause-capa",
          "supplier-escape-to-alternate-source", "supplier-quote-request", "trade-study-report"]


class SourceIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_manifest_pinned_to_reviewed_revision(self):
        self.assertEqual(self.m["upstream"]["revision"], PIN)
        self.assertEqual(self.m["upstream"]["subtree"], "plugins/claude-for-manufacturing")

    def test_every_manifest_file_is_byte_identical(self):
        for f in self.m["files"]:
            data = (UPSTREAM_DIR / f["path"]).read_bytes()
            self.assertEqual(git_blob_sha1(data), f["git_blob"], f["path"])
            self.assertEqual(sha256_bytes(data), f["sha256"], f["path"])

    def test_no_unmanifested_files(self):
        on_disk = {str(p.relative_to(UPSTREAM_DIR)).replace("\\", "/") for p in UPSTREAM_DIR.rglob("*") if p.is_file()}
        self.assertEqual(on_disk, {f["path"] for f in self.m["files"]})

    def test_required_content_present(self):
        for p in (".claude-plugin/plugin.json", ".mcp.json", "LICENSE", "README.md"):
            self.assertTrue((UPSTREAM_DIR / p).is_file(), p)
        self.assertTrue((UPSTREAM_DIR / "shared" / "contracts").is_dir())

    def test_all_17_skills_present_with_skill_md(self):
        found = sorted(p.name for p in (UPSTREAM_DIR / "skills").iterdir() if p.is_dir())
        self.assertEqual(found, SKILLS)
        for s in SKILLS:
            self.assertTrue((UPSTREAM_DIR / "skills" / s / "SKILL.md").is_file(), s)

    def test_license_is_apache_2(self):
        self.assertIn("Apache License", (UPSTREAM_DIR / "LICENSE").read_text(encoding="utf-8"))
        self.assertIn("Version 2.0", (UPSTREAM_DIR / "LICENSE").read_text(encoding="utf-8"))

    def test_tamper_is_detected(self):
        # Negative: a single changed byte must break both digests.
        f = next(x for x in self.m["files"] if x["path"] == "shared/scripts/plant_setup.py")
        data = (UPSTREAM_DIR / f["path"]).read_bytes()
        tampered = data[:-1] + (b"#" if data[-1:] != b"#" else b" ")
        self.assertNotEqual(git_blob_sha1(tampered), f["git_blob"])
        self.assertNotEqual(sha256_bytes(tampered), f["sha256"])

    def test_verify_tool_passes(self):
        r = subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "upstream_manifest.py"), "verify"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("references=PASS", r.stdout)


if __name__ == "__main__":
    unittest.main()
