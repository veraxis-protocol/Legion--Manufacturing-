"""Consumer gates from the upstream contracts' "Missing behavior for the consumer" tables, as LEGION consequence control.

Only rows whose behavior is **Blocks** are encoded, each with the contract and the exact row it comes from (the row
text must be found in the vendored file, so the gate cannot drift from upstream). A gate answers T (the consumer may
proceed) or Z (it must not, with the reasons); INV-07: VERDICT = Z => no consequential execution. A Degrades row is
not a gate: the consumer proceeds and states the limit.
"""
from __future__ import annotations

from manufacturing.contracts import upstream as U

GATES = {
    "geometry-estimate": [
        ("`approval.status` is `draft`", lambda r: (r.get("approval") or {}).get("status") == "draft",
         "rung 3 hours blocked: the estimate is unconfirmed"),
        ("`approval.status` is `declined`", lambda r: (r.get("approval") or {}).get("status") == "declined",
         "rung 3 hours blocked: declined at Gate 3"),
        ("`document_integrity.result` is `foreign_geometry`",
         lambda r: ((r.get("model") or {}).get("document_integrity") or {}).get("result") == "foreign_geometry",
         "the design step failed: no hours from this model"),
    ],
    "supplier-caused-flag": [
        ("`approval_state` is not `approved`", lambda r: r.get("approval_state") != "approved",
         "unapproved supplier-caused finding: no sourcing action"),
        ("`part_revision` absent", lambda r: not r.get("part_revision"), "the revision check cannot clear"),
        ("`supplier_id` absent", lambda r: not r.get("supplier_id"), "no determination without a named supplier"),
    ],
    "ncr": [
        ("`requirement_cited` null and `requirement_not_locatable` true",
         lambda r: r.get("requirement_cited") is None and r.get("requirement_not_locatable") is True,
         "no requirement cited: the 8D and customer pack are blocked"),
        ("`requirement_cited` null and the flag is false",
         lambda r: r.get("requirement_cited") is None and not r.get("requirement_not_locatable"),
         "no requirement cited and not flagged: producer error"),
        ("`approval_state` is not `approved`", lambda r: r.get("approval_state") != "approved",
         "anything customer-facing is blocked until approved"),
    ],
    "intake-form": [
        ("`bid_decision_state` is `declined`", lambda r: r.get("bid_decision_state") == "declined",
         "the estimator declined this inquiry"),
        ("`inquiry_state` is `superseded`", lambda r: r.get("inquiry_state") == "superseded",
         "a later revision of this inquiry exists"),
        ("`field_sources` absent", lambda r: not r.get("field_sources"), "no provenance to verify"),
    ],
    "downtime-record": [
        ("`safety_flagged` absent", lambda r: "safety_flagged" not in r, "safety unknown, never read as false"),
        ("`production_day` absent", lambda r: not r.get("production_day"), "cannot attribute the row to a day"),
    ],
}


def _missing_behavior_text(contract: str) -> str:
    text = U.load(contract).path.read_text(encoding="utf-8")
    return text.split("## Missing behavior", 1)[1] if "## Missing behavior" in text else ""


def verify_sources() -> list:
    """Every encoded row must appear in the upstream contract's missing-behavior table. Returns the misses."""
    miss = []
    for contract, rows in GATES.items():
        table = _missing_behavior_text(contract)
        for cond, _, _ in rows:
            if cond not in table:
                miss.append((contract, cond))
    return miss


def admit(contract: str, record: dict, purpose: str = "consume") -> dict:
    reasons = []
    for cond, test, why in GATES.get(contract, []):
        if test(record):
            reasons.append({"row": cond, "why": why})
    chk = U.check(record, U.load(contract))
    if chk["status"] == "BLOCK":
        reasons.append({"row": "Required field absent or invalid", "why": [b["field"] for b in chk["blocked"]] +
                        [e["field"] for e in chk["enum_violations"]]})
    return {"contract": contract, "purpose": purpose, "verdict": "Z" if reasons else "T", "reasons": reasons,
            "consequential_execution_allowed": not reasons}
