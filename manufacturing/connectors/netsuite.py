"""WO-B03: Oracle NetSuite, read-only, over NetSuite's own REST interfaces (record service and SuiteQL).

Record types and rules come from upstream `shared/erp-connectors.md` and `contracts/consolidated-dataset.md`:
  - record types: item, assemblyitem, inventorynumber, location, workorder, salesorder, itemfulfillment,
    purchaseorder, itemreceipt, vendor (the "NetSuite" column of the Record by record table, parsed at import)
  - scope by subsidiary and location; the account id is the tenant
  - sales order and fulfilment lines are signed negative in NetSuite: read as the absolute value, flagged
    sign_convention, with the signed value kept in qty_verbatim
  - a missing cost is null, never zero; a licensed feature that is not exposed (routings) is BLOCKED, not empty
  - GET only: any create, update, delete or transform is refused before the transport is touched
Paging follows the REST collection shape: {"items": [...], "hasMore": bool, "offset": n, "count": n}.
"""
from __future__ import annotations

import re
from pathlib import Path

from manufacturing.connectors.common import Adapter, base_row, key_pair, number_or_none
from manufacturing.connectors.lifecycle import LifecycleError

DOC = Path(__file__).resolve().parents[2] / "upstream" / "claude-for-manufacturing" / "shared" / "erp-connectors.md"
NEGATIVE_SIGN_TYPES = {"salesorder", "itemfulfillment"}
PAGE_SIZE = 1000


def documented_record_types() -> set:
    text = DOC.read_text(encoding="utf-8")
    table = text.split("## Record by record", 1)[1].split("\n---", 1)[0]
    types = set()
    for line in table.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[1] and not set(cells[1]) <= set("-: "):
            types |= set(re.findall(r"`([a-z]+)`", cells[1]))
    return types


RECORD_TYPES = documented_record_types()


class NetSuiteError(RuntimeError):
    pass


class NetSuite(Adapter):
    system = "netsuite"
    source_system = "netsuite"

    def connect(self, config: dict):
        self.lc.configure(config)
        if self.lc.state != "CONFIGURED":
            return self.lc.state
        res = self.transport("GET", "/services/rest/record/v1/metadata-catalog", {})
        if res.get("status") == 401:
            return self.lc.fail("UNAUTHENTICATED_OR_EXPIRED")
        if res.get("status", 200) != 200:
            return self.lc.fail(f"HTTP_{res.get('status')}")
        account = res.get("account")
        if config.get("account") and account != config["account"]:
            return self.lc.fail(f"ACCOUNT_MISMATCH connected={account} configured={config['account']}")
        self.lc.authenticated(account or "", config.get("expires_at"))
        if self.lc.state != "AUTHENTICATED":
            return self.lc.state
        sub, locs = self.profile_scope.get("subsidiary"), self.profile_scope.get("locations")
        if not sub or not locs:
            return self.lc.fail("PROFILE_HAS_NO_ERP_SCOPE (subsidiary and locations are required)")
        self.lc.scoped([f"subsidiary:{sub}"] + [f"location:{l}" for l in sorted(locs)])
        self.lc.verified(True)
        return self.lc.state

    def request(self, method: str, path: str, params=None):
        if method != "GET" and not (method == "POST" and path.endswith("/query/v1/suiteql")):
            self.refuse_write(f"{method} {path}", params)
        self.log.add("read", f"{method} {path}", params)
        return self.transport(method, path, dict(params or {}))

    def list(self, record_type: str, query: dict) -> dict:
        self.lc.require_verified()
        if record_type not in RECORD_TYPES:
            raise LifecycleError(f"{record_type} is not a documented NetSuite read")
        sub = query.get("subsidiary", self.profile_scope["subsidiary"])
        if str(sub) != str(self.profile_scope["subsidiary"]):
            raise LifecycleError(f"subsidiary {sub} is outside the profile scope")
        loc = query.get("location")
        if loc is not None and loc not in self.profile_scope["locations"]:
            raise LifecycleError(f"location {loc} is outside the profile scope")
        items, offset = [], 0
        while True:
            res = self.request("GET", f"/services/rest/record/v1/{record_type}",
                               {**query, "subsidiary": sub, "limit": PAGE_SIZE, "offset": offset})
            st = res.get("status", 200)
            if st == 401:
                self.lc.fail("CREDENTIAL_EXPIRED")
                raise LifecycleError("credential expired during a read; connector is UNAVAILABLE")
            if st == 403:
                return {"items": [], "denied": True, "feature_blocked": res.get("feature_blocked"),
                        "detail": res.get("detail")}
            if st != 200:
                raise NetSuiteError(f"HTTP {st} on {record_type}")
            if res.get("account") not in (None, self.lc.tenant):
                raise LifecycleError("response from another account; refused")
            items += res.get("items") or []
            if not res.get("hasMore"):
                break
            offset += res.get("count") or len(res.get("items") or []) or PAGE_SIZE
        return {"items": items, "denied": False}

    # -- mapping ------------------------------------------------------------------------------------------
    def _qty(self, row, record_type, raw):
        q = number_or_none(raw)
        flags = []
        if q is not None and record_type in NEGATIVE_SIGN_TYPES and q < 0:
            row["qty_verbatim"] = q
            q = abs(q)
            flags.append("sign_convention")
        row["qty"] = q
        if flags:
            row["integrity_flags"] = flags
        return row

    def rows(self, record_type: str, items: list, site: str) -> list:
        out = []
        for it in items:
            rid = it.get("id")
            row = base_row(site, self.source_system, f"netsuite:{record_type}/{rid}", it.get("lastModifiedDate"))
            if record_type in ("item", "assemblyitem"):
                key_pair(row, "part_number", it.get("itemId"))
                row["description"] = it.get("displayName")
                row["uom"] = it.get("stockUnit")
                row["amount"] = number_or_none(it.get("standardCost"))   # null stays null: not on file, not zero
                row["currency"] = it.get("currency") if row["amount"] is not None else None
            elif record_type == "salesorder":
                key_pair(row, "sales_order", it.get("tranId"))
                key_pair(row, "part_number", it.get("item"))
                self._qty(row, record_type, it.get("quantity"))
                row["uom"] = it.get("units")
            elif record_type == "purchaseorder":
                key_pair(row, "part_number", it.get("item"))
                key_pair(row, "supplier_id", it.get("entity"))
                self._qty(row, record_type, it.get("quantity"))
                row["uom"] = it.get("units")
                row["amount"] = number_or_none(it.get("rate"))
                row["currency"] = it.get("currency")
            elif record_type == "workorder":
                key_pair(row, "production_wo", it.get("tranId"))
                key_pair(row, "part_number", it.get("assemblyItem"))
                self._qty(row, record_type, it.get("quantity"))
                row["uom"] = it.get("units")
                row["actual_cost"] = number_or_none(it.get("actualCost"))
                key_pair(row, "sales_order", it.get("createdFrom"))
            elif record_type == "vendor":
                key_pair(row, "supplier_id", it.get("entityId"))
                row["supplier_name"] = it.get("companyName")
            else:
                row["raw_ref"] = rid
            out.append(row)
        return out
