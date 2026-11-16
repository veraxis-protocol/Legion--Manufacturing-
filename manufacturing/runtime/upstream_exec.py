"""Run the upstream plugin's own code, unchanged, from a copy in a task folder (never inside the vendored tree).

The plant profile used here is assembled from the ```markdown blocks of upstream
skills/onboarding/reference/config-profile.md (the profile contract's own example), with each block's line range
recorded, so the profile is source-bound and changes when upstream changes.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "upstream" / "claude-for-manufacturing"
CONFIG_PROFILE = PLUGIN / "skills" / "onboarding" / "reference" / "config-profile.md"
COMPANY = "Example Manufacturing"


def _blocks():
    lines = CONFIG_PROFILE.read_text(encoding="utf-8").split("\n")
    out, cur = [], None
    for i, l in enumerate(lines, 1):
        if l.startswith("```markdown"):
            cur = [i, []]
        elif l.startswith("```") and cur:
            out.append({"start": cur[0], "end": i, "text": "\n".join(cur[1])})
            cur = None
        elif cur:
            cur[1].append(l)
    return out


def profile_fixture() -> dict:
    """The ## Plant context block (setup file) and the ## Plant rates block (rates file), source-bound."""
    blocks = _blocks()
    setup = [b for b in blocks if b["text"].startswith(("## Plant context", "### ")) and
             not b["text"].startswith("### Commercial rates")]
    rates = [b for b in blocks if b["text"].startswith("## Plant rates")]
    sha = hashlib.sha256(CONFIG_PROFILE.read_bytes()).hexdigest()
    src = str(CONFIG_PROFILE.relative_to(ROOT)).replace("\\", "/")
    return {"setup": "\n\n".join(b["text"] for b in setup) + "\n",
            "rates": "\n\n".join(b["text"] for b in rates) + "\n",
            "source": {"file": src, "sha256": sha, "setup_blocks": [[b["start"], b["end"]] for b in setup],
                       "rates_blocks": [[b["start"], b["end"]] for b in rates]}}


class TaskFolder:
    """A temporary task folder holding a copy of the plugin. Use as a context manager."""

    def __enter__(self):
        self._td = tempfile.TemporaryDirectory(prefix="lmfg-task-")
        self.dir = Path(self._td.name)
        self.plugin = self.dir / "plugin"
        shutil.copytree(PLUGIN, self.plugin)
        self.task = self.dir / "task"
        self.task.mkdir()
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("MFG_", "CLAUDE_PLUGIN_DATA"))}
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"
        return self

    def __exit__(self, *exc):
        self._td.cleanup()

    def run(self, script_rel: str, *args, cwd=None, env=None, timeout=120) -> dict:
        e = dict(self.env)
        e.update(env or {})
        p = subprocess.run([sys.executable, "-I", str(self.plugin / script_rel), *map(str, args)],
                           cwd=str(cwd or self.task), env=e, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
        out = {"rc": p.returncode, "stdout": p.stdout, "stderr": p.stderr[-2000:]}
        try:
            out["json"] = json.loads(p.stdout.strip().splitlines()[-1]) if p.stdout.strip() else None
        except (json.JSONDecodeError, IndexError):
            out["json"] = None
        return out

    def plant_setup(self, *args, **kw) -> dict:
        return self.run("shared/scripts/plant_setup.py", *args, **kw)

    def install_profile(self, with_rates: bool = True) -> dict:
        fx = profile_fixture()
        src = self.dir / "page-files"
        src.mkdir(exist_ok=True)
        (src / "plant-context.txt").write_text(fx["setup"], encoding="utf-8")
        res = {"setup": self.plant_setup("install", "--from", src / "plant-context.txt", "--company", COMPANY)}
        if with_rates:
            (src / "plant-rates.txt").write_text(fx["rates"], encoding="utf-8")
            res["rates"] = self.plant_setup("install", "--from", src / "plant-rates.txt", "--company", COMPANY,
                                            "--kind", "rates")
        return res

    def plugin_tree_digest(self) -> str:
        h = hashlib.sha256()
        for p in sorted(self.plugin.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                h.update(str(p.relative_to(self.plugin)).replace("\\", "/").encode())
                h.update(p.read_bytes())
        return h.hexdigest()

    def pulse(self, exports: Path, day: str, out_name="pulse-out", env=None, extra=()) -> dict:
        out = self.task / out_name
        exports = Path(exports).resolve()
        r = self.run("skills/morning-plant-pulse/scripts/pulse_compute.py", "--exports", exports, "--out", out,
                     "--day", day, "--run-time", f"{day}T23:00:00", "--tz", "UTC", *extra, env=env)
        r["out"] = out
        f = out / "day_records.json"
        r["day_records"] = json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
        return r


def skill_files_digest(skill: str, manifest: dict) -> dict:
    """Recompute every file of one skill against the Phase A manifest (regression against the upstream baseline)."""
    prefix = f"skills/{skill}/"
    rows = [f for f in manifest["files"] if f["path"].startswith(prefix)]
    bad = []
    for f in rows:
        data = (PLUGIN / f["path"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != f["sha256"]:
            bad.append(f["path"])
    return {"files": len(rows), "mismatched": bad}
