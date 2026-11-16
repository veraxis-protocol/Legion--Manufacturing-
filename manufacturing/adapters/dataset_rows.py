"""Check a connector-pulled row against upstream contracts/consolidated-dataset.md (contract version 6).

The columns, key pairs and their behaviors are read from the contract file. A pull is pre-join, so join_status and
mismatch_class and the integrity results (set by data-consolidate's join and checks) are reported as "assigned at join", not as missing. Two situations
come straight from the contract's "Missing behavior for the consumer" table:
  - as_of that cannot be resolved -> Degrades: usable for counting, not for correlating
  - a qty without uom -> Degrades: reported, never aggregated
"""
from __future__ import annotations

from manufacturing.contracts import upstream as U

TAB_KEYS = {
    "parts": ["part_number"], "inventory": ["part_number"], "purchase_orders": ["part_number", "supplier_id"],
    "production_work_orders": ["production_wo", "part_number"], "sales_orders": ["sales_order", "part_number"],
    "operation_actuals": ["production_wo", "part_number"], "lots": ["lot_number"], "assets": ["asset_id"],
    "suppliers": ["supplier_id"],
}
ASSIGNED_AT_JOIN = ("join_status", "mismatch_class", "contradicted_by", "integrity_flags")


def check_pull_row(row: dict, tab: str) -> dict:
    c = U.load("consolidated-dataset")
    every = [f for f in c.fields if f.part == "Columns every row carries" and f.name not in ASSIGNED_AT_JOIN
             and f.name != "as_of"]
    keys = [f for f in c.fields if f.part == "Join-key columns"
            and f.name.replace("_verbatim", "") in TAB_KEYS.get(tab, [])]
    for f in keys:
        f.behavior = "Required"          # "Required on any tab keyed by ..." for the tabs listed in TAB_KEYS
    res = U.check(row, c, fields=every + keys, part="Columns every row carries")
    if row.get("as_of") in (None, ""):
        res["degraded"].append({"field": "as_of", "why": "unresolved",
                                "behavior": "Degrades: usable for counting and not for correlating "
                                            "(consolidated-dataset.md, Missing behavior for the consumer)"})
    if row.get("qty") is not None and not row.get("uom"):
        res["degraded"].append({"field": "uom", "why": "absent beside qty",
                                "behavior": "Degrades: report the quantity, refuse to aggregate it, say why"})
    if row.get("amount") is not None and not row.get("currency"):
        res["blocked"].append({"field": "currency", "why": "absent beside amount",
                               "behavior": "Required alongside any amount"})
    for k in TAB_KEYS.get(tab, []):
        if k in row and (k + "_verbatim") not in row:
            res["blocked"].append({"field": k + "_verbatim", "why": "rule 3: a key is a pair"})
    res["assigned_at_join"] = list(ASSIGNED_AT_JOIN)
    res["status"] = "BLOCK" if res["blocked"] or res["enum_violations"] else (
        "DEGRADED" if res["degraded"] else "OK")
    return res


def can_aggregate(rows: list) -> dict:
    """Rule 5: flag differing UOMs, do not silently sum. Returns the total only when it is a total."""
    uoms = {r.get("uom") for r in rows if r.get("qty") is not None}
    if None in uoms:
        return {"total": None, "why": "a quantity has no uom; not aggregated"}
    if len(uoms) > 1:
        return {"total": None, "why": f"differing uoms {sorted(uoms)}; not summed"}
    return {"total": sum(r["qty"] for r in rows if r.get("qty") is not None), "uom": uoms.pop() if uoms else None}
