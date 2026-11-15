"""Builds sourcing-output/bid-comparison.html from computed.json (every number printed from the computation)."""
import json, html, os
OUT = r"C:/LMFG/runs/B07-negative/work/out"
EV = "SRC-2026-11-14-BSH-1210"
d = json.load(open(os.path.join(OUT, "sourcing", EV, "computed.json"), encoding="utf-8"))
e = html.escape
def money(v): return "not stated" if v is None else f"{v:,.2f} USD"
def up(v): return "not quoted per unit" if v is None else f"{v:.2f} USD"

readiness = {
 "Alder Sintered Parts": "provisional: not priced at 800, 1,200 or 3,200; MOQ 1,000; lead time not split FA/production; tooling 'existing' with no price or ownership; clauses not stated; hardness exception 25-45 HRF open; not confirmed approved",
 "Birch Powder Metal": "provisional: drawing revision not stated; not priced at 800 or 1,200; lead time 6-7 weeks with no start event; MOQ, validity, tooling ownership not stated; clauses not stated; not confirmed approved",
}

tables = []
for q in d["breaks"]:
    c = d["comparison"][str(q)]
    rows = []
    for r in c["rows"]:
        moq = "not stated" if r["moq"] is None else f"{r['moq']:,}" + (" <b class=crit>MOQ above break: price does not buy this quantity</b>" if r["moq_above_break"] else "")
        tool = money(r["tooling"]) if r["tooling"] is not None else f"not stated ('{e(r['tooling_note'] or '')}')"
        rows.append("<tr>" + "".join(f"<td>{x}</td>" for x in [
            e(r["supplier"]), "not confirmed approved",
            up(r["unit_price"]) + ("" if r["unit_price"] is not None else f"<br><small>{e(r['as_quoted'])}</small>"),
            money(r["extended"]) if r["extended"] is not None else "not quoted per unit",
            tool,
            money(r["first_order_total"]) + (" <small>(includes one-time tooling)</small>" if r["first_order_total"] is not None else "") if r["first_order_total"] is not None else "n/a",
            moq, e(r["lead"]) + " <small>(FA / production split not stated)</small>",
            "not stated", e("; ".join(r["exceptions"]) or "none listed"),
            e(r["validity"] or "not stated"), e(r["freight"] or "not stated"),
            e(readiness[r["supplier"]]), e(r["source"])]) + "</tr>")
    tables.append(f"<h3>Break: {q:,} each</h3><p>{c['priced_count']} of {len(c['rows'])} bids priced per unit at this quantity.</p>"
                  "<div class=scroll><table><tr><th>Supplier</th><th>Approval</th><th>Unit price</th><th>Extended (unit × qty)</th><th>Tooling</th><th>First-order total</th><th>MOQ</th><th>Lead time</th><th>Clauses</th><th>Exceptions</th><th>Validity</th><th>Freight basis</th><th>Readiness</th><th>Source</th></tr>"
                  + "".join(rows) + "</table></div>")

own = "".join(f"<tr><td>{e(o['supplier'])}</td><td>{o['quantity']:,}</td><td>{o['unit_price']:.2f} USD</td><td>{o['extended_at_own_qty']:,.2f} USD</td><td>{e(o['as_quoted'])}</td><td>{e(o['source'])}</td></tr>" for o in d["own"])
figs = "".join(f"<tr><td>{e(str(f['figure']))}</td><td>{e(str(f['value']))}</td><td>{e(f['source'])}</td><td>{e(f['filter'])}</td></tr>" for f in d["figures"])
recs = "".join(f"<tr><td>{e(b['supplier_name'])}</td><td>{e(b['source_ref'])}</td><td>{e('; '.join(w for _,_,w in b['supplier_breaks']))}</td><td>{b['conformance']}</td><td>{e('; '.join(b['fields_missing']))}</td></tr>" for b in d["bids"])
lead = "".join(f"<li>{e(k)}: {e(v['weeks'])} weeks, start event {e(v['start_event'])}; if ordered {e('2026-11-14')}: {e(v['arrival_if_ordered_today'])} (illustrative; no first article date or qualification time included)</li>" for k, v in d["lead_illus"].items())

drafts = "<div class=card><pre>" + e(open(os.path.join(OUT, "scripts", "drafts.txt"), encoding="utf-8").read()) + "</pre></div>"
B = next(r for r in d["comparison"][str(d["total"])]["rows"] if r["supplier"] == "Birch Powder Metal")

page = f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>BSH-1210 Bid Comparison</title>
<style>
:root{{--ink:#1A1D21;--paper:#F2F3F5;--paper-raised:#FFFFFF;--line:#D6D9DD;--accent:#1F5C8B;--accent-soft:#E4EDF4;--good:#2E7248;--warn:#A8641A;--warn-soft:#F7EBDA;--critical:#A93226;--critical-soft:#F9E9E7;
--font-display:'IBM Plex Sans Condensed','Arial Narrow',sans-serif;--font-body:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,sans-serif;--font-mono:'IBM Plex Mono',Consolas,monospace}}
body{{background:var(--paper);color:var(--ink);font-family:var(--font-body);margin:0;padding:16px;max-width:1200px;margin:auto;font-size:14px}}
h1,h2,h3{{font-family:var(--font-display)}} h1{{font-size:22px}}
.card{{background:var(--paper-raised);border:1px solid var(--line);padding:12px 16px;margin:12px 0}}
.crit{{color:var(--critical)}} .warnbox{{background:var(--warn-soft);border-left:4px solid var(--warn)}} .critbox{{background:var(--critical-soft);border-left:4px solid var(--critical)}}
table{{border-collapse:collapse;width:100%;background:var(--paper-raised)}} td,th{{border:1px solid var(--line);padding:4px 6px;vertical-align:top;text-align:left}} th{{background:var(--accent-soft)}}
.scroll{{overflow-x:auto}} pre{{white-space:pre-wrap;font-family:var(--font-mono);font-size:12px;background:var(--paper);padding:8px}}
</style></head><body>
<h1>BSH-1210 bid comparison — {EV}</h1>
<p>Internal. Synthetic test data. Nothing on this page has been sent to any supplier, and nothing has been awarded or ordered.</p>

<div class="card critbox"><h2>Provisional recommendation</h2>
<p><b>No bid is ready for buyer review (0 of {len(d['bids'])}). Recommendation: request restatement from both suppliers against the RFQ package, once the drawing revision is confirmed.</b></p>
<p>Birch Powder Metal is the only bid priced per unit at the {d['total']:,}-piece MRP requirement ({B['unit_price']:.2f} USD, extended {B['extended']:,.2f} USD; {B['first_order_total']:,.2f} USD first-order total including {B['tooling']:,.2f} USD one-time tooling), but it does not state the drawing revision it quoted, gives "6-7 weeks" with no start event, and leaves MOQ, validity and tooling ownership unstated.
Alder Sintered Parts quoted rev A with existing tooling and "4 weeks ARO", but priced 1,000 and 3,000 rather than the required quantities, has an MOQ of 1,000 above the 800 December bucket, and takes an exception on hardness (25-45 HRF) that cannot be judged without the drawing.
Main tradeoff: Birch's lower per-piece price at the full requirement against its tooling charge, unstated revision and longer lead time; Alder's existing tooling and shorter lead time against its hardness exception and off-quantity pricing.</p>
<p><b>Open before any award:</b> drawing revision unverified (no drawing, no ERP item master); both suppliers not confirmed approved; quality clauses and commercial terms not issued, so neither bid accepts them; freight bases differ (FOB origin vs DDP Dayton) and are not comparable; first article date not set; neither quote is dated, so validity cannot be converted to a date.</p></div>

<div class="card warnbox"><h2>Next step</h2><p><b>Ask both suppliers to restate against the package, look into other suppliers, or pursue one of these bids?</b> Choosing one is a preference about what to do next, not a selection or an award.</p></div>

<h2>Comparison per quantity break</h2>
<p>Breaks are taken from the MRP export: smallest monthly bucket, largest monthly bucket, and the window total. Missing is <i>not stated</i>, never zero. Both bids are USD.</p>
{''.join(tables)}
<h3>As quoted at the suppliers' own quantities (not requested breaks, not ranked)</h3>
<table><tr><th>Supplier</th><th>Qty</th><th>Unit</th><th>Extended at that qty</th><th>As quoted</th><th>Source</th></tr>{own}</table>
<p>No interpolation between quantities is made. Alder's 3,000-piece price is not applied to 3,200.</p>
<p><b>Responses:</b> 2 bids in hand. No other supplier is known to have been asked; there is no send history to compute days past due against, and no due date has been set.</p>

<h2>Draft supplier emails — not sent</h2>
{drafts}

<details><summary><b>Detail: readiness evidence</b></summary><div class=card>
<p>Four prerequisites per bid: (1) cost comparable, (2) supplier approved, (3) delivery evidenced against the first article date, (4) technical and quality terms accepted.</p>
<ul><li><b>Alder Sintered Parts</b>: (1) no — not priced at 800/1,200/3,200, tooling not priced; (2) no — not confirmed approved, no approved list on file; (3) not evidenced — no first article date set; lead time not split; (4) no — clauses not stated; exception on hardness 25-45 HRF.</li>
<li><b>Birch Powder Metal</b>: (1) partial — priced at 3,200 only, MOQ not stated; (2) no — not confirmed approved; (3) not evidenced — no first article date, no start event; (4) no — clauses not stated; revision not stated.</li></ul>
<p>Lead time illustration:</p><ul>{lead}</ul>
<p>The December MRP bucket gives a month, not a day, so whether either arrival meets it cannot be determined.</p></div></details>
<details><summary><b>Detail: bid records summary</b></summary><table><tr><th>Supplier</th><th>Source</th><th>Prices as quoted</th><th>conformance</th><th>fields_missing</th></tr>{recs}</table>
<p>Full records: sourcing/{EV}/alder-sintered-parts.bid.txt, sourcing/{EV}/birch-powder-metal.bid.txt</p></details>
<details><summary><b>Detail: figures block</b></summary><table><tr><th>Figure</th><th>Value</th><th>Computed from</th><th>Filter or query</th></tr>{figs}</table>
<p>Computed by scripts/compute_bsh1210.py over the input files.</p></details>
<p>Offered page: save it over the last BSH-1210 comparison, if there is one. The dashboard was not updated: no artifact tools in this run.</p>
</body></html>"""
open(os.path.join(OUT, "sourcing-output", "bid-comparison.html"), "w", encoding="utf-8").write(page)
print("ok", len(page))
