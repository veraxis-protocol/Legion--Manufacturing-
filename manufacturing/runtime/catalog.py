"""The 17 upstream skills, classified by how each one can actually run (WO-LMFG-002 item 2).

Every classification is bound to a sentence in the skill's own SKILL.md: `file_only_quote` and `live_quote` must be
found verbatim in that file (tests fail otherwise), so the classification cannot drift from the upstream text.

Axes, independent of each other:
  deterministic_code   upstream Python the skill runs itself (executed here, on fixtures, every CI run)
  file_only            the skill states it runs from supplied files with no connector (so a missing ERP is NOT a
                       reason to block it)
  claude_runtime       the skill's reasoning steps are Markdown instructions executed by Claude: a model-driven run
                       needs the Claude runtime and is NOT RUN here (no model output is ever claimed from a fixture)
  live_required        external systems without which the skill cannot produce its output at all (BLOCKED here)
  live_optional        systems that improve it; their absence degrades, per the skill's Degradation section
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "upstream" / "claude-for-manufacturing"
FIND = "plant_setup.py find"

SKILLS = [
    {"id": "C01", "skill": "onboarding", "deterministic_code": ["plant_setup.py find", "plant_setup.py render",
                                                                 "plant_setup.py install", "plant_setup.py stamp",
                                                                 "plant_setup.py saved", "plant_setup.py put"],
     "file_only": True, "file_only_quote": "takes a bulk drop of the plant's own documents",
     "live_required": [], "live_optional": ["Microsoft 365", "Oracle NetSuite", "Infor M3", "Autodesk Fusion"],
     "live_quote": "tests the four supported connectors", "produces": ["plant profile"], "consumes": []},
    {"id": "C02", "skill": "custom-connector", "deterministic_code": [FIND], "file_only": False,
     "file_only_quote": None, "live_required": ["the target system (vendor API, database view or export contract)"],
     "live_optional": [], "live_quote": "Test against real data, and show it back",
     "produces": ["consolidated-dataset"], "consumes": []},
    {"id": "C03", "skill": "data-consolidate", "deterministic_code": [FIND], "file_only": True,
     "file_only_quote": "File-only is the designed path", "live_required": [],
     "live_optional": ["Oracle NetSuite", "Infor M3", "CMMS"], "live_quote": "If no connector is available at all",
     "produces": ["consolidated-dataset"], "consumes": []},
    {"id": "C04", "skill": "customer-inquiry-intake", "deterministic_code": [FIND], "file_only": True,
     "file_only_quote": "Runs on a pasted email and an uploaded PDF with no connector at all.", "live_required": [],
     "live_optional": ["Microsoft 365", "Oracle NetSuite"], "live_quote": "Accept the RFQ pasted or uploaded",
     "produces": ["intake-form"], "consumes": []},
    {"id": "C05", "skill": "quote-build", "deterministic_code": [FIND], "file_only": True,
     "file_only_quote": "Runs on the intake form plus pasted cost figures with no connector at all.",
     "live_required": [], "live_optional": ["Oracle NetSuite", "Infor M3", "Autodesk Fusion"],
     "live_quote": "Feature path only, and the internal sheet says so",
     "produces": [], "consumes": ["intake-form", "geometry-estimate", "supplier-bid", "consolidated-dataset"]},
    {"id": "C06", "skill": "rfq-to-quote", "deterministic_code": [FIND], "file_only": True,
     "file_only_quote": "**The chain still completes.**", "live_required": [],
     "live_optional": ["Autodesk Fusion", "Oracle NetSuite", "Infor M3", "Microsoft 365"],
     "live_quote": "Steps 5 and 6 both degrade", "produces": ["geometry-estimate", "intake-form"],
     "consumes": ["consolidated-dataset"]},
    {"id": "C07", "skill": "supplier-quote-request", "deterministic_code": [FIND], "file_only": True,
     "file_only_quote": "Runs on an uploaded drawing and pasted quantities with no connector.", "live_required": [],
     "live_optional": ["Oracle NetSuite", "Infor M3", "Microsoft 365"],
     "live_quote": "the revision comparison **cannot clear**", "produces": ["supplier-bid"],
     "consumes": ["supplier-caused-flag"]},
    {"id": "C08", "skill": "design-space-explore", "deterministic_code": [], "file_only": False,
     "file_only_quote": None, "live_required": ["Autodesk Fusion desktop with the base model open"],
     "live_optional": [], "live_quote": "the skill cannot generate variants and says",
     "produces": ["variant-manifest"], "consumes": []},
    {"id": "C09", "skill": "trade-study-report", "deterministic_code": [FIND], "file_only": True,
     "file_only_quote": "Runs entirely from a filled-in matrix and pasted figures", "live_required": [],
     "live_optional": ["Oracle NetSuite", "Infor M3"], "live_quote": "with no\nconnector and no CAD backend at all",
     "produces": [], "consumes": ["variant-manifest"]},
    {"id": "C10", "skill": "daily-production-report", "deterministic_code": [FIND], "file_only": True,
     "file_only_quote": "Without a planning export", "live_required": [],
     "live_optional": ["Oracle NetSuite", "Infor M3", "CMMS"], "live_quote": "no CMMS connector is live",
     "produces": [], "consumes": ["consolidated-dataset", "downtime-record", "pulse-day-record", "floor-layout"]},
    {"id": "C11", "skill": "morning-plant-pulse",
     "deterministic_code": [FIND, "pulse_compute.py", "render_short.py"], "file_only": True,
     "file_only_quote": "Run connector-only and name every tab that could not be built", "live_required": [],
     "live_optional": ["Oracle NetSuite", "Infor M3", "CMMS"], "live_quote": "no CMMS connector is live",
     "produces": ["pulse-day-record"], "consumes": ["consolidated-dataset"]},
    {"id": "C12", "skill": "breakdown-diagnosis", "deterministic_code": [FIND], "file_only": True,
     "file_only_quote": "it reads the maintenance export", "live_required": [],
     "live_optional": ["CMMS", "Microsoft 365"], "live_quote": "no CMMS connector is live",
     "produces": ["downtime-record"], "consumes": ["consolidated-dataset"]},
    {"id": "C13", "skill": "breakdown-to-next-report", "deterministic_code": [], "file_only": True,
     "file_only_quote": "It still\nruns end to end", "live_required": [], "live_optional": ["CMMS"],
     "live_quote": "no CMMS connector is live", "produces": ["downtime-record"],
     "consumes": ["downtime-record"], "chain_of": ["breakdown-diagnosis", "daily-production-report"]},
    {"id": "C14", "skill": "ncr-writeup", "deterministic_code": [FIND], "file_only": True,
     "file_only_quote": "The skill runs on a pasted finding and an uploaded drawing with no connector at",
     "live_required": [], "live_optional": ["Oracle NetSuite", "Infor M3", "Microsoft 365"],
     "live_quote": "In-transit and at-customer cannot", "produces": ["ncr", "quality-register-record"],
     "consumes": ["consolidated-dataset"]},
    {"id": "C15", "skill": "root-cause-capa", "deterministic_code": [FIND], "file_only": True,
     "file_only_quote": "Runs on exports alone.", "live_required": [],
     "live_optional": ["Oracle NetSuite", "Infor M3"], "live_quote": "a supplier-caused determination usually cannot be reached",
     "produces": ["supplier-caused-flag", "quality-register-record"], "consumes": ["ncr"]},
    {"id": "C16", "skill": "inspection-to-capa", "deterministic_code": [], "file_only": True,
     "file_only_quote": "Report \"no searchable history available\" at step 3", "live_required": [],
     "live_optional": ["Microsoft 365", "CMMS"], "live_quote": "no CMMS connector is live",
     "produces": ["ncr", "supplier-caused-flag"], "consumes": ["ncr"], "chain_of": ["ncr-writeup", "root-cause-capa"]},
    {"id": "C17", "skill": "supplier-escape-to-alternate-source", "deterministic_code": [], "file_only": True,
     "file_only_quote": "Demand picture and vendor list come from documents or are asked for", "live_required": [],
     "live_optional": ["Oracle NetSuite", "Infor M3"], "live_quote": "The ERP (NetSuite or Infor M3)",
     "produces": ["supplier-caused-flag", "supplier-bid"], "consumes": ["supplier-caused-flag"],
     "chain_of": ["ncr-writeup", "root-cause-capa", "supplier-quote-request"]},
]


def skill_dir(name: str) -> Path:
    return PLUGIN / "skills" / name


def skill_md(name: str) -> str:
    return (skill_dir(name) / "SKILL.md").read_text(encoding="utf-8")


def line_of(text: str, quote: str):
    """1-based line of the first occurrence of quote (which may span lines, ignoring line-wrap whitespace)."""
    if quote is None:
        return None
    flat = " ".join(text.split())
    q = " ".join(quote.split())
    pos = flat.find(q)
    if pos < 0:
        return None
    words_before = len(flat[:pos].split())
    count = 0
    for i, line in enumerate(text.split("\n"), 1):
        count += len(line.split())
        if count > words_before:
            return i
    return None


def classify(s: dict) -> dict:
    """The machine-readable classification of one skill, with the upstream lines it rests on."""
    md = skill_md(s["skill"])
    front = md.split("---", 2)[1] if md.startswith("---") else ""
    desc = next((l.split(":", 1)[1].strip().strip('"') for l in front.splitlines() if l.startswith("description:")), "")
    if s["live_required"]:
        mode = "LIVE_SYSTEM_REQUIRED"
    elif s.get("chain_of"):
        mode = "FILE_CAPABLE_CHAIN"
    else:
        mode = "FILE_CAPABLE"
    return {
        "id": s["id"], "skill": s["skill"], "mode": mode,
        "description_sha256": hashlib.sha256(desc.encode()).hexdigest(),
        "skill_md_sha256": hashlib.sha256((skill_dir(s["skill"]) / "SKILL.md").read_bytes()).hexdigest(),
        "runs_plant_setup_find": FIND in md,
        "deterministic_code": s["deterministic_code"],
        "file_only": s["file_only"],
        "file_only_evidence": None if not s["file_only"] else {"quote": s["file_only_quote"],
                                                               "line": line_of(md, s["file_only_quote"])},
        "claude_runtime_required": True,
        "live_required": s["live_required"], "live_optional": s["live_optional"],
        "live_evidence": {"quote": s["live_quote"], "line": line_of(md, s["live_quote"])},
        "approval_gates_section": "## Approval gates" in md,
        "produces": s["produces"], "consumes": s["consumes"], "chain_of": s.get("chain_of", []),
    }


def by_id(cid: str) -> dict:
    return next(s for s in SKILLS if s["id"] == cid)
