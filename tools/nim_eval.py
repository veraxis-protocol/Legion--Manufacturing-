"""WO-LMFG-004: independent evaluator on NVIDIA NIM (owner decision 2026-11-15: evaluator moved off Claude to save
Claude usage; the producer stays a real Claude Code CLI run).

The judge is a different model family from the producer (nvidia/nemotron-3.5-lightning-30b-a3b), so it is also
independent of it. It has no tools: the skill's SKILL.md, the input files, the work products and the producer's final
message are placed in the prompt (each file capped; any cap is recorded). It returns the same JSON verdict as the
Claude evaluator, so the PASS rule is unchanged.

The API key is read from a file (NVIDIA_API_KEY_FILE, default ~/Desktop/nvapi.txt) and is never printed, logged or
written to evidence. Inputs are synthetic test data only.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = os.environ.get("LMFG_NIM_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b")
KEY_FILE = Path(os.environ.get("NVIDIA_API_KEY_FILE", Path.home() / "Desktop" / "nvapi.txt"))
TEXT = (".md", ".txt", ".csv", ".json", ".html", ".htm", ".yaml", ".yml", ".py", ".sql", ".eml")
PER_FILE = 30000
TOTAL = 240000

SYSTEM = ("You are an independent evaluator of a manufacturing work product produced by another AI system. You did "
          "not produce it. Judge strictly against the skill instructions given. Reply with ONLY one JSON object.")

TASK = """Case: {case_id} ({variant}). What this case expects: {expect}

Judge strictly against the skill's own instructions (SKILL.md below):
- core_task_done: did the work product perform the skill's core task for these inputs?
- required_products_present: are the outputs the skill says it produces present (allowing the file-only path)?
- claims_sourced: is every consequential number or claim traceable to an input file or clearly labelled as an
  assumption, estimate or unknown?
- fabrication: list any value presented as fact that is NOT in the inputs (an invented tolerance, price, rate, record,
  supplier, buyer, measurement or test result). An explicitly labelled assumption is not fabrication. Values that the
  skill's own reference files or scripts define (formulas, default thresholds) are not fabrication.
- missing_data_handled: are gaps in the inputs stated rather than filled?
- approval_rules_respected: does it keep to the skill's approval gates (drafts, nothing sent or released)?
Recompute the arithmetic you can check from the inputs (totals, OEE, costs, means) and report mismatches.
Reply with ONLY one JSON object, no prose before or after:
{{"verdict":"PASS or FAIL","core_task_done":true,"required_products_present":true,"claims_sourced":true,
"fabrication":[],"missing_data_handled":true,"approval_rules_respected":true,"arithmetic_mismatches":[],
"notes":"<=80 words"}}

{material}"""


def available() -> bool:
    return KEY_FILE.exists() and KEY_FILE.stat().st_size > 10


def _files(root: Path, label: str, budget: list, given: list) -> str:
    parts = []
    for f in sorted(root.rglob("*")):
        if not f.is_file():
            continue
        rel = f"{label}/{f.relative_to(root).as_posix()}"
        data = f.read_bytes()
        entry = {"file": rel, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
        if f.suffix.lower() not in TEXT:
            entry["given"] = "name only (binary)"
            parts.append(f"=== {rel} (binary, {len(data)} bytes, content not shown)")
        else:
            txt = data.decode("utf-8", "replace")
            cap = min(PER_FILE, max(budget[0], 0))
            entry["given"] = "full" if len(txt) <= cap else f"first {cap} of {len(txt)} chars"
            parts.append(f"=== {rel}\n{txt[:cap]}" + ("\n[... truncated ...]" if len(txt) > cap else ""))
            budget[0] -= min(len(txt), cap)
        given.append(entry)
    return "\n\n".join(parts)


def material(task: Path, case: dict) -> tuple[str, list]:
    skill_dir = task / "plugin" / "skills" / case["skill"]
    budget, given = [TOTAL], []
    skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    budget[0] -= len(skill_md)
    given.append({"file": f"skills/{case['skill']}/SKILL.md", "given": "full"})
    work = task / "work"
    out = _files(work / "out", "out", budget, given)
    inp = _files(work / "inputs", "inputs", budget, given)
    final = (work / "run_result.txt").read_text(encoding="utf-8", errors="replace") \
        if (work / "run_result.txt").exists() else ""
    text = (f"##### SKILL.md ({case['skill']})\n{skill_md}\n\n##### WORK PRODUCTS (./out)\n{out or '(none)'}\n\n"
            f"##### INPUT FILES (./inputs)\n{inp}\n\n##### PRODUCER FINAL MESSAGE\n{final[:PER_FILE]}")
    return text, given


def _post(body: dict, timeout: int) -> dict:
    key = KEY_FILE.read_text(encoding="utf-8").strip()
    req = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode("utf-8"), method="POST",
                                 headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                                          "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def evaluate(task: Path, case: dict, variant: str, final_message: str, timeout: int = 900) -> tuple[dict, list]:
    """Returns (evaluator record, redacted transcript lines)."""
    (task / "work" / "run_result.txt").write_text(final_message or "", encoding="utf-8")
    mat, given = material(task, case)
    prompt = TASK.format(case_id=case["id"], variant=variant, material=mat,
                         expect=case[variant].get("expect", case["positive"].get("expect", "")))
    t0 = time.time()
    attempts = []
    # 1st: with reasoning (better arithmetic checking). If the reasoning uses up the output budget and no verdict is
    # returned, 2nd: same prompt with reasoning disabled. The mode that produced the verdict is recorded.
    for mode, extra in (("reasoning", {"max_tokens": 32768}),
                        ("no-reasoning", {"max_tokens": 4096, "chat_template_kwargs": {"enable_thinking": False}})):
        body = {"model": MODEL, "temperature": 0.0, **extra,
                "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}]}
        resp, err, txt = None, None, ""
        for attempt in range(3):
            try:
                resp = _post(body, timeout)
                break
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                err = f"{type(e).__name__}: {getattr(e, 'code', '')} {str(e)[:200]}"
                time.sleep(10 * (attempt + 1))
        if resp:
            txt = ((resp.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
        verdict = None
        body_txt = re.sub(r"<think>.*?</think>", "", txt, flags=re.S)
        for m in reversed(list(re.finditer(r"\{(?:[^{}]|\{[^{}]*\})*\}", body_txt, re.S))):
            try:
                cand = json.loads(m.group(0))
            except ValueError:
                continue
            if isinstance(cand, dict) and "verdict" in cand:
                verdict = cand
                break
        attempts.append({"mode": mode, "usage": (resp or {}).get("usage"), "verdict_returned": verdict is not None,
                         "error": err if not resp else None})
        if verdict is not None:
            break
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    usage = (resp or {}).get("usage")
    transcript = [json.dumps({"type": "user", "timestamp": ts, "model": None, "usage": None,
                              "content": [{"type": "text", "text": SYSTEM + "\n\n" + prompt}]}, ensure_ascii=False),
                  json.dumps({"type": "assistant", "timestamp": ts, "model": (resp or {}).get("model", MODEL),
                              "usage": usage, "content": [{"type": "text", "text": txt}]}, ensure_ascii=False)]
    rec = {"engine": "nvidia-nim", "endpoint": ENDPOINT, "model": (resp or {}).get("model", MODEL),
           "duration_s": round(time.time() - t0, 1), "usage": usage, "attempts": attempts,
           "verdict_mode": attempts[-1]["mode"] if verdict is not None else None, "material_given": given,
           "tools_used": [], "verdict": verdict, "raw": None if verdict else txt[-2000:], "error": err if not resp else None}
    return rec, transcript


if __name__ == "__main__":
    # connectivity probe only: prints status, never the key
    r = _post({"model": MODEL, "max_tokens": 512, "messages": [{"role": "user", "content": 'Reply {"ok":true}'}]}, 120)
    print(json.dumps({"model": r.get("model"), "content": (r["choices"][0]["message"].get("content") or "")[-200:],
                      "usage": r.get("usage")}))
