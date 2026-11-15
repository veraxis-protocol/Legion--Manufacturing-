"""BSH-1210 sourcing event: demand picture, bid ingest (map, never normalise), comparison.

Run from the work folder:  python3 -I out/scripts/compare_bids.py inputs/supplier out
Every figure printed in the RFQ notes / comparison comes from this script's output.
"""
import csv, json, re, sys, datetime as dt
from pathlib import Path

SRC = Path(sys.argv[1]); OUT = Path(sys.argv[2])
TODAY = dt.date(2026, 11, 15)
EVENT = "SRC-2026-11-15-BSH-1210"
BREAKS = [800, 1200, 3200]          # mandated breaks, derived from MRP (see figures)
NOW = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="minutes")
fig = []                             # figures block rows
def F(name, value, frm, flt): fig.append((name, value, frm, flt)); return value

# ---------------- demand ----------------
rows = [r for r in csv.DictReader(l for l in (SRC/"demand.csv").read_text(encoding="utf-8").splitlines() if not l.startswith("#"))]
part = [r for r in rows if r["item"] == "BSH-1210"]
F("MRP rows for BSH-1210", len(part), "demand.csv", 'item == "BSH-1210"')
revs = sorted({r["rev"] for r in part})
F("Revisions on MRP rows", ", ".join(revs), "demand.csv", "distinct rev")
total = F("Total MRP requirement (pcs)", sum(int(r["qty_required"]) for r in part), "demand.csv", "sum qty_required")
months = [r["month"] for r in part]
F("MRP horizon", f"{min(months)} to {max(months)} ({len(months)} months)", "demand.csv", "min/max month")
per = {r["month"]: int(r["qty_required"]) for r in part}
for m, q in per.items(): F(f"Requirement {m} (pcs)", q, "demand.csv", f'month == "{m}"')
F("Largest single month (pcs)", max(per.values()), "demand.csv", "max qty_required")
F("Average per month (pcs)", round(total/len(per), 1), "demand.csv", "total / months")
first_month = min(months)
first_need = dt.date(int(first_month[:4]), int(first_month[5:]), 1)
F("Earliest possible need date (month start, date within month not in export)", first_need.isoformat(), "demand.csv", f'month == "{first_month}"')
F("Historical usage / PO / receipt rows", "0 — none supplied", "inputs folder enumerated", "no usage, PO or receipt file present in ./inputs")
F("Forecast beyond MRP horizon", "none supplied", "inputs folder enumerated", "no forecast/EAU file present")
F("Mandated quantity breaks", ", ".join(map(str, BREAKS)), "demand.csv",
  f"first month ({per[first_month]}), largest month ({max(per.values())}), full horizon ({total})")
assert BREAKS == [per[first_month], max(per.values()), total]

# ---------------- bid ingest ----------------
def lines(p): return (SRC/p).read_text(encoding="utf-8").splitlines()
def find(ls, pat, flags=0):
    for i, l in enumerate(ls, 1):
        m = re.search(pat, l, flags)
        if m: return m, i
    return None, None
num = lambda s: float(s.replace(",", ""))

def base(fname, sid, name):
    return dict(contract_version=1, site="not set (no plant profile)", event_ref=EVENT,
        bid_ref=f"{EVENT}/{sid}/1", supersedes=None, supplier_id="unlisted", supplier_id_verbatim=sid,
        supplier_name=name, approval_status="not_confirmed_approved",
        received_at=None, received_at_note="no date in the file; nothing dates the bid",
        received_via="pasted", source_ref=fname, ingested_at=NOW)

# Supplier A
fa = "bid_supplier_A.txt"; A = lines(fa)
ra = base(fa, "A", "Alder Sintered Parts")
m, ln = find(A, r"Part BSH-1210 rev ([A-Z])"); ra["revision_quoted"] = m.group(1); ra["revision_ref"] = f"{fa}, line {ln}"
m, ln = find(A, r"Quote ([\w-]+), valid (\d+) days"); ra["supplier_quote_no"] = m.group(1)
ra["validity_until"] = None; ra["validity_stated"] = f"valid {m.group(2)} days (from an undated quote; cannot be converted to a date)"; ra["validity_ref"] = f"{fa}, line {ln}"
m, ln = find(A, r"(?i)currency|USD"); ra["currency"] = "USD"
priced = {}
for i, l in enumerate(A, 1):
    for q, p in re.findall(r"([\d,]+) pcs ([\d.]+) USD/ea", l): priced[int(num(q))] = (num(p), f"{q} pcs {p} USD/ea", f"{fa}, line {i}")
m, ln = find(A, r"Lead time ([^.]+)\."); a_lead = m.group(1); a_lead_ref = f"{fa}, line {ln}"
ra["breaks"] = []
for b in BREAKS:
    ra["breaks"].append(dict(quantity=b, uom="each", unit_price=priced[b][0] if b in priced else None,
        as_quoted=priced[b][1] if b in priced else "not priced at this break; quoted breaks: " + "; ".join(v[1] for v in priced.values()),
        lead_time_first_article=None, lead_time_production=None, lead_time_as_quoted=a_lead,
        source_ref=priced[b][2] if b in priced else f"{fa}, line {next(iter(priced.values()))[2].split()[-1]}"))
ra["quoted_breaks_off_request"] = [dict(quantity=q, unit_price=v[0], as_quoted=v[1], source_ref=v[2]) for q, v in priced.items()]
m, ln = find(A, r"Tooling: ([^.]+)\."); ra.update(tooling_price=None, tooling_in_unit_price=None, tooling_ownership=None, tooling_note=f'"Tooling: {m.group(1)}." ({fa}, line {ln}) — no price and no owner stated')
m, ln = find(A, r"MOQ ([\d,]+)"); ra.update(moq=int(num(m.group(1))), moq_uom="each", moq_ref=f"{fa}, line {ln}")
m, ln = find(A, r"(FOB [a-z]+)"); ra["freight_basis"] = m.group(1); ra["freight_ref"] = f"{fa}, line {ln}"
ra["payment_terms"] = None
m, ln = find(A, r"Exceptions: (.+)$")
ra.update(quality_clause_acceptance="not_stated", clause_exceptions=[],
          exceptions=[f'"{m.group(1).strip()}" ({fa}, line {ln}) — drawing requires 25-40 HRF'])
ra["fields_missing"] = [f"unit price at {b} (not priced at this break)" for b in BREAKS if b not in priced] + [
    "lead time, first article, from a named event (only '4 weeks ARO' given, not split)",
    "lead time, production, split from first article",
    "tooling price, or an explicit statement that none is charged ('existing' only)",
    "tooling ownership", "price validity as a date (30 days from an undated quote)",
    "quote date", "quality clause acceptance (certificate of conformance per lot not addressed)",
    "freight cost to our dock (quoted FOB origin)", "payment terms"]
ra.update(conformance="off_format", restatement_requested=True)

# Supplier B
fb = "bid_supplier_B.txt"; B = lines(fb)
rb = base(fb, "B", "Birch Powder Metal")
m, ln = find(B, r"Ref ([\w-]+)"); rb["supplier_quote_no"] = m.group(1)
m, ln = find(B, r"revision (not stated)"); rb["revision_quoted"] = None; rb["revision_ref"] = f'"BSH-1210, revision not stated" ({fb}, line {ln})'
m, ln = find(B, r"Unit price ([\d.]+) USD at ([\d,]+) pcs"); bp = {int(num(m.group(2))): (num(m.group(1)), m.group(0), f"{fb}, line {ln}")}
rb["currency"] = "USD"
m, ln = find(B, r"Lead ([^.]+)\."); b_lead = m.group(1)
rb["breaks"] = [dict(quantity=b, uom="each", unit_price=bp[b][0] if b in bp else None,
    as_quoted=bp[b][1] if b in bp else "not priced at this break",
    lead_time_first_article=None, lead_time_production=None, lead_time_as_quoted=b_lead,
    source_ref=bp[b][2] if b in bp else f"{fb}, line {ln}") for b in BREAKS]
m, ln = find(B, r"Tooling ([\d,]+) USD one time"); rb.update(tooling_price=num(m.group(1)), tooling_in_unit_price=False, tooling_ownership=None, tooling_note=f'"{m.group(0)}" ({fb}, line {ln})')
rb.update(moq=None, moq_uom="each", validity_until=None, validity_stated=None)
m, ln = find(B, r"Delivered (DDP \w+)"); rb["freight_basis"] = m.group(1); rb["freight_ref"] = f"{fb}, line {ln}"
m, ln = find(B, r"Payment (net \d+)"); rb["payment_terms"] = m.group(1)
rb.update(quality_clause_acceptance="not_stated", clause_exceptions=[], exceptions=[])
rb["fields_missing"] = ["drawing revision quoted (stated as 'revision not stated')"] + \
    [f"unit price at {b} (not priced at this break)" for b in BREAKS if b not in bp] + [
    "lead time, first article, from a named event ('6-7 weeks', no start event)",
    "lead time, production, split from first article", "tooling ownership",
    "tooling lead time / first-article sample timing for new tooling",
    "minimum order quantity", "price validity", "quote date",
    "quality clause acceptance (certificate of conformance per lot not addressed)",
    "exceptions (none listed; confirm none)"]
rb.update(conformance="off_format", restatement_requested=True)

bids = [ra, rb]
recdir = OUT/"sourcing"/EVENT; recdir.mkdir(parents=True, exist_ok=True)
for r, slug in ((ra, "alder-sintered-parts"), (rb, "birch-powder-metal")):
    (recdir/f"{slug}.bid.yaml").write_text("# Supplier bid record (contract v1). INTERNAL. JSON is valid YAML.\n" + json.dumps(r, indent=2), encoding="utf-8")
    F(f"fields_missing, {r['supplier_name']}", len(r["fields_missing"]), r["source_ref"], "mandated fields checked one by one")
F("Bids received / suppliers known", f"{len(bids)} of {len(bids)}", "inputs/supplier", "bid_*.txt files")
F("Approved suppliers confirmed", "0 of 2 — no approved supplier table (no plant profile)", "plant profile", "profile_path does not exist")

# ---------------- comparison ----------------
table = {}
for b in BREAKS:
    rowsb = []
    for r in bids:
        br = next(x for x in r["breaks"] if x["quantity"] == b)
        up = br["unit_price"]
        ext = round(up*b, 2) if up is not None else None
        tool = r["tooling_price"]
        first = round(ext + tool, 2) if (ext is not None and tool is not None) else None
        rowsb.append(dict(supplier=r["supplier_name"], unit=up, as_quoted=br["as_quoted"], ext=ext, tooling=tool,
            first_order=first, moq=r["moq"], moq_flag=(r["moq"] is not None and r["moq"] > b),
            lead=br["lead_time_as_quoted"], source=br["source_ref"], currency=r["currency"]))
        if ext is not None: F(f"{r['supplier_name']} extended @ {b}", f"{ext:.2f} USD", br["source_ref"], f"{up} x {b}")
        if first is not None: F(f"{r['supplier_name']} first-order total @ {b} (incl. one-time tooling)", f"{first:.2f} USD", br["source_ref"], f"{ext} + {tool}")
    table[b] = rowsb

# Indicative (NOT ranked): Alder's quoted breaks applied to requirement quantities. Labelled assumption.
a1000, a3000 = priced[1000][0], priced[3000][0]
ind = {}
ind["A_first_release_MOQ"] = F("INDICATIVE Alder first release: MOQ 1,000 x 1,000-pc price", f"{a1000*1000:.2f} USD", fa, "assumes 800 needed but MOQ forces 1,000; excl. freight (FOB origin)")
ind["A_3200_at_3000_price"] = F("INDICATIVE Alder 3,200 pcs at the 3,000-pc price", f"{a3000*3200:.2f} USD", fa, "ASSUMES the 3,000 break applies at 3,200 — not stated; excl. freight and tooling (price not stated)")
b3200_first = table[3200][1]["first_order"]
gap = round(b3200_first - a3000*3200, 2)
F("INDICATIVE gap: Birch first-order total minus Alder indicative @3,200", f"{gap:.2f} USD", "both files", "headroom for Alder freight before Birch is cheaper on the order")
F("Piece-price difference @3,000/3,200 (Alder - Birch)", f"{a3000 - bp[3200][0]:.2f} USD/ea", "both files", "0.55 - 0.49")
be = rb["tooling_price"]/(a3000 - bp[3200][0])
F("Break-even volume for Birch tooling vs Alder piece price", f"{be:,.0f} pcs", "both files", "tooling / piece-price difference; vs 3,200 pcs in MRP horizon")
F("Birch tooling as share of its 3,200 first order", f"{rb['tooling_price']/b3200_first*100:.1f} %", fb, "tooling / first-order total")

# lead time vs need (hypothetical PO today)
def wk(n): return (TODAY + dt.timedelta(weeks=n))
F("Alder arrival if PO placed today (4 wk ARO, transit not stated)", wk(4).isoformat(), fa, "2026-11-15 + 4 weeks")
F("Birch arrival if PO placed today (6-7 wk, start event not stated)", f"{wk(6).isoformat()} to {wk(7).isoformat()}", fb, "2026-11-15 + 6/7 weeks")
F("Days Alder lands after earliest Dec need date", (wk(4)-first_need).days, "computed", "arrival - 2026-12-01")
F("Days Birch lands after earliest Dec need date", f"{(wk(6)-first_need).days} to {(wk(7)-first_need).days}", "computed", "arrival - 2026-12-01")
F("Response tracker: suppliers with a send recorded by the buyer", 0, "conversation", "no send reported; bids predate this package")

# ---------------- write figures + comparison data ----------------
(OUT/"figures.md").write_text("# Figures block — " + EVENT + " (INTERNAL)\n\nProduced by `out/scripts/compare_bids.py`, run " + NOW +
    ". Every number in the package notes and comparison is quoted from here.\n\n| Figure | Value | Computed from | Filter or query |\n|---|---|---|---|\n" +
    "\n".join(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in fig) + "\n", encoding="utf-8")
(OUT/"sourcing"/EVENT/"comparison.json").write_text(json.dumps(dict(table={str(k): v for k, v in table.items()}, figures=fig), indent=2), encoding="utf-8")
for a, b, c, d in fig: print(f"{a} | {b}")
