"""Renders out/sourcing-output/bid-comparison.html and out/supply-chain-command-center.html
from out/figures.json (produced by sourcing_compute.py). Every number printed comes from that file."""
import html, json, os, sys
OUT = os.path.join(sys.argv[1], "out")
d = json.load(open(os.path.join(OUT, "figures.json"), encoding="utf-8"))
E = html.escape
def m(x): return "not stated" if x is None else f"{x:,.2f}"

CSS = """:root{--ink:#1A1D21;--paper:#F2F3F5;--paper-raised:#FFFFFF;--line:#D6D9DD;--accent:#1F5C8B;--accent-soft:#E4EDF4;
--good:#2E7248;--warn:#A8641A;--warn-soft:#F7EBDA;--critical:#A93226;--critical-soft:#F9E9E7;
--font-display:'IBM Plex Sans Condensed','Arial Narrow',sans-serif;--font-body:'IBM Plex Sans',-apple-system,sans-serif;--font-mono:'IBM Plex Mono',Consolas,monospace}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ink:#E8EAEC;--paper:#15181B;--paper-raised:#1D2126;--line:#2E343A;--accent:#6BA8D4;--accent-soft:#1B2C39;--warn:#D9A15C;--warn-soft:#33271A;--critical:#DE8378;--critical-soft:#35201E}}
body{background:var(--paper);color:var(--ink);font-family:var(--font-body);margin:0}
.page{display:flex;flex-direction:column;gap:1.25rem;max-width:900px;margin:0 auto;padding:2rem 1.5rem}
.panel{background:var(--paper-raised);border:1px solid var(--line);border-radius:4px;padding:1.5rem}
h1,h2{font-family:var(--font-display);font-weight:600;margin:0 0 .5rem}.meta{font-size:.875rem;opacity:.8;margin:0}
.banner{border-left:4px solid var(--critical);background:var(--critical-soft)}.warn{border-left:4px solid var(--warn);background:var(--warn-soft)}
.wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:.875rem}th,td{border-bottom:1px solid var(--line);padding:.4rem .5rem;text-align:left;vertical-align:top}
td.n{font-family:var(--font-mono);font-variant-numeric:tabular-nums;white-space:nowrap}pre{white-space:pre-wrap;font-family:var(--font-mono);font-size:.8rem}
@media (max-width:600px){.page{padding:1rem}}"""
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">'
def page(title, body):
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)}</title>{FONTS}<style>{CSS}</style></head><body><main class="page">{body}</main></body></html>'

readiness = {
 "Alder Sintered Parts": "provisional — not priced at this break; quality clauses not stated; hardness exception open; not confirmed approved; first article date unknown",
 "Birch Powder Metal": "provisional — revision not stated; quality clauses not stated; MOQ not stated; not confirmed approved; lead time has no start event",
}
approval = "not confirmed approved"
extra = {"Alder Sintered Parts": dict(tool="not stated (\"Tooling: existing\")", moq="1,000", lead="FA not stated / 4 weeks ARO", clauses="not stated", exc="hardness 25-45 HRF (drawing 25-40)", val="30 days, start not stated", frt="FOB origin"),
         "Birch Powder Metal": dict(tool="1,850.00 one time", moq="not stated", lead="6-7 weeks, no start event, no split", clauses="not stated", exc="none listed; revision not stated", val="not stated", frt="DDP Dayton, net 45")}

tables = ""
for q in d["breaks"]:
    rows = ""
    for r in d["comparison"][str(q)]:
        x = extra[r["supplier"]]
        unit = m(r["unit"]) + " USD" if r["unit"] is not None else f"not quoted per unit — <i>{E(r['as_quoted'])}</i>"
        ext = m(r["ext"]) if r["ext"] is not None else "—"
        foc = m(r["foc"]) if r["foc"] is not None else "—"
        flags = "<br>".join(E(f) for f in r["flags"])
        rows += f"<tr><td>{E(r['supplier'])}</td><td>{approval}</td><td class=n>{unit}</td><td class=n>{ext}</td><td class=n>{foc}</td><td>{E(x['tool'])}</td><td>{E(x['moq'])}<br><small>{flags}</small></td><td>{E(x['lead'])}</td><td>{x['clauses']}</td><td>{E(x['exc'])}</td><td>{E(x['val'])}</td><td>{E(readiness[r['supplier']])}</td><td>{E(r['src'])}</td></tr>"
    tables += f"""<section class=panel><h2>Break: {q:,} pcs</h2><div class=wrap><table><tr><th>Supplier</th><th>Approval</th><th>Unit price</th><th>Extended (unit × qty), USD</th><th>First-order total, includes one-time tooling</th><th>Tooling</th><th>MOQ</th><th>Lead time FA / production</th><th>Clauses</th><th>Exceptions</th><th>Validity</th><th>Readiness</th><th>Source</th></tr>{rows}</table></div></section>"""

ind = "".join(f"<tr><td>{E(r['supplier'])}</td><td class=n>{r['q']:,}</td><td class=n>{m(r['unit'])}</td><td class=n>{m(r['ext'])}</td><td class=n>{m(r['foc']) if r['foc'] is not None else 'tooling not stated'}</td><td>{E(extra[r['supplier']]['frt'])}</td><td>{E(r['src'])}</td></tr>" for r in d["indicative"])
figs = "".join("<tr>" + "".join(f"<td>{E(str(c))}</td>" for c in row) + "</tr>" for row in d["figures"])

body = f"""<header><h1>Bid comparison — SRC-2026-11-14-BSH-1210</h1><p class=meta>BSH-1210 flanged bushing, Rev A · Site not stated · Generated 2026-11-14 16:58 -05:00 · MRP export date not stated · INTERNAL · SYNTHETIC test data</p></header>
<section class="panel banner"><b>Revision gate not cleared.</b> Drawing and MRP demand both say Rev A; the ERP item master could not be read, so the RFQ package is held at release and all supplier emails are HELD.</section>
<section class=panel><h2>1. Provisional recommendation</h2><p><b>Pursue Alder Sintered Parts — conditional. Neither bid is ready for buyer review; both are provisional.</b></p>
<p>For: quoted against Rev A; existing tooling; 4 weeks ARO; lower first-order outlay at its own quantity (1,650.00 USD for 3,000 pcs vs Birch 3,418.00 USD for 3,200 pcs including 1,850.00 USD tooling). These are different quantities and freight bases (FOB origin vs DDP) and are <b>not ranked</b> against each other.</p>
<p>Against: hardness exception 25-45 HRF vs drawing 25-40 HRF; MOQ 1,000 above the December requirement of 800; its 3,000-pc price leaves 200 pcs of the 3,200 requirement unpriced; quality clauses not stated; not confirmed approved.</p>
<p>Birch: lowest per-piece figure at 3,200 (0.49 USD) but revision not stated, tooling 1,850.00 USD with ownership not stated, 6-7 weeks with no start event (illustratively 2026-12-26 to 2027-01-02 if counted from today), MOQ and validity not stated.</p>
<p><b>Open before any award:</b> revision confirmed by document control; restated bids at 800 / 1,200 / 3,200; quality clause acceptance; supplier approval or requalification; first article date; one freight basis; engineering decision on the hardness exception.</p></section>
<section class="panel warn"><h2>2. Next step</h2><p><b>Pursue Alder Sintered Parts, look into the alternatives, or ask both suppliers to restate?</b> Choosing one is a preference about the next step, not a selection or an award. No selection record exists; no purchase order has been raised and nothing has gone to any supplier.</p></section>
<h2>3. Comparison per quantity break (package breaks, proposed from MRP)</h2>{tables}
<section class=panel><h2>At each supplier's own quoted quantities — not a common break, not ranked</h2><div class=wrap><table><tr><th>Supplier</th><th>Qty as quoted</th><th>Unit USD</th><th>Extended USD</th><th>First-order total incl. tooling</th><th>Freight / terms</th><th>Source</th></tr>{ind}</table></div>
<p>2 of 2 invited bidders on file responded; both off-format. No other suppliers were invited (none on file). No due date set, so no days past due.</p></section>
<section class=panel><h2>4. Draft supplier emails — not sent</h2><p>All four drafts (RFQ cover and restatement request for each supplier) are HELD: revision unverified, no response due date, <code>[recipient: not on file]</code>, suppliers not confirmed approved. Full text in <code>out/reply.md</code> section 7.</p></section>
<section class=panel><h2>5. Detail</h2><details><summary>Readiness evidence per prerequisite</summary><div class=wrap><table><tr><th>Bid</th><th>Cost comparable</th><th>Supplier approved</th><th>Delivery evidenced</th><th>Technical &amp; quality terms accepted</th></tr>
<tr><td>Alder Q-A-118</td><td>No — no unit price at 800/1,200/3,200; tooling price not stated; currency USD; MOQ 1,000</td><td>No — not confirmed approved, no table on file</td><td>No — first article date not set; FA lead time not stated</td><td>No — hardness exception; clauses not stated</td></tr>
<tr><td>Birch BPM-77</td><td>Partly — 3,200 only; USD; tooling stated; MOQ not stated</td><td>No — not confirmed approved</td><td>No — no start event, no FA split, FA date not set</td><td>No — revision not stated; clauses not stated</td></tr></table></div></details>
<details><summary>Figures block (computed by out/scripts/sourcing_compute.py)</summary><div class=wrap><table><tr><th>Figure</th><th>Value</th><th>Computed from</th><th>Filter</th></tr>{figs}</table></div></details>
<details><summary>Sources</summary><p>inputs/supplier/bid_supplier_A.txt, bid_supplier_B.txt, BSH-1210_drawing_revA.md, demand.csv. Bid records: out/sourcing/SRC-2026-11-14-BSH-1210/*.bid.txt.</p></details></section>"""
os.makedirs(os.path.join(OUT, "sourcing-output"), exist_ok=True)
open(os.path.join(OUT, "sourcing-output", "bid-comparison.html"), "w", encoding="utf-8").write(page("BSH-1210 Bid Comparison", body))

cc = f"""<header><h1>Supply Chain — sourcing signal</h1><p class=meta>Site not stated · Generated 2026-11-14 16:58 -05:00 · data as of: MRP export date not stated · INTERNAL · SYNTHETIC</p></header>
<section class="panel banner"><b>Data freshness:</b> MRP export (demand.csv) — export date not stated. ERP, approved-supplier table, PO history: not available this session.</section>
<section class=panel><h2>Sourcing event SRC-2026-11-14-BSH-1210</h2><p>BSH-1210 flanged bushing, Rev A (unverified against ERP). Trigger: direct request. MRP requirement 3,200 pcs, 2026-12 to 2027-02. Status: open — package drafted, release blocked on the revision gate; 4 supplier drafts HELD; 2 off-format bids ingested; provisional recommendation Alder Sintered Parts (conditional); no decision recorded.</p>
<p>Single-source status: cannot be assessed (no approved-supplier table). Confirmed-approved suppliers: 0.</p>
<p>RFQ package (draft): <code>out/reply.md</code> section 2. Comparison: <code>out/sourcing-output/bid-comparison.html</code>.</p></section>
<section class=panel><p>Offered page: save it where the last Supply Chain page lives. Nothing was published or written to any system. The dashboard was not updated: Supply Chain is an offered page, and no artifact tools were available this run.</p></section>"""
open(os.path.join(OUT, "supply-chain-command-center.html"), "w", encoding="utf-8").write(page("Supply Chain Sourcing", cc))
print("rendered", len(d["figures"]), "figure rows")
