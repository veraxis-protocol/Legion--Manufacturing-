"""Every committed evidence file renders as a job summary and a notice (a rendering crash once turned two green
checks red in CI run 43498728219: the Phase A files use a "skills" key of a different shape)."""
import io
import json
import pathlib
import sys
import unittest
from contextlib import redirect_stdout

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import ci_notice  # noqa: E402
import ci_summary  # noqa: E402


class Render(unittest.TestCase):
    def test_every_evidence_file_renders(self):
        files = sorted((ROOT / "evidence").glob("*.json"))
        if not files:   # evidence is produced by the CI jobs and is not stored in the repository
            self.skipTest("no evidence files in this checkout")
        for f in files:
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(ci_summary.main(str(f)), 0, f.name)
                self.assertEqual(ci_notice.main(str(f)), 0, f.name)
            self.assertIn(f.name, buf.getvalue())

    def test_missing_file_is_reported(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ci_summary.main(str(ROOT / "evidence" / "DOES_NOT_EXIST.json"))
        self.assertIn("MISSING", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
