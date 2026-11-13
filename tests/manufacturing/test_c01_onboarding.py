"""C01 onboarding: the plant profile persists, reconnects and reports missing systems (upstream plant_setup.py)."""
import tempfile
import unittest

from manufacturing.connectors.lifecycle import Lifecycle
from manufacturing.runtime import upstream_exec as X
from tests.manufacturing import base


class C01Onboarding(base.SkillSuite):
    CID = "C01"

    def test_c01_profile_persists_and_reconnects(self):
        with tempfile.TemporaryDirectory() as data:
            env = {"CLAUDE_PLUGIN_DATA": data}
            with X.TaskFolder() as t:
                src = t.dir / "plant-context.txt"
                src.write_text(X.profile_fixture()["setup"], encoding="utf-8")
                r = t.plant_setup("install", "--from", src, "--company", X.COMPANY, env=env)
                self.assertEqual(r["rc"], 0, r)
                self.assertTrue(r["json"]["persistent"])
            with X.TaskFolder() as t2:                      # a new conversation, nothing uploaded
                f = t2.plant_setup("find", env=env)["json"]
                self.assertTrue(f["exists"] and f["persistent"])
                self.assertEqual(f["company"], X.COMPANY)

    def test_c01_render_refuses_rate_values_and_emails(self):
        with X.TaskFolder() as t:
            setup = X.profile_fixture()["setup"]
            bad = t.dir / "bad.txt"
            bad.write_text(setup + "\n### Commercial rates\n\n- **Labor rate:** confirmed 62.00/hr\n", encoding="utf-8")
            self.assertEqual(t.plant_setup("render", "--profile", bad, "--out", t.dir / "p1")["rc"], 2)
            bad.write_text(setup + "\n- **Quality contact:** someone@example.com\n", encoding="utf-8")
            self.assertEqual(t.plant_setup("render", "--profile", bad, "--out", t.dir / "p2")["rc"], 2)
            good = t.dir / "good.txt"
            good.write_text(setup, encoding="utf-8")
            self.assertEqual(t.plant_setup("render", "--profile", good, "--out", t.dir / "p3")["rc"], 0)

    def test_c01_stamp_changes_only_the_configured_line(self):
        with X.TaskFolder() as t:
            p = t.dir / "p.txt"
            p.write_text(X.profile_fixture()["setup"], encoding="utf-8")
            before = p.read_text(encoding="utf-8").splitlines()
            self.assertEqual(t.plant_setup("stamp", "--profile", p)["rc"], 0)
            after = p.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(before), len(after))
            diff = [a for a, b in zip(before, after) if a != b]
            self.assertTrue(all("Configured" in a for a in diff))

    def test_c01_missing_systems_reported_not_connected(self):
        text = X.profile_fixture()["setup"]
        not_live = next(l for l in text.splitlines() if "Connectors not live" in l).split(":**", 1)[1]
        self.assertIn("Autodesk Fusion", not_live)
        self.assertEqual(Lifecycle("fusion").state, "DISCONNECTED")   # listed as not live: stays DISCONNECTED
        with X.TaskFolder() as t:                                    # no profile: reported absent, never invented
            f = t.plant_setup("find")["json"]
            self.assertFalse(f["exists"])
            self.assertIsNone(f["company"])


if __name__ == "__main__":
    unittest.main()
