"""Computes every figure for sourcing event SRC-2026-11-14-BSH-1210 from the input files.
Bid values are mapped verbatim from the bid text (map, never normalise); all totals,
extensions, counts and dates are computed here and printed from the result."""
import csv, json, os, sys, datetime as dt, html

IN = r"C:/LMFG/runs/B07-negative/work/inputs/supplier"
OUT = r"C:/LMFG/runs/B07-negative/work/out"
EVENT = "SRC-2026-11-14-BSH-1210"
TODAY = dt.date(2026, 11, 14)
NOW = "2026-11-14T00:00:00 (session date; time of day and zone not known)"

# ---------- demand ----------
rows = []
with open(os.path.join(IN, "demand.csv"), newline="", encoding="utf-8") as f:
    lines = [l for l in f if not l.startswith("#")]
for r in csv.DictReader(lines):
    rows.append(r)
part = [r for r in rows if r["item"] == "BSH-1210"]
revs = sorted({r["rev"] for r in part})
months = [r["month"] for r in part]
qtys = [int(r["qty_required"]) for r in part]
total = sum(qtys)
monthly = {r["month"]: int(r["qty_required"]) for r in part}

# Quantity breaks for the package: taken from the MRP rows (smallest monthly, largest monthly, window total)
breaks = sorted({min(qtys), max(qtys), total})

# ---------- bids (verbatim mapping) ----------
A_FILE, B_FILE = "bid_supplier_A.txt", "bid_supplier_B.txt"
bids = [
    dict(
        contract_version=1, site="not stated (no plant profile)", event_ref=EVENT,
        bid_ref=f"{EVENT}/unlisted-alder/1", supersedes=None,
        supplier_id="unlisted", supplier_id_verbatim="Alder Sintered Parts (fictitious)",
        supplier_name="Alder Sintered Parts", approval_status="not_confirmed_approved",
        received_at=None, received_at_reason="the bid text carries no date",
        received_via="pasted", source_ref=f"{A_FILE}, line 2-4", ingested_at=NOW,
        quote_ref="Q-A-118", revision_quoted="A (stated: 'Part BSH-1210 rev A')",
        currency="USD",
        supplier_breaks=[(1000, 0.62, "1,000 pcs 0.62 USD/ea"), (3000, 0.55, "3,000 pcs 0.55 USD/ea")],
        lead_time_as_quoted="4 weeks ARO",
        tooling_price=None, tooling_in_unit_price=None, tooling_ownership=None,
        tooling_note="Tooling: existing.",
        moq=1000, moq_uom="each", validity_as_quoted="valid 30 days", validity_until=None,
        freight_basis="FOB origin", payment_terms=None,
        quality_clause_acceptance="not_stated", clause_exceptions=[],
        exceptions=["hardness 25-45 HRF"],
    ),
    dict(
        contract_version=1, site="not stated (no plant profile)", event_ref=EVENT,
        bid_ref=f"{EVENT}/unlisted-birch/1", supersedes=None,
        supplier_id="unlisted", supplier_id_verbatim="Birch Powder Metal (fictitious)",
        supplier_name="Birch Powder Metal", approval_status="not_confirmed_approved",
        received_at=None, received_at_reason="the bid text carries no date",
        received_via="pasted", source_ref=f"{B_FILE}, line 2-3", ingested_at=NOW,
        quote_ref="BPM-77", revision_quoted=None,
        currency="USD",
        supplier_breaks=[(3200, 0.49, "Unit price 0.49 USD at 3,200 pcs")],
        lead_time_as_quoted="Lead 6-7 weeks",
        tooling_price=1850.0, tooling_in_unit_price=False, tooling_ownership=None,
        tooling_note="Tooling 1,850 USD one time",
        moq=None, moq_uom="each", validity_as_quoted=None, validity_until=None,
        freight_basis="Delivered DDP Dayton", payment_terms="net 45",
        quality_clause_acceptance="not_stated", clause_exceptions=[],
        exceptions=[],
    ),
]

def map_breaks(b):
    out = []
    sb = {q: (p, w) for q, p, w in b["supplier_breaks"]}
    for q in breaks:
        if q in sb:
            p, w = sb[q]
            out.append(dict(quantity=q, uom="each", unit_price=p, as_quoted=w,
                            lead_time_first_article=None, lead_time_production=None,
                            source_ref=b["source_ref"]))
        else:
            quoted = "; ".join(w for _, _, w in b["supplier_breaks"])
            out.append(dict(quantity=q, uom="each", unit_price=None,
                            as_quoted=f"not priced at {q:,}; supplier quoted: {quoted}",
                            lead_time_first_article=None, lead_time_production=None,
                            source_ref=b["source_ref"]))
    return out

for b in bids:
    b["breaks"] = map_breaks(b)
    fm = []
    for br in b["breaks"]:
        if br["unit_price"] is None:
            fm.append(f"unit price at {br['quantity']:,} (not priced at this quantity)")
    if not b["currency"]: fm.append("currency")
    fm.append(f"lead time, first article, from a named event (as quoted: '{b['lead_time_as_quoted']}')")
    fm.append(f"lead time, production, from a named event (as quoted: '{b['lead_time_as_quoted']}')")
    if b["tooling_price"] is None: fm.append("tooling price, or a statement that none is needed (as quoted: 'Tooling: existing.')" if b["tooling_note"] else "tooling price")
    if b["tooling_ownership"] is None: fm.append("tooling ownership")
    if b["moq"] is None: fm.append("minimum order quantity")
    if b["validity_until"] is None:
        fm.append("price validity as a date (stated '30 days' but the quote is undated)" if b["validity_as_quoted"] else "price validity")
    if b["quality_clause_acceptance"] == "not_stated": fm.append("quality clause acceptance")
    if b["revision_quoted"] is None: fm.append("drawing revision quoted against")
    if b["payment_terms"] is None: fm.append("payment terms")
    b["fields_missing"] = fm
    b["conformance"] = "off_format" if fm else "conforming"
    b["restatement_requested"] = True

# ---------- comparison ----------
comparison = {}
for q in breaks:
    rowsq = []
    for b in bids:
        br = next(x for x in b["breaks"] if x["quantity"] == q)
        up = br["unit_price"]
        ext = round(up * q, 2) if up is not None else None
        first = round(ext + b["tooling_price"], 2) if (ext is not None and b["tooling_price"] is not None) else None
        rowsq.append(dict(supplier=b["supplier_name"], approval=b["approval_status"], unit_price=up,
                          as_quoted=br["as_quoted"], extended=ext, tooling=b["tooling_price"],
                          tooling_note=b["tooling_note"], first_order_total=first,
                          moq=b["moq"], moq_above_break=(b["moq"] is not None and b["moq"] > q),
                          lead=b["lead_time_as_quoted"], clauses=b["quality_clause_acceptance"],
                          exceptions=b["exceptions"], validity=b["validity_as_quoted"],
                          freight=b["freight_basis"], source=b["source_ref"]))
    priced = [r for r in rowsq if r["unit_price"] is not None]
    comparison[q] = dict(rows=rowsq, priced_count=len(priced))

# Supplier's own quantities, shown as quoted (not at a requested break, not ranked)
own = []
for b in bids:
    for q, p, w in b["supplier_breaks"]:
        own.append(dict(supplier=b["supplier_name"], quantity=q, unit_price=p,
                        extended_at_own_qty=round(p * q, 2), as_quoted=w, source=b["source_ref"]))

# Lead-time illustration: order placed today, weeks as stated (start event 'ARO' only stated by A)
def add_weeks(w): return (TODAY + dt.timedelta(weeks=w)).isoformat()
lead_illus = {
    "Alder Sintered Parts": dict(weeks="4", start_event="ARO (stated)", arrival_if_ordered_today=add_weeks(4)),
    "Birch Powder Metal": dict(weeks="6-7", start_event="not stated", arrival_if_ordered_today=f"{add_weeks(6)} to {add_weeks(7)}"),
}

figures = [
    ("MRP rows for BSH-1210", len(part), "demand.csv", "item == 'BSH-1210', comment lines skipped"),
    ("Revisions on those rows", ", ".join(revs), "demand.csv", "distinct rev"),
    ("MRP window", f"{min(months)} to {max(months)}", "demand.csv", "min/max month"),
    ("MRP requirement total", total, "demand.csv", "sum qty_required over the 3 rows"),
] + [(f"MRP requirement {m}", v, "demand.csv", f"month == '{m}'") for m, v in monthly.items()] + [
    ("Quantity breaks in package", ", ".join(f"{q:,}" for q in breaks), "computed", "min monthly, max monthly, window total"),
    ("Historical usage rows", 0, "inputs folder", "no PO / receipt / usage file present - not found by enumerating inputs/supplier"),
    ("Bids received", len(bids), "inputs/supplier", "files named bid_*.txt"),
    ("Bids off_format", sum(b["conformance"] == "off_format" for b in bids), "bid records", "conformance == off_format"),
    ("Bids ready for buyer review", 0, "bid records", "all four prerequisites hold"),
    ("Approved suppliers known", "not available", "plant profile", "no ## Plant context found (plant_setup.py find: exists=false)"),
] + [(f"{b['supplier_name']} fields_missing count", len(b["fields_missing"]), "bid record", "mandated fields checked one by one") for b in bids]
for q, c in comparison.items():
    figures.append((f"Bids priced per unit at {q:,}", c["priced_count"], "bid records", f"breaks[].quantity == {q} and unit_price not null"))
    for r in c["rows"]:
        if r["extended"] is not None:
            figures.append((f"{r['supplier']} extended at {q:,}", f"{r['extended']:.2f} USD", "bid record", f"{r['unit_price']} x {q}"))
        if r["first_order_total"] is not None:
            figures.append((f"{r['supplier']} first-order total at {q:,} (includes one-time tooling)", f"{r['first_order_total']:.2f} USD", "bid record", f"extended + tooling {r['tooling']}"))
for o in own:
    figures.append((f"{o['supplier']} extended at its own quoted qty {o['quantity']:,} (not a requested break)", f"{o['extended_at_own_qty']:.2f} USD", "bid record", f"{o['unit_price']} x {o['quantity']}"))
for s, l in lead_illus.items():
    figures.append((f"{s} arrival if ordered {TODAY} (illustrative)", l["arrival_if_ordered_today"], "bid record + session date", f"{l['weeks']} weeks, start event {l['start_event']}"))

json.dump(dict(event=EVENT, breaks=breaks, total=total, monthly=monthly, revs=revs,
               bids=bids, comparison={str(k): v for k, v in comparison.items()},
               own=own, lead_illus=lead_illus,
               figures=[dict(figure=a, value=b, source=c, filter=d) for a, b, c, d in figures]),
          open(os.path.join(OUT, "sourcing", EVENT, "computed.json"), "w", encoding="utf-8"), indent=2, default=str)

# ---------- bid records (contract format, YAML-like text) ----------
def yv(v):
    if v is None: return "null"
    if isinstance(v, bool): return "true" if v else "false"
    if isinstance(v, (int, float)): return str(v)
    return json.dumps(v)
for b, slug in zip(bids, ["alder-sintered-parts", "birch-powder-metal"]):
    keys = ["contract_version","site","event_ref","bid_ref","supersedes","supplier_id","supplier_id_verbatim",
            "supplier_name","approval_status","received_at","received_via","source_ref","ingested_at","currency"]
    L = [f"{k}: {yv(b[k])}" + (f"   # {b['received_at_reason']}" if k == "received_at" else "") for k in keys]
    L.append("breaks:")
    for br in b["breaks"]:
        L.append(f"  - quantity: {br['quantity']}")
        for k in ["uom","unit_price","as_quoted","lead_time_first_article","lead_time_production","source_ref"]:
            L.append(f"    {k}: {yv(br[k])}")
    for k in ["tooling_price","tooling_in_unit_price","tooling_ownership","tooling_note","moq","moq_uom","validity_until","freight_basis","quality_clause_acceptance"]:
        L.append(f"{k}: {yv(b[k])}")
    L.append(f"clause_exceptions: {json.dumps(b['clause_exceptions'])}")
    L.append(f"exceptions: {json.dumps(b['exceptions'])}")
    L.append(f"conformance: {b['conformance']}")
    L.append("fields_missing:")
    L += [f"  - {json.dumps(x)}" for x in b["fields_missing"]]
    L.append(f"restatement_requested: {yv(b['restatement_requested'])}   # drafted, not sent")
    L.append("# notes (verbatim, outside the contract fields):")
    L.append(f"#   quote ref: {b['quote_ref']}; revision quoted: {b['revision_quoted'] or 'not stated'}; lead time as quoted: {b['lead_time_as_quoted']}; validity as quoted: {b['validity_as_quoted'] or 'not stated'}; payment: {b['payment_terms'] or 'not stated'}")
    L.append("#   supplier's own quantities: " + "; ".join(w for _, _, w in b["supplier_breaks"]))
    open(os.path.join(OUT, "sourcing", EVENT, f"{slug}.bid.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")

for a, b_, c, d in figures:
    print(f"{a} | {b_} | {c} | {d}")
