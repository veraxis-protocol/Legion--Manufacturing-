"""Read Anthropic's handoff contracts (upstream/.../shared/contracts/*.md) as data, and check records against them.

Nothing here restates a contract. The field tables, the missing behavior of each field and the worked examples are
parsed from the vendored Markdown at run time, and every result carries the SHA-256 of the contract file it was
checked against, so a change upstream changes the result instead of being silently ignored.

Behaviors (contracts/README.md, rule 2): Required -> the consumer blocks; Degrades -> it proceeds and states the
limit; Optional -> no comment. "Guess" and "default silently" are not behaviors, so this module never fills a value.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = ROOT / "upstream" / "claude-for-manufacturing" / "shared" / "contracts"

_TICK = re.compile(r"`([^`]+)`")


@dataclass
class Field:
    name: str                 # dotted, e.g. "approval.status", "datums[].basis"
    type: str
    behavior: str             # Required | Degrades | Optional | Conditional (text kept in behavior_text)
    behavior_text: str
    notes: str
    section: str
    line: int
    enum: tuple = ()
    part: str = ""            # the "## " heading the field sits under (a contract may define two record kinds)

    @property
    def nullable(self) -> bool:
        return "null" in self.type.lower()


@dataclass
class Contract:
    name: str
    path: Path
    sha256: str
    version: int | None
    emitted_by: str
    consumed_by: str
    fields: list = field(default_factory=list)
    examples: list = field(default_factory=list)   # [(start_line, end_line, lang, text)]

    def field(self, name):
        return next((f for f in self.fields if f.name == name), None)


def _cells(line: str) -> list:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _enum_from_notes(type_: str, notes: str) -> tuple:
    if "enum" not in type_.lower():
        return ()
    first = notes.split(". ")[0].rstrip(".")
    toks = _TICK.findall(first)
    rest = _TICK.sub("", first).replace(",", "").replace(" or ", "").replace("and", "").strip()
    return tuple(toks) if toks and not rest else ()


def load(name: str) -> Contract:
    path = CONTRACTS_DIR / f"{name}.md"
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    lines = text.split("\n")
    head = "\n".join(lines[:15])
    ver = re.search(r"\*\*Contract version\*\*\s+(\d+)", head)
    emit = re.search(r"\*\*Emitted by\*\*\s+(.+)", head)
    cons = re.search(r"\*\*Consumed by\*\*\s+(.+)", head)
    c = Contract(name, path, hashlib.sha256(raw).hexdigest(), int(ver.group(1)) if ver else None,
                 emit.group(1).strip() if emit else "", cons.group(1).strip() if cons else "")
    section, part, cols, in_code = "", "", None, None
    for i, line in enumerate(lines, 1):
        if line.startswith("```"):
            if in_code is None:
                in_code = (i, line[3:].strip())
            else:
                c.examples.append((in_code[0], i, in_code[1], "\n".join(lines[in_code[0]:i - 1])))
                in_code = None
            continue
        if in_code is not None:
            continue
        if line.startswith("#"):
            section, cols = line.lstrip("#").strip(), None
            if line.startswith("## "):
                part = section
            continue
        if not line.startswith("|"):
            cols = None
            continue
        cells = _cells(line)
        if cols is None:
            if cells and cells[0] in ("Field", "Column") and "Behavior" in cells:
                cols = cells
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        row = dict(zip(cols, cells + [""] * (len(cols) - len(cells))))
        names = _TICK.findall(row.get(cols[0], ""))
        btxt = row.get("Behavior", "")
        b = btxt.replace("*", "").split(".")[0].strip()
        if b.startswith("Required when"):
            beh = "Conditional"
        elif b.startswith("Required"):
            beh = "Required"
        elif b.startswith("Degrades"):
            beh = "Degrades"
        elif b.startswith("Optional"):
            beh = "Optional"
        else:
            beh = "Unparsed"
        prefix = ""
        m = re.match(r"`([a-z_]+)`$", section)
        if m:                                        # "### `document_integrity`" nests its fields
            prefix = m.group(1) + "."
        for n in names:
            full = n if ("." in n or "[" in n or not prefix) else prefix + n
            c.fields.append(Field(full, row.get("Type", ""), beh, btxt, row.get("Notes", ""), section, i,
                                  _enum_from_notes(row.get("Type", ""), row.get("Notes", "")), part))
    return c


def all_contract_names() -> list:
    return sorted(p.stem for p in CONTRACTS_DIR.glob("*.md") if p.stem != "README")


def worked_examples(c: Contract) -> list:
    """Every YAML document in the contract's examples, parsed, each with its source location."""
    import yaml  # pinned in DEPENDENCY_LOCK; the only non-stdlib import, used to read upstream examples verbatim
    out = []
    for start, end, lang, body in c.examples:
        if lang != "yaml":
            continue
        for k, doc in enumerate(yaml.safe_load_all(body)):
            if isinstance(doc, dict):
                out.append({"record": doc, "source": {"file": str(c.path.relative_to(ROOT)).replace("\\", "/"),
                                                      "lines": [start, end], "document": k,
                                                      "contract_sha256": c.sha256}})
    return out


def worked_example(c: Contract):
    """The largest YAML example document (the complete worked record). None if the contract has none."""
    docs = worked_examples(c)
    return max(docs, key=lambda d: len(d["record"])) if docs else None


def part_of(record: dict, c: Contract) -> str:
    """Which record kind (## part) a record is, by the most top-level field names it shares with that part."""
    parts = {}
    for f in c.fields:
        parts.setdefault(f.part, set()).add(f.name.split(".")[0].replace("[]", ""))
    return max(parts, key=lambda p: len(parts[p] & set(record)))


# --- checking a record --------------------------------------------------------------------------------------------

_MISSING = object()


def _lookup(record, dotted: str):
    """Values at a dotted path; '[]' fans out over a list. Returns a list of values (_MISSING where absent)."""
    parts = dotted.replace("[]", ".[]").split(".")
    vals = [record]
    for p in parts:
        nxt = []
        for v in vals:
            if p == "[]":
                nxt.extend(v if isinstance(v, list) else [_MISSING])
            elif isinstance(v, dict):
                nxt.append(v.get(p, _MISSING))
            else:
                nxt.append(_MISSING)
        vals = nxt
    return vals


def _find_anywhere(record, key: str):
    """For a flat field name whose nesting the contract does not spell out: every value stored under that key."""
    out = []
    if isinstance(record, dict):
        for k, v in record.items():
            if k == key:
                out.append(v)
            out.extend(_find_anywhere(v, key))
    elif isinstance(record, list):
        for v in record:
            out.extend(_find_anywhere(v, key))
    return out


def check(record: dict, c: Contract, fields: list | None = None, part: str | None = None) -> dict:
    """Field-level check. Returns {status, blocked, degraded, enum_violations, contract, contract_sha256}.

    status: BLOCK when a Required field is absent (or null where the type does not allow null) or an enum value is
    outside the contract's set; DEGRADED when only Degrades fields are absent or null; OK otherwise.
    Nothing is filled in: the record is returned untouched by the caller.
    """
    blocked, degraded, bad_enum = [], [], []
    if fields is None:
        part = part if part is not None else part_of(record, c)
        multi = len({f.part for f in c.fields}) > 1 and any(f.part.lower().startswith("the ") for f in c.fields)
        fields = [f for f in c.fields if not multi or f.part == part]
    for f in fields:
        if f.behavior not in ("Required", "Degrades"):
            # Optional and conditional fields are not required, but a value that is present must still be one the
            # contract allows
            if f.enum and "." not in f.name and "[" not in f.name and record.get(f.name) is not None \
                    and not isinstance(record[f.name], (dict, list)) and str(record[f.name]) not in f.enum:
                bad_enum.append({"field": f.name, "value": record[f.name], "allowed": list(f.enum),
                                 "contract_line": f.line})
            continue
        base = f.name.split(".")[-1].replace("[]", "")
        if "." in f.name or "[" in f.name:
            vals = _lookup(record, f.name)
            if f.name.split(".")[0].replace("[]", "") not in record:
                vals = _find_anywhere(record, base) or [_MISSING]
        elif f.name not in record and isinstance(record.get(f.part.lower().split(" ")[0]), list):
            # a table under "## Features" describes each row of record["features"]: checked per row, and an
            # empty list has no rows to check (whether the list may be empty is the list field's own behavior)
            vals = [el.get(f.name, _MISSING) if isinstance(el, dict) else _MISSING
                    for el in record[f.part.lower().split(" ")[0]]]
        else:
            vals = [record[f.name]] if f.name in record else (_find_anywhere(record, f.name) or [_MISSING])
        for v in vals:
            if v is _MISSING or (v is None and not f.nullable):
                (blocked if f.behavior == "Required" else degraded).append(
                    {"field": f.name, "why": "absent" if v is _MISSING else "null", "contract_line": f.line,
                     "behavior": f.behavior_text})
                break
            if v is None and f.behavior == "Degrades":
                degraded.append({"field": f.name, "why": "null", "contract_line": f.line, "behavior": f.behavior_text})
                break
            if f.enum and v is not None and not isinstance(v, (dict, list)) and str(v) not in f.enum:
                bad_enum.append({"field": f.name, "value": v, "allowed": list(f.enum), "contract_line": f.line})
    status = "BLOCK" if blocked or bad_enum else ("DEGRADED" if degraded else "OK")
    return {"status": status, "part": part, "blocked": blocked, "degraded": degraded, "enum_violations": bad_enum,
            "contract": c.name, "contract_version": c.version, "contract_sha256": c.sha256}


def csv_examples(c: Contract) -> dict:
    """The CSV worked examples (```-fenced, no language) as {tab: [row dicts]}, each row with its source lines.

    Upstream wraps long CSV lines in the Markdown: a header or a row continues until a blank line, so wrapped lines
    are joined before parsing. Values are kept as written (strings); nothing is converted.
    """
    import csv
    import io
    out = {}
    for start, end, lang, body in c.examples:
        if lang:
            continue
        tab, groups, cur, cur_start = None, [], [], None
        lines = body.split("\n")
        for k, line in enumerate(lines + [""]):
            ln = start + 1 + k
            if line.startswith("# "):
                if cur:
                    groups.append((tab, cur_start, cur))
                tab, cur = line[2:].strip(), []
                continue
            if not line.strip():
                if cur:
                    groups.append((tab, cur_start, cur))
                cur = []
                continue
            if not cur:
                cur_start = ln
            cur.append(line.strip())
        header = {}
        for tab, ln, parts in groups:
            text = "".join(parts)
            if tab not in header:
                header[tab] = next(csv.reader(io.StringIO(text)))
                continue
            vals = next(csv.reader(io.StringIO(text)))
            row = dict(zip(header[tab], vals))
            row["_source"] = {"file": str(c.path.relative_to(ROOT)).replace("\\", "/"), "line": ln,
                              "contract_sha256": c.sha256}
            out.setdefault(tab, []).append(row)
    return out
