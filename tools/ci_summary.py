"""Render an evidence JSON file as a GitHub job summary (Markdown) so results are readable without signing in.

  python3 -I tools/ci_summary.py evidence/<file>.json >> "$GITHUB_STEP_SUMMARY"

Prints the artifact header, status and counts, every check row (when present) and, at the end, the full JSON.
A missing file is reported, not hidden.
"""
import json
import pathlib
import sys


def main(path: str) -> int:
    p = pathlib.Path(path)
    print(f"## `{p.name}`\n")
    if not p.exists():
        print("**MISSING**: the evidence file was not produced (the step before failed early).")
        return 0
    d = json.loads(p.read_text(encoding="utf-8"))
    print(f"**Status: {d.get('status')}**  ")
    print(f"source_commit `{d.get('source_commit')}` · executed_at_utc {d.get('executed_at_utc')} · "
          f"python {d.get('environment', {}).get('python')} on {d.get('environment', {}).get('platform')}  ")
    print(f"command: `{d.get('command')}`\n")
    if d.get("counts"):
        print("| count | value |\n|---|---|")
        for k, v in d["counts"].items():
            print(f"| {k} | {v} |")
        print()
    if d.get("checks"):
        print("| status | check | note |\n|---|---|---|")
        for c in d["checks"]:
            note = c.get("upstream_defect") or (f"self-checks {c['self_checks']}" if c.get("self_checks") else "")
            print(f"| {c['status']} | `{c['id']}` | {note or ''} |")
        print()
    if isinstance(d.get("skills"), list) and d["skills"] and isinstance(d["skills"][0], dict) \
            and "verdict" in d["skills"][0]:          # the per-skill matrix (Phase A files use "skills" differently)
        print("| id | skill | mode | verdict | PASS | FAIL | NOT RUN | BLOCKED |\n|---|---|---|---|---|---|---|---|")
        for s in d["skills"]:
            c = s["counts"]
            print(f"| {s['id']} | `{s['skill']}` | {s['mode']} | {s['verdict']} | {c.get('PASS', 0)} | "
                  f"{c.get('FAIL', 0) + c.get('ERROR', 0)} | {c.get('NOT_RUN', 0)} | {c.get('BLOCKED', 0)} |")
        print()
    if d.get("modules"):
        print("| module | results |\n|---|---|")
        for m, c in d["modules"].items():
            print(f"| `{m}` | {c} |")
        print()
    if d.get("systems"):
        print("| system | live | first reason |\n|---|---|---|")
        for name, s in d["systems"].items():
            print(f"| {name} | {s['live']} | {s['live_tests'][0]['reason'][:160]} |")
        print()
    if d.get("repositories"):
        print("| status | repository | pinned | remote HEAD |\n|---|---|---|---|")
        for r in d["repositories"]:
            print(f"| {r['status']} | {r['repository']} | `{r['pinned'][:12]}` | `{(r['remote_head'] or '-')[:12]}` |")
        print()
    print("<details><summary>Full evidence JSON</summary>\n\n```json")
    print(json.dumps(d, indent=1, ensure_ascii=False)[:60000])
    print("```\n</details>")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
