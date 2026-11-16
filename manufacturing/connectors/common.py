"""Shared pieces of the four connector adapters: a counted, read-only transport wrapper and dataset-row building.

A transport is the provider's own interface (an MCP tool call, a REST request). In contract tests it is a recorded
or scripted stand-in; in live acceptance it is the real client. The adapters never know which, so the code tested
here is the code that runs live. Contract-test results are never reported as connectivity (INV-03).
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

from manufacturing.connectors.lifecycle import Lifecycle, WriteRefused


class CallLog:
    """Every call the adapter made, so a test can prove which calls were (and were not) issued."""

    def __init__(self):
        self.calls = []

    def add(self, kind, name, args):
        self.calls.append({"kind": kind, "name": name, "args": args})

    @property
    def writes(self):
        return [c for c in self.calls if c["kind"] == "write"]


class Adapter:
    system = "base"
    source_system = "manual"

    def __init__(self, transport, profile_scope: dict, clock=None):
        self.transport = transport
        self.profile_scope = dict(profile_scope or {})
        self.lc = Lifecycle(self.system, **({"clock": clock} if clock else {}))
        self.log = CallLog()

    def refuse_write(self, name, args=None):
        self.log.add("refused", name, args)
        raise WriteRefused(f"{self.system}: {name} is not a documented read; nothing was called")


def iso(dt_or_str) -> str:
    if isinstance(dt_or_str, datetime):
        return dt_or_str.isoformat()
    return str(dt_or_str)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def base_row(site: str, source_system: str, source_ref: str, as_of: str | None) -> dict:
    """The columns every consolidated-dataset row carries, except join_status/mismatch_class.

    join_status is assigned by data-consolidate's join (contracts/consolidated-dataset.md); a connector pull is
    pre-join, so the adapter does not set it rather than claim a join it did not perform.
    """
    row = {"site": site, "source_system": source_system, "source_ref": source_ref}
    row["as_of"] = as_of  # None stays None: "when the source recorded it", never the read time
    return row


def key_pair(row: dict, key: str, verbatim):
    """Rule 3: the normalized and the verbatim form. The ladder belongs to data-consolidate, so the pull keeps the
    source value in both until the join normalizes it; the verbatim column is never rewritten."""
    if verbatim is None or str(verbatim).strip() == "":
        row[key] = None
        row[key + "_verbatim"] = None
    else:
        row[key + "_verbatim"] = verbatim
        row[key] = str(verbatim).strip()
    return row


_YMD = re.compile(r"^\d{8}$")
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_date(value):
    """M3 writes YYYYMMDD and YYYY-MM-DD, sometimes in one record (shared/erp-connectors.md, Reading M3 output 2)."""
    if value in (None, "", 0, "0"):
        return None
    s = str(value).strip()
    if _YMD.match(s):
        return f"{s[:4]}-{s[4:6]}-{s[6:]}"
    if _ISO.match(s):
        return s
    raise ValueError(f"unrecognised date {value!r}")


def number_or_none(v):
    if v is None or (isinstance(v, str) and v.strip() == ""):
        return None
    return float(v) if not isinstance(v, (int, float)) else v
