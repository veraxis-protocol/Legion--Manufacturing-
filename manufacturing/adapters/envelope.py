"""WO-B05: the LEGION envelope around an upstream contract record.

The upstream record is carried unchanged (contracts/README.md rule 1: no transformation step in between). LEGION adds
only what the upstream schema has no home for, beside the record and never inside it:

  source_bindings   which system, tenant and record each value came from, verbatim, with when it was read
  permission_scope  the tenant and the read scopes the values were obtained under; it can only narrow
  verification      the contract check result and the connector state at the time of the read

Rules enforced here (WO-LMFG-001 WO-B05):
  - the record's canonical hash is fixed at wrap time; any later change to it is detected (no silent transformation)
  - envelopes from different tenants never merge (tenant isolation)
  - every transformation carries the scope forward as the intersection of its inputs (scope survives)
  - a missing value stays missing: wrap() never fills, and absent() records why a value is absent
  - a source that is not VERIFIED yields an UNAVAILABLE envelope, never an empty success
"""
from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone

from manufacturing.contracts import upstream as U

SCHEMA = "legion.manufacturing.envelope.v1"


class EnvelopeError(ValueError):
    pass


class TenantIsolationError(EnvelopeError):
    pass


def canonical_sha256(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                                     default=str).encode("utf-8")).hexdigest()


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def binding(field_path: str, system: str, tenant: str, record_ref: str, verbatim, retrieved_at: str | None = None):
    """One source binding: where the value at field_path came from, as the source system wrote it."""
    if not (field_path and system and tenant and record_ref):
        raise EnvelopeError("a source binding needs field_path, system, tenant and record_ref")
    return {"field_path": field_path, "system": system, "tenant": tenant, "record_ref": record_ref,
            "verbatim": verbatim, "retrieved_at": retrieved_at or _now()}


def scope(tenant: str, scopes, mode: str = "read") -> dict:
    if mode != "read":
        raise EnvelopeError("LEGION Manufacturing reads only; a write scope is never granted by an adapter")
    return {"tenant": tenant, "scopes": sorted(set(scopes)), "mode": "read"}


def wrap(contract_name: str, record: dict, bindings: list, permission_scope: dict, connector_state: str = "VERIFIED",
         part: str | None = None) -> dict:
    """Envelope an upstream-shaped record. The record is deep-copied and never modified."""
    if connector_state != "VERIFIED":
        return unavailable(contract_name, permission_scope, connector_state)
    tenants = {b["tenant"] for b in bindings} | {permission_scope["tenant"]}
    if len(tenants) != 1:
        raise TenantIsolationError(f"bindings span tenants {sorted(tenants)}")
    c = U.load(contract_name)
    rec = copy.deepcopy(record)
    return {"schema": SCHEMA, "status": "AVAILABLE",
            "upstream_contract": {"name": c.name, "version": c.version, "sha256": c.sha256},
            "record": rec, "record_sha256": canonical_sha256(rec),
            "legion": {"source_bindings": list(bindings), "permission_scope": dict(permission_scope),
                       "verification": {"contract_check": U.check(rec, c, part=part),
                                        "connector_state": connector_state, "checked_at": _now()},
                       "absent": []}}


def unavailable(contract_name: str, permission_scope: dict, state: str) -> dict:
    """A disconnected, expired or unscoped source: no record at all, and a status that cannot be read as success."""
    return {"schema": SCHEMA, "status": "UNAVAILABLE", "upstream_contract": {"name": contract_name},
            "record": None, "record_sha256": None,
            "legion": {"source_bindings": [], "permission_scope": dict(permission_scope),
                       "verification": {"connector_state": state, "checked_at": _now()}, "absent": []}}


def absent(env: dict, field_path: str, why: str) -> dict:
    """Record that a value is absent and why. The record itself is not touched; nothing is filled."""
    env["legion"]["absent"].append({"field_path": field_path, "why": why})
    return env


def verify_unchanged(env: dict) -> bool:
    return env["record"] is None or canonical_sha256(env["record"]) == env["record_sha256"]


def combine(envs: list, into_contract: str, record: dict, extra_bindings: list = ()) -> dict:
    """A transformation that builds one record from several envelopes (e.g. connector rows -> one dataset row).

    Refuses inputs from more than one tenant, refuses any UNAVAILABLE input, carries every input binding forward
    and narrows the scope to what every input was read under.
    """
    if not envs:
        raise EnvelopeError("nothing to combine")
    if any(e["status"] != "AVAILABLE" for e in envs):
        raise EnvelopeError("an input is UNAVAILABLE; a combined record would hide that")
    tenants = {e["legion"]["permission_scope"]["tenant"] for e in envs}
    if len(tenants) != 1:
        raise TenantIsolationError(f"inputs span tenants {sorted(tenants)}")
    for e in envs:
        if not verify_unchanged(e):
            raise EnvelopeError("an input record was modified after it was wrapped")
    common = set(envs[0]["legion"]["permission_scope"]["scopes"])
    for e in envs[1:]:
        common &= set(e["legion"]["permission_scope"]["scopes"])
    bindings = [b for e in envs for b in e["legion"]["source_bindings"]] + list(extra_bindings)
    out = wrap(into_contract, record, bindings, scope(tenants.pop(), common))
    out["legion"]["derived_from"] = [e["record_sha256"] for e in envs]
    return out
