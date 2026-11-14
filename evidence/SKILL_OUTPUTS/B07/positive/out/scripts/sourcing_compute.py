"""Sourcing event SRC-2026-11-14-BSH-1210 - computes every figure used in the
RFQ package, the internal notes and the bid comparison (supplier-quote-request,
steps 3, 10, 11, 12). Run:  python -I sourcing_compute.py <work_dir>

Bid values are MAPPED from the bid files as the supplier stated them (never
normalised); every value carries a source_ref. Nothing here is sent anywhere.
"""
import csv, datetime as dt, html, json, os, sys

WORK = sys.argv[1]
INP = os.path.join(WORK, "inputs", "supplier")
OUT = os.path.join(WORK, "out")
EVENT = "SRC-2026-11-14-BSH-1210"
TODAY = dt.date(2026, 11, 14)
NOW = "2026-11-14T16:58:06-05:00"
SITE = "not stated (no plant profile on file)"

figures = []  # (figure, value, computed_from, filter)
def fig(name, value, src, flt):
    figures.append((name, value, src, flt)); return value

# ---------------- Step 3: demand picture ----------------
rows = []
with open(os.path.join(INP, "demand.csv"), newline="", encoding="utf-8") as f:
    lines = [l for l in f if not l.startswith("#")]
for r in csv.DictReader(lines):
    rows.append(r)
part = [r for r in rows if r["item"] == "BSH-1210"]
qtys = [int(r["qty_required"]) for r in part]
months = sorted(r["month"] for r in part)
revs = sorted(set(r["rev"] for r in part))
fig("MRP requirement rows, BSH-1210", len(part), "demand.csv", 'item == "BSH-1210", comment line excluded')
total = fig("MRP requirement total, BSH-1210 (pcs)", sum(qtys), "demand.csv", 'sum(qty_required) where item == "BSH-1210"')
fig("MRP requirement window", f"{months[0]} to {months[-1]} ({len(set(months))} months)", "demand.csv", "min/max of month")
for r in part:
    fig(f"MRP requirement {r['month']} (pcs)", int(r["qty_required"]), "demand.csv", f'item == "BSH-1210" and month == "{r["month"]}"')
fig("Largest single-month requirement (pcs)", max(qtys), "demand.csv", "max(qty_required)")
fig("Revision(s) the MRP demand is stated against", ",".join(revs), "demand.csv", "distinct rev")
fig("Purchase-order / receipt history rows for BSH-1210", "0 - none supplied", "inputs/supplier folder enumerated", "no PO, receipt or usage file present among the 4 input files")
fig("Forecast / EAU rows", "0 - none supplied", "inputs/supplier folder enumerated", "no forecast file; demand.csv holds MRP requirement only")

# Package quantity breaks: taken from MRP figures (first month, largest month, window total)
first_month_qty = int([r for r in part if r["month"] == months[0]][0]["qty_required"])
BREAKS = sorted(set([first_month_qty, max(qtys), total]))
fig("Package quantity breaks proposed (pcs)", ", ".join(str(b) for b in BREAKS), "demand.csv",
    f"first month {months[0]} qty; largest month qty; window total - buyer to confirm")

# ---------------- Step 11: bid records (mapped, not normalised) ----------------
def brk(q, unit, as_q, fa, prod, src):
    return dict(quantity=q, uom="each", unit_price=unit, as_quoted=as_q,
                lead_time_first_article=fa, lead_time_production=prod, source_ref=src)

A_SRC = "bid_supplier_A.txt"
B_SRC = "bid_supplier_B.txt"
bids = [
    dict(contract_version=1, site=SITE, event_ref=EVENT, bid_ref=f"{EVENT}/unlisted-alder/1", supersedes=None,
         supplier_id="unlisted", supplier_id_verbatim="Alder Sintered Parts", supplier_name="Alder Sintered Parts",
         approval_status="not_confirmed_approved", received_at=None,
         received_at_reason="nothing in the file dates the bid; file timestamp is a copy time, not receipt",
         received_via="pasted", source_ref=f"{A_SRC}, lines 2-4", ingested_at=NOW,
         quote_ref="Q-A-118", revision_quoted="A (\"Part BSH-1210 rev A\", line 2)",
         currency="USD",
         breaks=[brk(800, None, "not quoted at 800 (MOQ 1,000)", None, None, f"{A_SRC}, line 3"),
                 brk(1200, None, "not quoted at 1,200 (quoted 1,000 pcs 0.62 USD/ea)", None, None, f"{A_SRC}, line 3"),
                 brk(3200, None, "not quoted at 3,200 (quoted 3,000 pcs 0.55 USD/ea)", None, None, f"{A_SRC}, line 3")],
         breaks_as_quoted=[brk(1000, 0.62, "1,000 pcs 0.62 USD/ea", None, "4 weeks ARO", f"{A_SRC}, line 3"),
                           brk(3000, 0.55, "3,000 pcs 0.55 USD/ea", None, "4 weeks ARO", f"{A_SRC}, line 3")],
         tooling_price=None, tooling_in_unit_price=None, tooling_ownership=None, tooling_note="Tooling: existing.",
         moq=1000, moq_uom="each", validity_until=None, validity_as_stated="valid 30 days (start event not stated; receipt date unknown)",
         freight_basis="FOB origin", payment_terms=None,
         quality_clause_acceptance="not_stated", clause_exceptions=[],
         exceptions=["Exceptions: hardness 25-45 HRF. (drawing rev A requires 25-40 HRF)"],
         conformance="off_format",
         fields_missing=["unit price at 800", "unit price at 1,200", "unit price at 3,200",
                         "lead time, first article, from a named event",
                         "lead time split first article / production (only '4 weeks ARO' given)",
                         "tooling price, or an explicit statement that no charge applies ('Tooling: existing')",
                         "tooling ownership", "price validity as a date or from a named start event",
                         "quality clause acceptance (certificate of conformance per lot)",
                         "payment terms"],
         restatement_requested=True),
    dict(contract_version=1, site=SITE, event_ref=EVENT, bid_ref=f"{EVENT}/unlisted-birch/1", supersedes=None,
         supplier_id="unlisted", supplier_id_verbatim="Birch Powder Metal", supplier_name="Birch Powder Metal",
         approval_status="not_confirmed_approved", received_at=None,
         received_at_reason="nothing in the file dates the bid; file timestamp is a copy time, not receipt",
         received_via="pasted", source_ref=f"{B_SRC}, lines 2-3", ingested_at=NOW,
         quote_ref="BPM-77", revision_quoted="not stated (\"BSH-1210, revision not stated\", line 2)",
         currency="USD",
         breaks=[brk(800, None, "not quoted at 800", None, None, f"{B_SRC}, line 3"),
                 brk(1200, None, "not quoted at 1,200", None, None, f"{B_SRC}, line 3"),
                 brk(3200, 0.49, "Unit price 0.49 USD at 3,200 pcs", None, None, f"{B_SRC}, line 3")],
         breaks_as_quoted=[brk(3200, 0.49, "Unit price 0.49 USD at 3,200 pcs", None, None, f"{B_SRC}, line 3")],
         lead_time_as_stated="Lead 6-7 weeks (no start event, no first article / production split)",
         tooling_price=1850.0, tooling_in_unit_price=False, tooling_ownership=None, tooling_note="Tooling 1,850 USD one time.",
         moq=None, moq_uom="each", validity_until=None, validity_as_stated=None,
         freight_basis="Delivered DDP Dayton", payment_terms="net 45",
         quality_clause_acceptance="not_stated", clause_exceptions=[], exceptions=[],
         conformance="off_format",
         fields_missing=["drawing revision quoted against", "unit price at 800", "unit price at 1,200",
                         "lead time, first article, from a named event",
                         "lead time, production, from a named event ('6-7 weeks' has no start event)",
                         "tooling ownership", "minimum order quantity", "price validity",
                         "quality clause acceptance (certificate of conformance per lot)"],
         restatement_requested=True),
]
for b in bids:
    fig(f"fields_missing count, {b['supplier_name']}", len(b["fields_missing"]), b["source_ref"], "mandated fields checked one by one")
fig("Bids received", len(bids), "inputs/supplier", "files named bid_*.txt")
fig("Bids conforming to mandated format", sum(1 for b in bids if b["conformance"] == "conforming"), "bid records", 'conformance == "conforming"')
fig("Suppliers confirmed approved", sum(1 for b in bids if b["approval_status"] != "not_confirmed_approved"), "bid records",
    "no approved-supplier table and no ERP vendor records on file -> none can be confirmed")

# ---------------- Step 12: comparison per break ----------------
def money(x): return f"{x:,.2f}"
comparison = {}
for q in BREAKS:
    rowsq = []
    for b in bids:
        br = [x for x in b["breaks"] if x["quantity"] == q][0]
        ext = round(br["unit_price"] * q, 2) if br["unit_price"] is not None else None
        foc = round(ext + b["tooling_price"], 2) if (ext is not None and b["tooling_price"] is not None) else None
        flags = []
        if b["moq"] is not None and b["moq"] > q: flags.append(f"MOQ {b['moq']:,} above break {q:,}: price does not buy this quantity")
        if b["moq"] is None: flags.append("MOQ not stated")
        rowsq.append(dict(supplier=b["supplier_name"], unit=br["unit_price"], as_quoted=br["as_quoted"], ext=ext, foc=foc, flags=flags, src=br["source_ref"]))
        if ext is not None:
            fig(f"Extended at {q:,}, {b['supplier_name']} (USD)", money(ext), br["source_ref"], f"{br['unit_price']} x {q}")
        if foc is not None:
            fig(f"First-order total at {q:,} incl. one-time tooling, {b['supplier_name']} (USD)", money(foc), br["source_ref"], f"{money(ext)} + tooling {money(b['tooling_price'])}")
    priced = [r for r in rowsq if r["unit"] is not None]
    fig(f"Bids priced per unit at break {q:,}", f"{len(priced)} of {len(rowsq)}", "bid records", f"breaks[quantity=={q}].unit_price not null")
    comparison[q] = rowsq

# Indicative: at each supplier's own quoted quantities (NOT a common break, not ranked)
indicative = []
for b in bids:
    for br in b["breaks_as_quoted"]:
        ext = round(br["unit_price"] * br["quantity"], 2)
        foc = round(ext + b["tooling_price"], 2) if b["tooling_price"] is not None else None
        indicative.append(dict(supplier=b["supplier_name"], q=br["quantity"], unit=br["unit_price"], ext=ext, foc=foc, src=br["source_ref"]))
        fig(f"Extended at own quoted qty {br['quantity']:,}, {b['supplier_name']} (USD)", money(ext), br["source_ref"], f"{br['unit_price']} x {br['quantity']} - supplier's own quantity, not a package break")
        if foc is not None:
            fig(f"Own-qty first-order total incl. tooling, {b['supplier_name']} (USD)", money(foc), br["source_ref"], f"{money(ext)} + {money(b['tooling_price'])}")
# coverage of the 3-month requirement by A's 3,000 quote
fig("Shortfall of Alder's 3,000-pc quote against MRP window total (pcs)", total - 3000, "demand.csv + bid_supplier_A.txt", f"{total} - 3000")

# Lead time vs first need (illustrative: if ordered today, ARO)
a_arrive = TODAY + dt.timedelta(weeks=4)
b_lo, b_hi = TODAY + dt.timedelta(weeks=6), TODAY + dt.timedelta(weeks=7)
fig("Alder '4 weeks ARO' if order placed 2026-11-14 (illustrative)", a_arrive.isoformat(), "bid_supplier_A.txt line 3", "today + 28 days; order date is an assumption")
fig("Birch '6-7 weeks' if counted from 2026-11-14 (illustrative)", f"{b_lo.isoformat()} to {b_hi.isoformat()}", "bid_supplier_B.txt line 3", "today + 42/49 days; supplier named no start event")
fig("First MRP requirement month", months[0], "demand.csv", "min(month); no day-of-month in the export")
fig("Required first article date", "not supplied", "inputs", "no first-article date in drawing, demand.csv or request")

# Response tracker: no due date set, no send recorded
fig("Suppliers with a recorded send", 0, "conversation", "buyer has not said any RFQ was sent")
fig("Days past due", "not computable - no response due date set", "package", "due date is a buyer question")

# ---------------- write bid records (.bid.txt, YAML-shaped) ----------------
def yaml_val(v):
    if v is None: return "null"
    if isinstance(v, bool): return "true" if v else "false"
    if isinstance(v, (int, float)): return str(v)
    return json.dumps(v, ensure_ascii=False)
def dump(d, ind=0):
    out = []
    pad = "  " * ind
    for k, v in d.items():
        if isinstance(v, list):
            if not v: out.append(f"{pad}{k}: []"); continue
            out.append(f"{pad}{k}:")
            for it in v:
                if isinstance(it, dict):
                    first = True
                    for kk, vv in it.items():
                        out.append(f"{pad}  {'- ' if first else '  '}{kk}: {yaml_val(vv)}"); first = False
                else:
                    out.append(f"{pad}  - {yaml_val(it)}")
        else:
            out.append(f"{pad}{k}: {yaml_val(v)}")
    return "\n".join(out)
slugs = {"Alder Sintered Parts": "alder-sintered-parts", "Birch Powder Metal": "birch-powder-metal"}
for b in bids:
    p = os.path.join(OUT, "sourcing", EVENT, f"{slugs[b['supplier_name']]}.bid.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write("# Supplier bid record - contract supplier-bid v1. INTERNAL. Mapped, not normalised. SYNTHETIC test data.\n")
        f.write(dump(b) + "\n")

# ---------------- figures block ----------------
with open(os.path.join(OUT, "figures.json"), "w", encoding="utf-8") as f:
    json.dump(dict(figures=figures, breaks=BREAKS,
                   comparison={str(k): v for k, v in comparison.items()}, indicative=indicative), f, indent=1)
print("| Figure | Value | Computed from | Filter or query |\n|---|---|---|---|")
for r in figures:
    print("| " + " | ".join(str(x).replace("|", "/") for x in r) + " |")
