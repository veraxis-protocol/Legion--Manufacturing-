"""WO-B04: Infor M3, read-only, through the M3 MCP tools named M3_<program>_<transaction>.

Everything this adapter may call, and how it reads the output, is taken from upstream
`shared/erp-connectors.md` (parsed at import, so the allow-list cannot drift from the document):
  - only the transactions in its "Record by record" table, plus the connection test
  - "Record does not exist" from a list call means none found, never zero and never a failed check
  - YYYYMMDD and YYYY-MM-DD dates; status codes as numbers; deleted (90) out of every count
  - about 30 rows means more exist: narrow and pull again
  - RunTimeHours is never used; operation times stay in the profile's unit, or are "unit unconfirmed"
  - BalanceIdStatus 1 under inspection, 2 approved, 3 rejected
  - never an unfiltered search: facility, warehouse and a date window on every pull
"""
from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path

from manufacturing.connectors.common import Adapter, base_row, key_pair, number_or_none, parse_date
from manufacturing.connectors.lifecycle import LifecycleError

DOC = Path(__file__).resolve().parents[2] / "upstream" / "claude-for-manufacturing" / "shared" / "erp-connectors.md"
CONNECTION_TEST = "MNS150MI_GetUserData_CurrentUser"
PAGE_LIMIT = 30
INSPECTION_STATUS = {"1": "under_inspection", "2": "approved", "3": "rejected"}
CLOSED_WO = {"OrderCompleted", "OrderReady"}


def documented_reads() -> set:
    text = DOC.read_text(encoding="utf-8")
    table = text.split("## Record by record", 1)[1].split("\n---", 1)[0]
    calls = set(re.findall(r"`([A-Z]{3}\d{3}MI_[A-Za-z_]+)`", table))
    calls.add(CONNECTION_TEST)
    return calls


def documented_never_called() -> set:
    text = DOC.read_text(encoding="utf-8")
    sect = text.split("The skills do not call", 1)[1].split("\n", 2)
    return set(re.findall(r"`([A-Z]{3}\d{3}MI_[A-Za-z_]+)`", " ".join(sect[:2])))


ALLOWED = documented_reads()
NEVER = documented_never_called()


class M3CheckFailed(RuntimeError):
    pass


class InforM3(Adapter):
    system = "infor_m3"
    source_system = "infor_m3"

    def connect(self, config: dict):
        self.lc.configure(config)
        if self.lc.state != "CONFIGURED":
            return self.lc.state
        try:
            user = self._raw(CONNECTION_TEST, {})
        except M3CheckFailed as e:
            return self.lc.fail(f"CONNECTION_TEST_FAILED {e}")
        rows = user.get("rows") or []
        if not rows:
            return self.lc.fail("CONNECTION_TEST_RETURNED_NO_USER")
        u = rows[0]
        tenant = f"{u.get('Company')}/{u.get('Division')}"
        self.lc.authenticated(tenant if u.get("Company") else "", config.get("expires_at"))
        if self.lc.state != "AUTHENTICATED":
            return self.lc.state
        want_fac = self.profile_scope.get("facility")
        want_whs = set(self.profile_scope.get("warehouses") or [])
        if not want_fac or not want_whs:
            return self.lc.fail("PROFILE_HAS_NO_ERP_SCOPE (facility and warehouses are required; never unfiltered)")
        if u.get("Facility") and u["Facility"] != want_fac:
            return self.lc.fail(f"FACILITY_MISMATCH user={u['Facility']} profile={want_fac}")
        self.lc.scoped([f"facility:{want_fac}"] + [f"warehouse:{w}" for w in sorted(want_whs)])
        self.lc.verified(True)
        self.user = u
        return self.lc.state

    # -- transport --------------------------------------------------------------------------------------------
    def _raw(self, call: str, args: dict) -> dict:
        if call in NEVER or call not in ALLOWED:
            self.refuse_write(call, args)
        self.log.add("read", call, args)
        out = self.transport("M3_" + call, dict(args))
        if out.get("error"):
            msg = str(out["error"])
            if "record does not exist" in msg.lower():
                return {"rows": [], "none_found": True}
            raise M3CheckFailed(f"{call}: {msg}")
        return {"rows": list(out.get("rows") or []), "none_found": False}

    def read(self, call: str, args: dict, window: tuple, date_arg: tuple = ("FromDate", "ToDate")) -> dict:
        """A filtered, paginated read. Splits the date window while a slice returns PAGE_LIMIT or more rows."""
        self.lc.require_verified()
        if call == CONNECTION_TEST:
            raise LifecycleError("the connection test is not a data read")
        fac = self.profile_scope["facility"]
        if args.get("Facility", fac) != fac:
            raise LifecycleError(f"facility {args.get('Facility')} is outside the profile scope {fac}")
        if "Warehouse" in args and args["Warehouse"] not in self.profile_scope["warehouses"]:
            raise LifecycleError(f"warehouse {args['Warehouse']} is outside the profile scope")
        start, end = window
        if start is None or end is None:
            raise LifecycleError("never an unfiltered search: a date window is required")
        rows, slices, none_found = [], 0, True
        stack = [(start, end)]
        while stack:
            a, b = stack.pop()
            res = self._raw(call, {**args, "Facility": fac, date_arg[0]: a.strftime("%Y%m%d"),
                                   date_arg[1]: b.strftime("%Y%m%d")})
            slices += 1
            if len(res["rows"]) >= PAGE_LIMIT:
                if a >= b:
                    raise M3CheckFailed(f"{call}: {len(res['rows'])} rows in a one-day slice; narrow by item or status")
                mid = a + timedelta(days=(b - a).days // 2)
                stack += [(mid + timedelta(days=1), b), (a, mid)]
                continue
            none_found &= res["none_found"]
            rows += res["rows"]
        return {"rows": rows, "slices": slices, "sliced": slices > 1, "none_found": none_found and not rows}

    # -- mapping onto the consolidated dataset (contracts/consolidated-dataset.md) ------------------------------
    def inventory_rows(self, rows, site, as_of):
        out = []
        for r in rows:
            row = base_row(site, self.source_system,
                           f"infor_m3:balance/{r.get('Warehouse')}/{r.get('Location')}/{r.get('ItemNumber')}/{r.get('BatchNumber')}",
                           as_of)
            key_pair(row, "part_number", r.get("ItemNumber"))
            key_pair(row, "lot_number", r.get("BatchNumber"))
            row["location"] = r.get("Location")
            row["qty"] = number_or_none(r.get("ApprovedOnHandBalance"))
            row["uom"] = r.get("BasicUnitOfMeasure")          # None stays None: a qty without uom is not summed
            st = str(r.get("BalanceIdStatus")) if r.get("BalanceIdStatus") is not None else None
            row["inspection_status"] = INSPECTION_STATUS.get(st, "unknown" if st else None)
            row["available"] = st == "2"
            out.append(row)
        return out

    def work_order_rows(self, rows, site):
        out = []
        for r in rows:
            row = base_row(site, self.source_system, f"infor_m3:mo/{r.get('ManufacturingOrderNumber')}", None)
            key_pair(row, "production_wo", r.get("ManufacturingOrderNumber"))
            key_pair(row, "part_number", r.get("ProductNumber"))
            row["status"] = r.get("WorkOrderStatus")
            row["closed"] = r.get("WorkOrderStatus") in CLOSED_WO
            row["qty"] = number_or_none(r.get("OrderedQuantity"))
            row["uom"] = r.get("BasicUnitOfMeasure")
            row["due_date"] = parse_date(r.get("PlannedFinishDate"))
            row["start_date"] = parse_date(r.get("StartDate"))
            row["sales_order"] = row["sales_order_verbatim"] = None   # the M3 pull holds no WO-to-SO link
            out.append(row)
        return out

    def operation_rows(self, rows, site, mo, part):
        unit = (self.profile_scope.get("m3_time_unit") or "").strip() or None
        out = []
        for r in rows:
            row = base_row(site, self.source_system, f"infor_m3:mo/{mo}/op/{r.get('OperationNumber')}",
                           None)
            key_pair(row, "production_wo", mo)
            key_pair(row, "part_number", part)
            row["op_seq"] = int(r["OperationNumber"]) if r.get("OperationNumber") is not None else None
            key_pair(row, "work_center", r.get("WorkCenter"))
            row["actual_setup_hours"] = number_or_none(r.get("UsedLaborSetupTime"))
            row["actual_run_hours"] = number_or_none(r.get("UsedLaborRunTime"))
            row["qty_completed"] = number_or_none(r.get("CompletedQuantity"))
            row["closed_date"] = parse_date(r.get("ReportingDate"))
            # erp-connectors.md, Reading M3 output 5: RunTimeHours is not hours, and is never read.
            row["time_unit"] = unit
            row["time_unit_flag"] = None if unit else "M3 time unit not recorded in the profile: values as read, unit unconfirmed, not costed"
            row["costable"] = bool(unit)
            out.append(row)
        return out

    def purchase_rows(self, rows, site):
        out = []
        for r in rows:
            st = str(r.get("HighestStatus") or r.get("Status") or "")
            if st == "90":
                continue                                          # deleted: out of every count
            row = base_row(site, self.source_system,
                           f"infor_m3:po/{r.get('PurchaseOrderNumber')}/{r.get('LineNumber', '')}", None)
            key_pair(row, "part_number", r.get("ItemNumber"))
            key_pair(row, "supplier_id", r.get("SupplierNumber"))
            row["qty"] = number_or_none(r.get("OrderedQuantity"))
            row["uom"] = r.get("BasicUnitOfMeasure")
            row["amount"] = number_or_none(r.get("PurchasePrice"))
            row["currency"] = r.get("Currency")                  # Required alongside amount; never assumed
            row["status_code"] = st or None
            out.append(row)
        return out
