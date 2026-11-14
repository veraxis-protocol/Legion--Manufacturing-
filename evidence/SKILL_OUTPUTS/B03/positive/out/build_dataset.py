"""data-consolidate run: join the pulse_oee export drop and the equipment list.

Writes one CSV per dataset tab (no XLSX writer is installed: openpyxl/xlsxwriter
absent, nothing installed), the key-mismatch log, the figures block, and the
HTML data quality report. Every figure in the report comes from this script.
"""
import csv, os, re, html, datetime, json

ROOT = r"C:/LMFG/runs/B03-positive/work"
INP = ROOT + "/inputs"
OUT = ROOT + "/out"
DS = OUT + "/dataset"
os.makedirs(DS, exist_ok=True)
RUN = datetime.datetime.now()


def read(path):
    rows, comments = [], []
    with open(path, newline="", encoding="utf-8") as f:
        lines = f.read().splitlines()
    data = []
    for i, ln in enumerate(lines, 1):
        if ln.startswith("#"):
            comments.append(ln)
            continue
        data.append((i, ln))
    hdr = next(csv.reader([data[0][1]]))
    for i, ln in data[1:]:
        if not ln.strip():
            continue
        vals = next(csv.reader([ln]))
        rows.append((i, dict(zip(hdr, vals))))
    return hdr, rows, comments


def mtime(path):
    return datetime.datetime.fromtimestamp(os.path.getmtime(path))


# ---------- Step 1: discover ----------
files = {}
for dp, _, fns in os.walk(INP):
    for fn in sorted(fns):
        files[os.path.join(dp, fn).replace("\\", "/")] = None

def fold(h):
    return re.sub(r"[^a-z0-9]", "", h.lower())

identified = []  # (file, identified_as, tab or None, note)
for p in sorted(files):
    name = os.path.basename(p)
    if not name.endswith(".csv"):
        identified.append((p, "Not a data export (readme text)", None,
                           "Read for context only: says the drop is synthetic test data."))
        continue
    hdr, rows, _ = read(p)
    h = {fold(x) for x in hdr}
    if {"assetid", "startedat", "endedat"} <= h:
        identified.append((p, "Downtime events (MES/historian export)", "downtime_events", ""))
    elif {"workorder", "qtygood", "qtyscrap"} <= h:
        identified.append((p, "Production output (MES export)", "production_output", ""))
    elif {"partnumber", "plannedqty", "plandate"} <= h:
        identified.append((p, "Plan / schedule (planning export)", "plan", ""))
    elif {"workorder", "partnumber", "qtyordered", "status"} <= h:
        identified.append((p, "Production work orders (ERP export, system not named)", "production_work_orders", ""))
    elif {"assetid", "description"} <= h:
        identified.append((p, "Asset / equipment list", "assets", ""))
    elif "opseq" in h and "workcenter" in h and "partnumber" in h:
        has_setup = any("setup" in x for x in h)
        has_run = any("run" in x for x in h)
        if has_setup and has_run:
            identified.append((p, "Routing", "routings", ""))
        else:
            identified.append((p, "UNRECOGNIZED: routing-like, missing a signature column", None,
                               "Carries part, op_seq, work center and a run time per unit, but no setup time "
                               "(and no revision). Per the routing signature it is not loaded and the gap is not filled."))
    else:
        identified.append((p, "UNRECOGNIZED", None, "Header matches no known signature."))

def rel(p):
    return p.replace(INP + "/", "")

# ---------- load ----------
src = {}
for p, what, tab, note in identified:
    if p.endswith(".csv"):
        src[os.path.basename(p)] = (p,) + read(p)

eq_p, eq_h, eq_rows, eq_comments = src["equipment.csv"]
out_p, _, out_rows, _ = src["output.csv"]
dt_p, _, dt_rows, _ = src["downtime.csv"]
pl_p, _, pl_rows, _ = src["plan.csv"]
wo_p, _, wo_rows, _ = src["work_orders.csv"]
rt_p, rt_h, rt_rows, _ = src["routing.csv"]

# ---------- normalization ladder (compare only) ----------
def rung1(k): return k.strip()
def rung2(k): return rung1(k).upper()
def rung3(k): return re.sub(r"[^A-Z0-9]", "", rung2(k))
def rung4(k): return re.sub(r"(?<![0-9])0+(?=[0-9])", "", rung3(k))
def rung5(k): return re.sub(r"\s*REV\s*\w+$", "", rung2(k), flags=re.I)

def match(key, universe):
    """Return (status, rung, partner, class)."""
    if key in universe:
        return ("matched", 0, key, None)
    for n, fn, cls in ((1, rung1, 5), (2, rung2, 5), (3, rung3, 2), (4, rung4, 3)):
        hits = [u for u in universe if fn(u) == fn(key)]
        if len(hits) == 1:
            return ("proposed_normalization", n, hits[0], cls)
    hits = [u for u in universe if rung3(rung5(u)) == rung3(rung5(key))]
    if len(hits) == 1:
        return ("proposed_normalization", 5, hits[0], 4)
    return ("unmatched", None, None, 1)

asset_master = [r["asset_id"] for _, r in eq_rows]
wo_master = [r["work_order"] for _, r in wo_rows]
wo_part = {r["work_order"]: r["part_number"] for _, r in wo_rows}
parts_seen_wo = sorted(set(wo_part.values()))

mismatch_log = []  # dicts
def log(tab, srcfile, line, key_type, verbatim, res, note=""):
    status, rung, partner, cls = res
    mismatch_log.append(dict(tab=tab, source_ref=f"{rel(srcfile)}:{line}", key=key_type,
                             value_verbatim=verbatim, status=status,
                             ladder_rung=rung if rung is not None else "",
                             partner=partner or "", mismatch_class=cls or "",
                             note=note))

COMMON = ["site", "source_system", "source_ref", "as_of", "join_status",
          "mismatch_class", "contradicted_by", "integrity_flags"]

def row_status(results):
    """Row-level join_status: worst of its keys."""
    if any(r[0] == "unmatched" for r in results):
        cls = [r[3] for r in results if r[0] == "unmatched"]
        return "unmatched", cls[0]
    if any(r[0] == "proposed_normalization" for r in results):
        return "proposed_normalization", [r[3] for r in results if r[0] == "proposed_normalization"][0]
    return "matched", None

# activity window
act_dates = {"output.csv": sorted({r["production_day"] for _, r in out_rows}),
             "downtime.csv": sorted({r["started_at"][:10] for _, r in dt_rows} | {r["ended_at"][:10] for _, r in dt_rows}),
             "plan.csv": sorted({r["plan_date"] for _, r in pl_rows})}
win = {k: (v[0], v[-1]) for k, v in act_dates.items()}
ov_start = max(v[0] for v in win.values()); ov_end = min(v[1] for v in win.values())
overlap_ok = ov_start <= ov_end

def future(ts):
    try:
        d = datetime.datetime.fromisoformat(ts) if "T" in ts else datetime.datetime.fromisoformat(ts + "T00:00:00")
    except ValueError:
        return False
    return d > RUN

SITE_UNSTATED = "not stated in source"

# ---------- assets ----------
used_assets = {}
for f, rows in (("output.csv", out_rows), ("downtime.csv", dt_rows), ("plan.csv", pl_rows)):
    for _, r in rows:
        used_assets.setdefault(r["asset_id"], set()).add(f)

assets_tab = []
for ln, r in eq_rows:
    a = r["asset_id"]
    used = a in {rung2(x) for x in used_assets} or any(match(x, [a])[0] != "unmatched" for x in used_assets)
    assets_tab.append(dict(site=SITE_UNSTATED, source_system="manual",
                           source_ref=f"{rel(eq_p)}:{ln}",
                           as_of=f"{mtime(eq_p).date()} (file modified date; source records no date, zone unresolved)",
                           join_status="matched" if used else "unmatched",
                           mismatch_class="" if used else 6, contradicted_by="", integrity_flags="",
                           asset_id=rung1(a), asset_id_verbatim=a, location=r["cell"]))
    if not used:
        log("assets", eq_p, ln, "asset", a, ("unmatched", None, None, 6),
            "On the equipment list; appears in no output, downtime or plan row. No other source records activity on it.")

# ---------- production_work_orders ----------
out_wos = {r["work_order"] for _, r in out_rows}
pwo_tab = []
for ln, r in wo_rows:
    has_out = r["work_order"] in out_wos
    pwo_tab.append(dict(site=SITE_UNSTATED, source_system="manual", source_ref=f"{rel(wo_p)}:{ln}",
                        as_of=f"{mtime(wo_p).date()} (file modified date; source records no date, zone unresolved)",
                        join_status="matched" if has_out else "unmatched",
                        mismatch_class="" if has_out else 6, contradicted_by="", integrity_flags="",
                        production_wo=rung1(r["work_order"]), production_wo_verbatim=r["work_order"],
                        part_number=rung1(r["part_number"]), part_number_verbatim=r["part_number"],
                        qty=r["qty_ordered"], uom="", due_date=r["due_date"], status=r["status"],
                        sales_order="", sales_order_verbatim=""))

# ---------- production_output ----------
po_tab = []
grain = {}
for ln, r in out_rows:
    rw = match(r["work_order"], wo_master); log("production_output", out_p, ln, "production work order", r["work_order"], rw)
    rp_res = ("matched", 0, r["part_number"], None) if wo_part.get(r["work_order"]) == r["part_number"] else ("unmatched", None, None, 1)
    log("production_output", out_p, ln, "part (vs work order's part)", r["part_number"], rp_res)
    ra = match(r["asset_id"], asset_master)
    log("production_output", out_p, ln, "asset", r["asset_id"], ra,
        "" if ra[0] == "matched" else "Asset ID not on the equipment list under any ladder rung.")
    st, cls = row_status([rw, rp_res, ra])
    win_ok = ov_start <= r["production_day"] <= ov_end
    if not win_ok:
        st, cls = "unmatched", 7
    flags = ["future_timestamp"] if future(r["production_day"]) else []
    g = (r["work_order"], r["shift"], r["production_day"]); grain.setdefault(g, []).append(ln)
    po_tab.append(dict(site=r["site"], source_system="mes_export", source_ref=f"{rel(out_p)}:{ln}",
                       as_of=f"{r['production_day']} (date only; zone unresolved)",
                       join_status=st, mismatch_class=cls or "", contradicted_by="",
                       integrity_flags=";".join(flags),
                       production_wo=rung1(r["work_order"]), production_wo_verbatim=r["work_order"],
                       part_number=rung1(r["part_number"]), part_number_verbatim=r["part_number"],
                       part_revision="", asset_id=rung1(r["asset_id"]), asset_id_verbatim=r["asset_id"],
                       qty_good=r["qty_good"], qty_scrap=r["qty_scrap"], uom="",
                       shift=r["shift"], production_day=r["production_day"]))
dups_output = {g: l for g, l in grain.items() if len(l) > 1}

# ---------- downtime_events ----------
dt_tab = []
dur_checks = []
for ln, r in dt_rows:
    ra = match(r["asset_id"], asset_master)
    log("downtime_events", dt_p, ln, "asset", r["asset_id"], ra,
        "" if ra[0] == "matched" else "Asset ID not on the equipment list under any ladder rung.")
    s = datetime.datetime.fromisoformat(r["started_at"]); e = datetime.datetime.fromisoformat(r["ended_at"])
    calc = (e - s).total_seconds() / 60
    flags = []
    if e < s: flags.append("end_before_start")
    if abs(calc - float(r["duration_minutes"])) > 1: flags.append("duration_mismatch")
    if future(r["started_at"]) or future(r["ended_at"]): flags.append("future_timestamp")
    dur_checks.append((rel(dt_p) + f":{ln}", r["duration_minutes"], calc))
    st, cls = row_status([ra])
    dt_tab.append(dict(site=SITE_UNSTATED, source_system="mes_export", source_ref=f"{rel(dt_p)}:{ln}",
                       as_of=f"{r['started_at']} (no zone in source; unresolved)",
                       join_status=st, mismatch_class=cls or "", contradicted_by="",
                       integrity_flags=";".join(flags),
                       asset_id=rung1(r["asset_id"]), asset_id_verbatim=r["asset_id"],
                       started_at=r["started_at"], ended_at=r["ended_at"],
                       duration_minutes=r["duration_minutes"], reason_code=r["reason_code"],
                       reason_text=r["reason_text"]))

# ---------- plan ----------
pl_tab = []
pgrain = {}
for ln, r in pl_rows:
    rp_res = ("matched", 0, r["part_number"], None) if r["part_number"] in parts_seen_wo else match(r["part_number"], parts_seen_wo)
    log("plan", pl_p, ln, "part (vs work-order export)", r["part_number"], rp_res)
    ra = match(r["asset_id"], asset_master)
    log("plan", pl_p, ln, "asset", r["asset_id"], ra,
        "" if ra[0] == "matched" else "Asset ID not on the equipment list under any ladder rung.")
    st, cls = row_status([rp_res, ra])
    pgrain.setdefault((r["part_number"], r["plan_date"]), []).append(ln)
    pl_tab.append(dict(site=SITE_UNSTATED, source_system="planning_export", source_ref=f"{rel(pl_p)}:{ln}",
                       as_of=f"{r['plan_date']} (date only; zone unresolved)",
                       join_status=st, mismatch_class=cls or "", contradicted_by="",
                       integrity_flags="future_timestamp" if future(r["plan_date"]) else "",
                       part_number=rung1(r["part_number"]), part_number_verbatim=r["part_number"],
                       asset_id=rung1(r["asset_id"]), asset_id_verbatim=r["asset_id"],
                       qty=r["planned_qty"], uom="", plan_date=r["plan_date"],
                       planned_hours=r["planned_hours"], work_center_verbatim=r["work_center"]))
dups_plan = {g: l for g, l in pgrain.items() if len(l) > 1}

# ---------- write tabs ----------
def write_tab(name, rows):
    if not rows:
        return
    with open(f"{DS}/{name}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

tabs = {"assets": assets_tab, "production_work_orders": pwo_tab, "production_output": po_tab,
        "downtime_events": dt_tab, "plan": pl_tab}
for k, v in tabs.items():
    write_tab(k, v)
missing_tabs = {
    "parts": "No item master was in the drop and no ERP is connected. Part numbers were checked across the work-order, output and plan exports only.",
    "routings": "routing.csv was set aside: it has no setup-time column (and no revision), so it does not meet the routing signature. quote-build would start at closed-job actuals, which are also missing.",
    "operation_actuals": "No actuals file in the drop. With no routing either, quote-build would start at a geometry-derived or first-principles estimate.",
    "sales_orders": "No sales order export; work orders carry no sales order link, so commitment impact is not traceable.",
    "lots": "No MES lot or quality export in the drop.",
    "inventory": "No inventory export in the drop.",
    "purchase_orders": "No purchasing export in the drop.",
    "inspection_results": "No quality/inspection export in the drop.",
    "maintenance_work_orders": "The equipment list carries assets only; no maintenance tickets.",
    "ncrs": "No NCR export in the drop.",
}
with open(f"{DS}/_tabs_missing.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["tab", "status", "why"])
    for k, v in missing_tabs.items():
        w.writerow([k, "MISSING (not empty)", v])

with open(f"{OUT}/key_mismatch_log.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(mismatch_log[0].keys())); w.writeheader(); w.writerows(mismatch_log)

# ---------- figures ----------
all_rows = assets_tab + pwo_tab + po_tab + dt_tab + pl_tab
def cnt(rows, **kw):
    return sum(all(str(r.get(k)) == str(v) for k, v in kw.items()) for r in rows)

key_checks = [m for m in mismatch_log if m["tab"] != "assets"]
F = []
def fig(name, val, frm, flt):
    F.append(dict(figure=name, value=val, computed_from=frm, filter=flt)); return val

rows_in = fig("Rows in, all loaded files", len(all_rows), "5 loaded files", "data rows, comment lines excluded")
for t, rws in tabs.items():
    fig(f"Rows in, {t}", len(rws), t, "all rows")
    fig(f"Rows fully joined, {t}", cnt(rws, join_status="matched"), t, "join_status == matched")
joined = fig("Rows fully joined, all tabs", cnt(all_rows, join_status="matched"), "all tabs", "join_status == matched")
kc = fig("Key checks run (non-asset-list rows)", len(key_checks), "key_mismatch_log.csv", "tab != assets")
exact = fig("Key checks matched exactly", sum(m["status"] == "matched" for m in key_checks), "key_mismatch_log.csv", "status == matched")
normd = fig("Key checks matched after normalization", sum(m["status"] == "normalized" for m in key_checks), "key_mismatch_log.csv", "status == normalized")
prop = fig("Key checks awaiting a proposed fix (classes 2-5)", sum(m["status"] == "proposed_normalization" for m in key_checks), "key_mismatch_log.csv", "status == proposed_normalization")
unm = fig("Key checks unmatched", sum(m["status"] == "unmatched" for m in key_checks), "key_mismatch_log.csv", "status == unmatched")
fig("Key checks matched (exact + normalized)", exact + normd, "reconciliation", "exact + normalized")
cls_counts = {}
for c in range(1, 9):
    n = sum(str(m["mismatch_class"]) == str(c) for m in mismatch_log)
    cls_counts[c] = fig(f"Records in class {c}", n, "key_mismatch_log.csv + duplicate/window checks", f"mismatch_class == {c}")
cls_counts[8] = len(dups_output) + len(dups_plan)
F[-1]["value"] = cls_counts[8]; F[-1]["filter"] = "colliding keys at tab grain (output: WO+shift+day; plan: part+date)"
asset_orph_rows = [m for m in mismatch_log if m["key"] == "asset" and m["status"] == "unmatched" and m["tab"] != "assets"]
fig("Asset IDs used in output/downtime/plan", len(used_assets), "output, downtime, plan", "distinct asset_id")
fig("Of those, on the equipment list", sum(match(a, asset_master)[0] != "unmatched" for a in used_assets), "equipment.csv", "any ladder rung")
fig("Assets on equipment list", len(asset_master), "equipment.csv", "all rows")
fig("Equipment assets with no activity (class 6)", cls_counts[6], "assets tab", "mismatch_class == 6")
fig("Output rows with orphan asset", sum(1 for m in asset_orph_rows if m["tab"] == "production_output"), "production_output", "asset unmatched")
fig("Downtime rows with orphan asset", sum(1 for m in asset_orph_rows if m["tab"] == "downtime_events"), "downtime_events", "asset unmatched")
fig("Plan rows with orphan asset", sum(1 for m in asset_orph_rows if m["tab"] == "plan"), "plan", "asset unmatched")
fig("Downtime minutes on orphan assets", sum(int(r["duration_minutes"]) for r in dt_tab if r["join_status"] == "unmatched"), "downtime_events", "join_status == unmatched; minutes as stated")
fig("Production WOs in output found in work-order export", sum(1 for m in mismatch_log if m["key"] == "production work order" and m["status"] == "matched"), "key_mismatch_log.csv", "key == production work order, matched")
fig("Output rows whose part equals the work order's part", sum(1 for m in mismatch_log if m["key"].startswith("part (vs work order") and m["status"] == "matched"), "key_mismatch_log.csv", "part vs work order part")
fig("Work orders with no output (class 6)", cnt(pwo_tab, mismatch_class=6), "production_work_orders", "mismatch_class == 6")
flagnames = ["sign_convention", "mixed_sign", "end_before_start", "duration_mismatch", "ncr_part_differs", "ncr_dated_before_wo", "future_timestamp", "units_conflict"]
for fl in flagnames:
    fig(f"Rows flagged {fl}", sum(fl in str(r["integrity_flags"]).split(";") for r in all_rows), "all tabs", f"'{fl}' in integrity_flags")
fig("Rows with no UOM stated", sum(1 for r in all_rows if "uom" in r and r["uom"] == ""), "all tabs carrying a quantity", "uom empty")
fig("Rows with as_of zone unresolved", len(all_rows), "all tabs", "no zone in any source; no Plant context")
fig("Rows with site not stated in source", cnt(all_rows, site=SITE_UNSTATED), "all tabs", "site column absent from source")
fig("Activity overlap window start", ov_start, "output, downtime, plan", "max of window starts")
fig("Activity overlap window end", ov_end, "output, downtime, plan", "min of window ends")
fig("Class 7 (outside window) activity rows", cls_counts[7], "activity tabs", "date outside overlap")
fig("actuals rows flagged probable_standard", "n/a (operation_actuals tab missing)", "-", "-")
fig("Normalization rules applied", 0, "ladder log", "no rung fired on any key")

# reconcile
assert exact + normd + prop + unm == kc, "key checks do not reconcile"
assert prop == sum(cls_counts[c] for c in (2, 3, 4, 5)), "proposed != classes 2-5"
with open(f"{OUT}/figures_block.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["figure", "value", "computed_from", "filter"]); w.writeheader(); w.writerows(F)

json.dump(dict(identified=[(rel(a), b, c, d) for a, b, c, d in identified],
               mtimes={rel(p): mtime(p).isoformat(timespec="minutes") for p in files},
               windows=win, overlap=(ov_start, ov_end), dur_checks=dur_checks,
               dups_output=len(dups_output), dups_plan=len(dups_plan),
               used_assets={k: sorted(v) for k, v in used_assets.items()},
               run=RUN.isoformat(timespec="minutes")),
          open(f"{OUT}/_run_facts.json", "w"), indent=1)
print(json.dumps({f["figure"]: f["value"] for f in F}, indent=1))
