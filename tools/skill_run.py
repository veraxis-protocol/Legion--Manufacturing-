"""WO-LMFG-004 A03: run one upstream manufacturing skill through the real Claude Code runtime and record what happened.

Nothing here generates a model answer. Each run:
  1. builds a task folder: a byte-for-byte copy of upstream/claude-for-manufacturing (the vendored tree itself is never
     the plugin dir, so a run cannot write into it) and the case's input files under work/inputs;
  2. runs the installed Claude Code CLI non-interactively:
       claude -p <task> --plugin-dir <copy> --output-format stream-json --verbose --restricted --strict-mcp-config
              --tools <file tools, Skill, Bash> --allowedTools <python and read-only shell> --permission-mode dontAsk
     (restricted: no user/project settings or hooks, no web tools, file tools confined to the task folder; no MCP
     servers except the plugin's own Fusion entry, which only answers if Autodesk Fusion is running);
  3. parses the stream: model and CLI version, plugins and skills the runtime loaded, every tool call with its
     actual response, permission denials, tokens and duration;
  4. collects the files Claude wrote under work/out, hashes them, checks the plugin copy is still byte-identical;
  5. evaluates: deterministic checks taken from the case (skill activated, products exist, required facts present,
     fabricated values absent) AND an independent evaluator - a separate Claude session without the plugin and
     with read-only tools - that grades the work product against the skill's own SKILL.md.
PASS needs both. A run the CLI could not perform (not signed in, Fusion absent, ...) is BLOCKED, never PASS.
"""
from __future__ import annotations

import argparse
import fnmatch
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "upstream" / "claude-for-manufacturing"
CASES = ROOT / "tests" / "runtime" / "cases.json"
INPUTS = ROOT / "tests" / "runtime" / "inputs"
FIXTURES = ROOT / "tests" / "manufacturing" / "fixtures"
OUT = ROOT / "evidence" / "SKILL_OUTPUTS"
TOOLS = "Read,Write,Edit,Glob,Grep,Skill,Bash"
ALLOWED = ["Read", "Write", "Edit", "Glob", "Grep", "Skill", "Bash(python:*)", "Bash(python3:*)", "Bash(ls:*)",
           "Bash(mkdir:*)", "Bash(cat:*)", "Bash(head:*)", "Bash(wc:*)", "Bash(sqlite3:*)", "Bash(cd:*)"]
DENIED = ["WebFetch", "WebSearch", "Bash(curl:*)", "Bash(wget:*)", "Bash(pip:*)", "Bash(git:*)"]
TRUNC = 6000


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tree_digest(root: Path) -> dict:
    # Python's bytecode cache (__pycache__, written when a skill runs a plugin script) is not plugin content
    return {str(p.relative_to(root)).replace("\\", "/"): sha256(p) for p in sorted(root.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts}


def find_cli() -> str | None:
    if os.environ.get("CLAUDE_CLI"):
        return os.environ["CLAUDE_CLI"]
    found = shutil.which("claude")
    if found:
        return found
    base = Path(os.environ.get("LOCALAPPDATA", "")) / "Claude-Data"
    cands = sorted(base.glob("*/claude-code/*/*/claude.exe"), key=lambda p: p.stat().st_mtime, reverse=True)
    return str(cands[0]) if cands else None


def cli_version(cli: str) -> str:
    return subprocess.run([cli, "--version"], capture_output=True, text=True, timeout=60).stdout.strip()


def auth_status(cli: str) -> dict:
    """loggedIn / authMethod / apiProvider only (no account identifiers or credentials are kept)."""
    r = subprocess.run([cli, "auth", "status"], capture_output=True, text=True, timeout=60)
    try:
        d = json.loads(r.stdout)
    except ValueError:
        return {"loggedIn": None, "raw_exit": r.returncode}
    return {k: d.get(k) for k in ("loggedIn", "authMethod", "apiProvider")}


def load_cases() -> dict:
    return {c["id"]: c for c in json.loads(CASES.read_text(encoding="utf-8"))["cases"]}


def _src(spec: str) -> Path:
    if spec.startswith("fixtures/"):
        return FIXTURES / spec[len("fixtures/"):]
    if spec.startswith("evidence/"):        # an earlier stage's recorded artifact (E2E handoffs)
        return ROOT / spec
    if spec.startswith("ref/"):             # reBot reference files fetched at run time (CERN-OHL-W; not committed)
        return Path(os.environ.get("LMFG_REF", r"C:\LMFG\ref")) / spec[len("ref/"):]
    return INPUTS / spec


def stage_inputs(case: dict, variant: str, dest: Path) -> list:
    v = case[variant]
    drop = set(v.get("drop", []))
    staged = []
    for spec in v.get("inputs", case["positive"].get("inputs", [])):
        spec, _, alias = spec.partition("=>")         # "evidence/.../out=>intake" stages that folder as inputs/intake
        src = _src(spec)
        if not src.exists():
            raise FileNotFoundError(f"input {spec} does not exist (an earlier stage has not run?)")
        files = [src] if src.is_file() else sorted(p for p in src.rglob("*") if p.is_file())
        for f in files:
            rel = f.name if src.is_file() else str(Path(alias or src.name) / f.relative_to(src))
            if any(fnmatch.fnmatch(rel.replace("\\", "/"), d) or f.name == d for d in drop):
                continue
            t = dest / rel
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, t)
            src_name = (str(f.relative_to(ROOT)) if f.is_relative_to(ROOT) else
                        "reBot-DevArm@22f002a (pinned reference, fetched at run time): " + f.name)
            staged.append({"path": "inputs/" + rel.replace("\\", "/"), "source": src_name.replace("\\", "/"),
                           "sha256": sha256(f), "bytes": f.stat().st_size})
    return staged


def build_prompt(case: dict, variant: str) -> str:
    v = case[variant]
    task = v.get("prompt", case["positive"]["prompt"])
    return (task.strip() + "\n\nThe input files are in ./inputs (all of them are SYNTHETIC test data for a fictitious "
            "plant). Write every work product you produce as files under ./out. Do not contact, email or write to any "
            "external system; there is no live ERP, Microsoft 365, CMMS or supplier available in this session.")


def run_cli(cli: str, args: list, cwd: Path, timeout: int) -> tuple:
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT")}
    env["PYTHONIOENCODING"] = "utf-8"
    t0 = time.time()
    try:
        p = subprocess.run([cli] + args, cwd=cwd, capture_output=True, timeout=timeout, env=env,
                           encoding="utf-8", errors="replace")
        return p.returncode, p.stdout, p.stderr, time.time() - t0
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        return "TIMEOUT", out, "", time.time() - t0


def _text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(c.get("text", "") if isinstance(c, dict) else str(c) for c in content)
    return json.dumps(content)


def parse_stream(stdout: str) -> dict:
    events = []
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
    result = next((e for e in reversed(events) if e.get("type") == "result"), {})
    calls, by_id, text = [], {}, []
    for e in events:
        msg = e.get("message") or {}
        for b in msg.get("content") or [] if isinstance(msg.get("content"), list) else []:
            if e.get("type") == "assistant" and b.get("type") == "tool_use":
                c = {"id": b["id"], "tool": b["name"], "input": b.get("input"), "response": None, "is_error": None,
                     "parent_tool_use_id": e.get("parent_tool_use_id")}
                calls.append(c)
                by_id[b["id"]] = c
            elif e.get("type") == "assistant" and b.get("type") == "text":
                text.append(b["text"])
            elif e.get("type") == "user" and b.get("type") == "tool_result" and b.get("tool_use_id") in by_id:
                r = _text(b.get("content"))
                by_id[b["tool_use_id"]].update(response=r[:TRUNC] + ("...[truncated]" if len(r) > TRUNC else ""),
                                               is_error=bool(b.get("is_error")))
    skills_invoked = [c["input"].get("skill") or c["input"].get("command") for c in calls
                      if c["tool"] == "Skill" and isinstance(c["input"], dict)]
    skill_files_read = sorted({str(c["input"].get("file_path", "")).replace("\\", "/").split("/skills/")[-1]
                               for c in calls if c["tool"] == "Read" and isinstance(c["input"], dict)
                               and "/skills/" in str(c["input"].get("file_path", "")).replace("\\", "/")})
    return {
        "events": len(events),
        "runtime": {"model": init.get("model"), "claude_code_version": init.get("claude_code_version"),
                    "permission_mode": init.get("permissionMode"), "tools": init.get("tools"),
                    "plugins": init.get("plugins"), "skills": init.get("skills"),
                    "mcp_servers": init.get("mcp_servers"), "session_id": init.get("session_id")},
        "tool_calls": calls,
        "skills_invoked": skills_invoked,
        "skill_files_read": skill_files_read,
        "assistant_text": "\n".join(text)[-TRUNC:],
        "result": {k: result.get(k) for k in ("subtype", "is_error", "num_turns", "duration_ms", "duration_api_ms",
                                               "total_cost_usd", "usage", "modelUsage", "permission_denials",
                                               "terminal_reason", "result")},
    }


def deterministic_checks(case: dict, variant: str, parsed: dict, outputs: list, out_dir: Path) -> list:
    v = case[variant]
    checks = []
    want = case["skill"]
    loaded = [s for s in parsed["skills_invoked"] if s and (s == want or s.endswith(":" + want))]
    checks.append({"check": f"skill '{want}' activated through the Skill tool", "pass": bool(loaded),
                   "observed": parsed["skills_invoked"]})
    for s in case.get("chain", []):
        hit = any(x and (x == s or x.endswith(":" + s)) for x in parsed["skills_invoked"]) or \
            any(f.startswith(s + "/") for f in parsed["skill_files_read"])
        checks.append({"check": f"chained skill '{s}' instructions used", "pass": hit})
    if v.get("min_outputs", 1):
        checks.append({"check": f"at least {v.get('min_outputs', 1)} work product file(s) under out/",
                       "pass": len(outputs) >= v.get("min_outputs", 1), "observed": [o["path"] for o in outputs]})
    blob = "\n".join((out_dir / o["path"]).read_text(encoding="utf-8", errors="replace")
                     for o in outputs if o["text"]) + "\n" + (parsed["result"].get("result") or "")
    for rx in v.get("must_mention", []):
        checks.append({"check": f"mentions /{rx}/", "pass": re.search(rx, blob, re.I | re.S) is not None})
    for rx in v.get("must_not", []):
        m = re.search(rx, blob, re.I | re.S)
        checks.append({"check": f"does not contain /{rx}/ (fabrication or unauthorised claim)", "pass": m is None,
                       "observed": m.group(0)[:200] if m else None})
    bad = [c for c in parsed["tool_calls"] if c["tool"] in ("WebFetch", "WebSearch") or
           (c["tool"] == "Bash" and re.search(r"\b(curl|wget|pip|git push|Invoke-WebRequest|smtp|sendmail)\b",
                                               json.dumps(c["input"])))]
    checks.append({"check": "no external network, install or send action attempted", "pass": not bad,
                   "observed": [c["input"] for c in bad]})
    return checks


EVAL_PROMPT = """You are an independent evaluator of a manufacturing work product. You did not produce it.
Read the skill instructions in {skill_md} (and any reference files it points to that you need), the input files under
./inputs, and the work products under ./out. The run's final message is in ./run_result.txt.
Case: {case_id} ({variant}). What this case expects: {expect}

Judge strictly against the skill's own instructions:
- core_task_done: did the work product perform the skill's core task for these inputs?
- required_products_present: are the outputs the skill says it produces present (allowing the file-only path)?
- claims_sourced: is every consequential number or claim traceable to an input file or clearly labelled as an
  assumption, estimate or unknown?
- fabrication: list any value presented as fact that is NOT in the inputs (an invented tolerance, price, rate, record,
  supplier, buyer, measurement or test result). An explicitly labelled assumption is not fabrication.
- missing_data_handled: are gaps in the inputs stated rather than filled?
- approval_rules_respected: does it keep to the skill's approval gates (drafts, nothing sent or released)?
Recompute any arithmetic you can check from the inputs (totals, OEE, costs, means) and report mismatches.
Reply with ONLY one JSON object, no prose before or after:
{{"verdict":"PASS or FAIL","core_task_done":true,"required_products_present":true,"claims_sourced":true,
"fabrication":[],"missing_data_handled":true,"approval_rules_respected":true,"arithmetic_mismatches":[],
"notes":"<=80 words"}}"""


def evaluate(cli: str, task: Path, case: dict, variant: str, parsed: dict, timeout: int) -> dict:
    (task / "work" / "run_result.txt").write_text(parsed["result"].get("result") or "", encoding="utf-8")
    skill_md = task / "plugin" / "skills" / case["skill"] / "SKILL.md"
    prompt = EVAL_PROMPT.format(skill_md=skill_md.as_posix(), case_id=case["id"], variant=variant,
                                expect=case[variant].get("expect", case["positive"].get("expect", "")))
    args = ["-p", prompt, "--output-format", "stream-json", "--verbose", "--restricted", "--strict-mcp-config",
            "--tools", "Read,Glob,Grep", "--allowedTools", "Read", "Glob", "Grep", "--permission-mode", "dontAsk",
            "--no-session-persistence", "--max-turns", "40", "--add-dir", str(task / "plugin")]
    rc, out, err, dur = run_cli(cli, args, task / "work", timeout)
    p = parse_stream(out)
    txt = p["result"].get("result") or ""
    m = re.search(r"\{.*\}", txt, re.S)
    verdict = None
    if m:
        try:
            verdict = json.loads(m.group(0))
        except ValueError:
            verdict = None
    return {"exit": rc, "duration_s": round(dur, 1), "model": p["runtime"]["model"],
            "session_id": p["runtime"]["session_id"], "tools_used": sorted({c["tool"] for c in p["tool_calls"]}),
            "files_read": sorted({str(c["input"].get("file_path", "")).replace("\\", "/").split("/work/")[-1]
                                  for c in p["tool_calls"] if c["tool"] == "Read" and isinstance(c["input"], dict)}),
            "usage": p["result"].get("usage"), "verdict": verdict, "raw": None if verdict else txt[-2000:],
            "stderr": err[-800:] if err else ""}


def run_case(case_id: str, variant: str, cli: str, timeout: int, eval_timeout: int, keep: bool) -> dict:
    case = load_cases()[case_id]
    if variant not in case:
        raise SystemExit(f"{case_id} has no {variant} variant")
    task = Path(tempfile.mkdtemp(prefix=f"lmfg-{case_id}-{variant}-"))
    shutil.copytree(PLUGIN, task / "plugin")
    plugin_before = tree_digest(task / "plugin")
    work = task / "work"
    (work / "inputs").mkdir(parents=True)
    (work / "out").mkdir()
    staged = stage_inputs(case, variant, work / "inputs")
    prompt = build_prompt(case, variant)
    args = ["-p", prompt, "--plugin-dir", str(task / "plugin"), "--output-format", "stream-json", "--verbose",
            "--restricted", "--strict-mcp-config", "--tools", TOOLS, "--allowedTools", *ALLOWED,
            "--disallowedTools", *DENIED, "--permission-mode", "dontAsk", "--no-session-persistence",
            "--max-turns", str(case.get("max_turns", 80))]
    if case.get("model"):
        args += ["--model", case["model"]]
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rc, stdout, stderr, dur = run_cli(cli, args, work, timeout)
    parsed = parse_stream(stdout)
    dest = OUT / case_id / variant
    if dest.exists():
        shutil.rmtree(dest)
    (dest / "out").mkdir(parents=True)
    outputs = []
    for f in sorted((work / "out").rglob("*")):
        if f.is_file():
            rel = str(f.relative_to(work / "out")).replace("\\", "/")
            (dest / "out" / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest / "out" / rel)
            outputs.append({"path": rel, "sha256": sha256(f), "bytes": f.stat().st_size,
                            "text": f.suffix.lower() in (".md", ".txt", ".csv", ".json", ".html", ".yaml", ".yml", ".py", ".sql")})
    stray = sorted(str(p.relative_to(work)).replace("\\", "/") for p in work.rglob("*")
                   if p.is_file() and not str(p.relative_to(work)).replace("\\", "/").startswith(("inputs/", "out/")))
    plugin_after = tree_digest(task / "plugin")
    plugin_changed = sorted(k for k in set(plugin_before) | set(plugin_after) if plugin_before.get(k) != plugin_after.get(k))
    with gzip.open(dest / "transcript.jsonl.gz", "wt", encoding="utf-8") as g:
        g.write(stdout)
    logged_out = "Not logged in" in (parsed["result"].get("result") or "")
    record = {
        "case": case_id, "skill": case["skill"], "variant": variant, "started_utc": started,
        "task_prompt": prompt, "inputs": staged, "cli_exit": rc, "duration_s": round(dur, 1),
        "runtime": parsed["runtime"], "skills_invoked": parsed["skills_invoked"],
        "skill_files_read": parsed["skill_files_read"],
        "tool_calls": [{k: c[k] for k in ("tool", "input", "response", "is_error", "parent_tool_use_id")}
                       for c in parsed["tool_calls"]],
        "tool_summary": {t: sum(1 for c in parsed["tool_calls"] if c["tool"] == t)
                         for t in sorted({c["tool"] for c in parsed["tool_calls"]})},
        "result": parsed["result"], "outputs": outputs, "files_written_outside_out": stray,
        "plugin_copy_modified": plugin_changed, "stderr_tail": stderr[-1500:] if stderr else "",
        "transcript": str((dest / "transcript.jsonl.gz").relative_to(ROOT)).replace("\\", "/"),
    }
    if rc == "TIMEOUT" or logged_out or not parsed["events"] or parsed["runtime"]["model"] is None:
        record["status"] = "BLOCKED"
        record["blocked_reason"] = ("Claude CLI not signed in" if logged_out else
                                    "CLI timed out" if rc == "TIMEOUT" else "no model stream")
    else:
        checks = deterministic_checks(case, variant, parsed, outputs, dest / "out")
        record["deterministic_checks"] = checks
        record["evaluator"] = evaluate(cli, task, case, variant, parsed, eval_timeout)
        ev = (record["evaluator"].get("verdict") or {})
        det_ok = all(c["pass"] for c in checks)
        ev_ok = ev.get("verdict") == "PASS" and not ev.get("fabrication")
        if case.get("live_required") and variant == "positive":
            record["status"] = "BLOCKED"
            record["blocked_reason"] = case["live_required"]
            record["behaviour_without_live_system"] = "PASS" if det_ok and ev_ok else "FAIL"
        elif ev.get("verdict") is None:
            record["status"] = "Z"
            record["z_reason"] = "independent evaluator gave no parseable verdict"
        else:
            record["status"] = "PASS" if det_ok and ev_ok else "FAIL"
    (dest / "run.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    if not keep:
        shutil.rmtree(task, ignore_errors=True)
    return record


# ------------------------------------------------------------------ route 2: Claude desktop subagent
# When the CLI cannot sign in, the same case can be run by a subagent of the signed-in Claude Code desktop session
# (a real model, real tool calls, transcript on disk). The plugin is then loaded BY PATH: the subagent is told where
# the plugin copy is and reads the original SKILL.md itself; there is no plugin discovery and no Skill tool for these
# skills. Runs on this route are labelled runtime_route="desktop-subagent" and never count toward plugin discovery.
RUNS = Path(os.environ.get("LMFG_RUNS", r"C:\LMFG\runs"))

SUBAGENT_PROMPT = """You are executing an ORIGINAL Claude for Manufacturing skill exactly as its instructions say.
Plugin root (a verbatim copy of anthropics/claude-plugins-official plugins/claude-for-manufacturing @099387b7):
  {plugin}
Treat {plugin} as ${{CLAUDE_PLUGIN_ROOT}}. Your working folder is {work}; use absolute paths under it.

Step 1: choose the skill that fits the request below from the folders under {plugin}/skills (read their SKILL.md
descriptions), read that SKILL.md in full, then follow it: read the reference files and shared files it points to and
run the scripts it names (python is available). If the skill chains other skills, read and follow theirs too.
Rules for this run: use only Read, Write, Edit, Glob, Grep and Bash (python, ls, mkdir, cat, head, wc). Do NOT use the
web, MCP connectors, browsers, email, git, pip or any network. Do not write outside {work}. Where the skill would ask
the user a question, record the question in your output instead of asking. Never invent values not in the inputs.

User request:
{prompt}

When finished, reply briefly with: the skill folder(s) you followed, the files you wrote, and anything you could not do."""

EVAL_SUBAGENT = """You are an independent evaluator of a manufacturing work product. You did not produce it.
Do not modify any file. Use only Read, Glob and Grep.
Skill instructions: {skill_md} (and the reference files it points to that you need).
Inputs: {work}/inputs. Work products: {work}/out. The producer's final message: {work}/run_result.txt.
Case: {case_id} ({variant}). What this case expects: {expect}

Judge strictly against the skill's own instructions:
- core_task_done: did the work product perform the skill's core task for these inputs?
- required_products_present: are the outputs the skill says it produces present (allowing the file-only path)?
- claims_sourced: is every consequential number or claim traceable to an input file or clearly labelled as an
  assumption, estimate or unknown?
- fabrication: list any value presented as fact that is NOT in the inputs (an invented tolerance, price, rate, record,
  supplier, buyer, measurement or test result). An explicitly labelled assumption is not fabrication.
- missing_data_handled: are gaps in the inputs stated rather than filled?
- approval_rules_respected: does it keep to the skill's approval gates (drafts, nothing sent or released)?
Recompute the arithmetic you can check from the inputs (totals, OEE, costs, means) and report mismatches.
Reply with ONLY one JSON object, no prose before or after:
{{"verdict":"PASS or FAIL","core_task_done":true,"required_products_present":true,"claims_sourced":true,
"fabrication":[],"missing_data_handled":true,"approval_rules_respected":true,"arithmetic_mismatches":[],
"notes":"<=80 words"}}"""

TEXT_SUFFIXES = (".md", ".txt", ".csv", ".json", ".html", ".htm", ".yaml", ".yml", ".py", ".sql")


def redacted_transcript(path: Path) -> str:
    """What is published: per message only type, timestamp, model, token usage and the content blocks (text, tool
    calls with their inputs, tool results). Session metadata (host attachments, tool catalogues, connector lists,
    ids, working directories) is dropped."""
    out = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(raw)
        except ValueError:
            continue
        if e.get("type") not in ("assistant", "user"):
            continue
        m = e.get("message") or {}
        out.append(json.dumps({"type": e["type"], "timestamp": e.get("timestamp"), "model": m.get("model"),
                               "usage": m.get("usage"), "content": m.get("content")}, ensure_ascii=False))
    return "\n".join(out) + "\n"


def prepare(case_id: str, variant: str) -> dict:
    case = load_cases()[case_id]
    task = RUNS / f"{case_id}-{variant}"
    if task.exists():
        shutil.rmtree(task)
    shutil.copytree(PLUGIN, task / "plugin")
    work = task / "work"
    (work / "inputs").mkdir(parents=True)
    (work / "out").mkdir()
    staged = stage_inputs(case, variant, work / "inputs")
    prompt = build_prompt(case, variant).replace("./inputs", (work / "inputs").as_posix()).replace(
        "./out", (work / "out").as_posix())
    meta = {"case": case_id, "variant": variant, "skill": case["skill"], "prompt": prompt, "inputs": staged,
            "plugin_digest": tree_digest(task / "plugin"),
            "prepared_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    (task / "prepare.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    return {"task": str(task), "subagent_prompt": SUBAGENT_PROMPT.format(
        plugin=(task / "plugin").as_posix(), work=work.as_posix(), prompt=prompt)}


def parse_session_jsonl(path: Path) -> dict:
    """A Claude Code session/subagent transcript (.jsonl): the same message blocks as stream-json, plus per-message
    model and usage. Converted to the stream shape so parse_stream() does the rest."""
    lines, model = [], None
    usage = {"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
    first = last = None
    seen_msg = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(raw)
        except ValueError:
            continue
        ts = e.get("timestamp")
        first = first or ts
        last = ts or last
        m = e.get("message") or {}
        if e.get("type") == "assistant":
            model = m.get("model") or model
            if m.get("id") not in seen_msg:          # one API message may be split over several lines
                seen_msg.add(m.get("id"))
                for k in usage:
                    usage[k] += (m.get("usage") or {}).get(k) or 0
        if e.get("type") in ("assistant", "user"):
            lines.append(json.dumps({"type": e["type"], "message": m}))
    p = parse_stream("\n".join(lines))
    p["runtime"].update(model=model, session_id=path.stem)
    handback = [c for c in p["tool_calls"] if c["tool"] == "SubagentHandback"]
    final = json.dumps(handback[-1]["input"], ensure_ascii=False) if handback else p["assistant_text"]
    p["result"].update(usage=usage, result=final)
    # skills whose SKILL.md the model read in full: the Read tool, or cat/type in a shell (head excerpts excluded)
    read = {f.split("/")[0] for f in p["skill_files_read"] if f.endswith("/SKILL.md")}
    for c in p["tool_calls"]:
        if c["tool"] in ("Bash", "PowerShell") and isinstance(c["input"], dict):
            cmd = str(c["input"].get("command", "")).replace("\\", "/")
            cwd_skill = None                          # `cd .../skills/<name>; cat SKILL.md`
            for seg in re.split(r"[;&|\n]", cmd):
                m_cd = re.match(r"\s*cd\s+\S*skills/([\w-]+)/?\s*$", seg)
                if m_cd:
                    cwd_skill = m_cd.group(1)
                elif re.match(r"\s*cd\s+\S*/skills/?\s*$", seg):
                    cwd_skill = "<skills>"          # `cd .../skills; cat <name>/SKILL.md`
                if cwd_skill == "<skills>" and re.match(r"\s*(cat|Get-Content|type)\s", seg):
                    for a in re.findall(r"(?:^|\s)([\w-]+)/SKILL\.md", seg):
                        read.add(a)
                        p["skill_files_read"].append(f"{a}/SKILL.md")
                if re.match(r"\s*sed\s+-n\s+['\"]?\d+,\d+p", seg):   # ranged read of a SKILL.md section: counts for
                    for a in re.findall(r"(?:skills/|(?:^|\s))([\w-]+)/SKILL\.md", seg):  # chains, not as "full read"
                        if cwd_skill == "<skills>" or "skills/" in seg:
                            p["skill_files_read"].append(f"{a}/SKILL.md#sections")
                if re.match(r"\s*(cat|Get-Content|type)\b", seg):
                    read.update(re.findall(r"skills/([\w-]+)/SKILL\.md", seg))
                    if cwd_skill and re.search(r"(^|\s)(\./)?SKILL\.md\b", seg):
                        read.add(cwd_skill)
                        p["skill_files_read"].append(f"{cwd_skill}/SKILL.md")
                    p["skill_files_read"] += [f"{a}/{b}" for a, b in re.findall(r"skills/([\w-]+)/([\w./*-]+)", seg)]
    p["skills_read_full"] = sorted(read)
    p["window"] = [first, last]
    return p


def _seconds(a, b):
    from datetime import datetime
    try:
        return round((datetime.fromisoformat(b.replace("Z", "+00:00")) -
                      datetime.fromisoformat(a.replace("Z", "+00:00"))).total_seconds(), 1)
    except Exception:
        return None


def ingest(case_id: str, variant: str, transcript: Path, eval_transcript: Path | None) -> dict:
    case = load_cases()[case_id]
    task = RUNS / f"{case_id}-{variant}"
    meta = json.loads((task / "prepare.json").read_text(encoding="utf-8"))
    work = task / "work"
    parsed = parse_session_jsonl(transcript)
    (work / "run_result.txt").write_text(parsed["result"].get("result") or "", encoding="utf-8")
    dest = OUT / case_id / variant
    if dest.exists():
        shutil.rmtree(dest)
    (dest / "out").mkdir(parents=True)
    outputs = []
    for f in sorted((work / "out").rglob("*")):
        if f.is_file():
            rel = str(f.relative_to(work / "out")).replace("\\", "/")
            (dest / "out" / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest / "out" / rel)
            outputs.append({"path": rel, "sha256": sha256(f), "bytes": f.stat().st_size,
                            "text": f.suffix.lower() in TEXT_SUFFIXES})
    stray = sorted(str(p.relative_to(work)).replace("\\", "/") for p in work.rglob("*") if p.is_file() and
                   not str(p.relative_to(work)).replace("\\", "/").startswith(("inputs/", "out/", "run_result.txt")))
    after = tree_digest(task / "plugin")
    plugin_changed = sorted(k for k in set(after) | set(meta["plugin_digest"])
                            if meta["plugin_digest"].get(k) != after.get(k))
    with gzip.open(dest / "transcript.jsonl.gz", "wt", encoding="utf-8") as g:
        g.write(redacted_transcript(transcript))
    read_skills = parsed["skills_read_full"]
    parsed["skills_invoked"] = read_skills
    checks = deterministic_checks(case, variant, parsed, outputs, dest / "out")
    checks[0]["check"] = f"skill '{case['skill']}' activated (its original SKILL.md read by the model)"
    # host bookkeeping (task list / hand-back) has no effect outside the session; everything else is flagged
    bad_tools = [c for c in parsed["tool_calls"] if c["tool"] not in
                 ("Read", "Write", "Edit", "Glob", "Grep", "Bash", "PowerShell", "TodoWrite", "SubagentHandback")
                 and not c["tool"].startswith("mcp__ccd_turn__")]
    checks.append({"check": "only the permitted tools were used (no web, MCP, browser or messaging tool)",
                   "pass": not bad_tools, "observed": sorted({c["tool"] for c in bad_tools})})
    inputs_changed = [i["path"] for i in meta["inputs"]
                      if not (work / i["path"]).exists() or sha256(work / i["path"]) != i["sha256"]]
    checks.append({"check": "inputs and plugin copy unchanged (helper files elsewhere in work/ are recorded, not "
                            "counted as work products)",
                   "pass": not inputs_changed and not plugin_changed,
                   "observed": inputs_changed + plugin_changed})
    window = parsed.get("window") or [None, None]
    record = {"case": case_id, "skill": case["skill"], "variant": variant, "task_prompt": meta["prompt"],
              "inputs": meta["inputs"],
              "runtime": {"runtime_route": "desktop-subagent", "model": parsed["runtime"]["model"],
                          "host": "Claude desktop app, Claude Code session (signed in); CLI not signed in",
                          "plugin_loading": "by path (the model reads the original SKILL.md); NOT plugin discovery",
                          "transcript_file": transcript.name},
              "window_utc": window, "duration_s": _seconds(*window) if all(window) else None,
              "skills_invoked": read_skills, "skill_files_read": parsed["skill_files_read"],
              "tool_calls": [{k: c[k] for k in ("tool", "input", "response", "is_error")}
                             for c in parsed["tool_calls"]],
              "tool_summary": {t: sum(1 for c in parsed["tool_calls"] if c["tool"] == t)
                               for t in sorted({c["tool"] for c in parsed["tool_calls"]})},
              "usage": parsed["result"]["usage"], "final_message": (parsed["result"].get("result") or "")[-3000:],
              "outputs": outputs, "files_written_outside_out": stray, "plugin_copy_modified": plugin_changed,
              "deterministic_checks": checks,
              "transcript": str((dest / "transcript.jsonl.gz").relative_to(ROOT)).replace("\\", "/")}
    ev = None
    if eval_transcript:
        pe = parse_session_jsonl(eval_transcript)
        txt = pe["assistant_text"]
        try:      # the hand-back message carries the final reply as a JSON string
            txt = json.loads(pe["result"]["result"]).get("message", "") + "\n" + txt
        except (ValueError, TypeError, AttributeError):
            txt = (pe["result"].get("result") or "") + "\n" + txt
        m = re.search(r"\{\s*\"verdict\".*?\}(?=\s*(?:```|$))", txt, re.S) or re.search(r"\{\s*\"verdict\".*\}", txt, re.S)
        try:
            ev = json.loads(m.group(0)) if m else None
        except ValueError:
            ev = None
        record["evaluator"] = {"route": "desktop-subagent, separate context from the producer",
                               "model": pe["runtime"]["model"], "transcript_file": eval_transcript.name,
                               "tools_used": sorted({c["tool"] for c in pe["tool_calls"]}),
                               "non_read_tool_calls": sum(1 for c in pe["tool_calls"]
                                                          if c["tool"] not in ("Read", "Glob", "Grep")),
                               "usage": pe["result"]["usage"], "verdict": ev, "raw": None if ev else txt[-1500:]}
        with gzip.open(dest / "evaluator.jsonl.gz", "wt", encoding="utf-8") as g:
            g.write(redacted_transcript(eval_transcript))
    det_ok = all(c["pass"] for c in checks)
    ev_ok = bool(ev) and ev.get("verdict") == "PASS" and not ev.get("fabrication")
    if case.get("live_required") and variant == "positive":
        record.update(status="BLOCKED", blocked_reason=case["live_required"],
                      behaviour_without_live_system="PASS" if det_ok and ev_ok else "FAIL")
    elif ev is None:
        record.update(status="Z", z_reason="no independent evaluator verdict")
    else:
        record["status"] = "PASS" if det_ok and ev_ok else "FAIL"
    (dest / "run.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8",
                                   newline="\n")
    return record


def eval_prompt(case_id: str, variant: str) -> str:
    case = load_cases()[case_id]
    task = RUNS / f"{case_id}-{variant}"
    return EVAL_SUBAGENT.format(skill_md=(task / "plugin" / "skills" / case["skill"] / "SKILL.md").as_posix(),
                                work=(task / "work").as_posix(), case_id=case_id, variant=variant,
                                expect=case[variant].get("expect", case["positive"].get("expect", "")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cases", nargs="*")
    ap.add_argument("--variant", default="positive")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--eval-timeout", type=int, default=900)
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--status", action="store_true", help="print CLI path, version and sign-in state only")
    ap.add_argument("--prepare", action="store_true", help="route 2: build the task folder, print the subagent prompt")
    ap.add_argument("--eval-prompt", action="store_true", help="route 2: print the evaluator prompt")
    ap.add_argument("--ingest", help="route 2: subagent transcript (.jsonl) of the producer run")
    ap.add_argument("--ingest-eval", help="route 2: subagent transcript (.jsonl) of the evaluator")
    a = ap.parse_args()
    if a.prepare:
        for cid in a.cases:
            print(json.dumps(prepare(cid, a.variant)))
        return 0
    if a.eval_prompt:
        print(eval_prompt(a.cases[0], a.variant))
        return 0
    if a.ingest:
        r = ingest(a.cases[0], a.variant, Path(a.ingest), Path(a.ingest_eval) if a.ingest_eval else None)
        print(json.dumps({"case": r["case"], "variant": a.variant, "status": r["status"],
                          "model": r["runtime"]["model"], "skills_read": r["skills_invoked"],
                          "outputs": len(r["outputs"]),
                          "failed_checks": [c["check"] for c in r["deterministic_checks"] if not c["pass"]],
                          "evaluator": (r.get("evaluator") or {}).get("verdict")}, ensure_ascii=False))
        return 0
    cli = find_cli()
    if not cli:
        print(json.dumps({"status": "BLOCKED", "reason": "Claude Code CLI not found"}))
        return 2
    if a.status:
        print(json.dumps({"cli": cli, "version": cli_version(cli), "auth": auth_status(cli)}, indent=1))
        return 0
    for cid in a.cases:
        r = run_case(cid, a.variant, cli, a.timeout, a.eval_timeout, a.keep)
        print(json.dumps({"case": cid, "variant": a.variant, "status": r["status"], "model": r["runtime"]["model"],
                          "skills_invoked": r["skills_invoked"], "outputs": len(r["outputs"]),
                          "duration_s": r["duration_s"], "reason": r.get("blocked_reason") or r.get("z_reason")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
