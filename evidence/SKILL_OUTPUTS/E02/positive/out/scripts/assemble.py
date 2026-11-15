"""Assemble quote-build outputs from figures.json and the text templates. python -I assemble.py <out_dir>"""
import json, os, sys, html, re
out = sys.argv[1]; sd = os.path.join(out, "scripts")
d = json.load(open(os.path.join(out, "figures.json"), encoding="utf-8"))
F = {f["figure"]: f["value"] for f in d["figures"]}
fmt2 = lambda v: f"{v:.2f}"
sub = {
 "PIDS": F["CNC part ids in BOM handoff"], "PCS": F["CNC pieces per arm set"], "PCS20": F["CNC pieces for 20 sets"],
 "PRICED_IDS": F["Part ids with a material lower bound"], "PRICED_PCS": F["Pieces per set with a material lower bound"],
 "UNK_IDS": F["Part ids with material unknown"], "UNK_PCS": F["Pieces per set with material unknown"],
 "MAT_SET": (lambda v: f"{v:.4f}")(F["Material lower bound per set, priced parts only (USD)"]), "MAT_20": fmt2(F["Material lower bound, 20 sets, priced parts only (USD)"]),
 "N_ASSETS": F["Assets in equipment list"], "WCS": F["Work centres in equipment list"],
 "N_FORM": F["Assets whose description mentions bend/brake/press/form/sheet"], "N_5AX": F["Assets whose description mentions 5-axis"],
 "MAXDIM": F["Largest bbox dimension, any part (mm)"],
 "P30710": fmt2(F["PO-30710 price per m2 (USD)"]), "P30711": fmt2(F["PO-30711 price per m2 (USD)"]), "P30744": fmt2(F["PO-30744 price per m2 (USD)"]),
 "N_INPUTS": F["Input files enumerated"], "N_HIST": F["Input files that are routings, actuals, work orders, prior quotes or planning exports"],
 "D_TODAY": F["Calendar days, today (2026-11-14) to requested 2027-01-31"], "D_RECV": F["Calendar days, receipt (2026-11-12) to requested 2027-01-31"],
}
leads = {F[k] for k in F if k.endswith("order-to-receipt days")}
assert len(leads) == 1; sub["LEAD"] = leads.pop()
rd = lambda n: open(os.path.join(sd, n), encoding="utf-8").read()
sub["MATERIAL_TABLE"] = open(os.path.join(out, "_material_table.md"), encoding="utf-8").read()
sub["FIGURES_TABLE"] = open(os.path.join(out, "_figures_table.md"), encoding="utf-8").read()
def fill(t):
    for k, v in sub.items(): t = t.replace("{{" + k + "}}", str(v))
    return t
cust = fill(rd("customer_block.md")); internal = fill(rd("internal_block.md"))
# outbound check, in code, on the customer block alone
body = cust.split("=== END ===")[0]
bad = [w for w in ["margin", "routing", "hour", "rung", "first principles", "geometry estimate", "PO-", "148.60", "171.25", "262.80", "Metals Supply", "plant_library", "fusion_default", "probable_standard", "rough order", "USD", "$"] if w.lower() in body.lower()]
assert not bad, bad
assert not re.search(r"ROM", body)
reply = fill(rd("reply_template.md")).replace("{{CUSTOMER_BLOCK}}", cust).replace("{{INTERNAL_BLOCK}}", internal)
assert "{{" not in reply
open(os.path.join(out, "quote-build-reply.md"), "w", encoding="utf-8").write(reply)

# operation record
ops = []
for r in d["material_table"]:
    ops.append({"part": r["part_id"], "revision_priced_to": "v1.1 (reBot_B601_DM_v1.1_20260625.step)", "op_seq": None,
        "op": "machining (operation list not established)" + ("; forming" if r["process"] != "CNC" else ""),
        "work_center": None, "machine_class": None, "rung": 4, "path": "first principles (not quantified)", "cutting_data_basis": None,
        "setup_h": {"low": None, "expected": None, "high": None, "unit": "h"}, "run": {"low": None, "expected": None, "high": None, "unit": "min/pc"},
        "qty_per_set": r["qty_per_arm"], "quantity_breaks_priced": [20], "material": {k: r.get(k) for k in ("stock", "po", "po_date", "blank_mm", "usd_per_pc", "status", "reason")},
        "sources": ["inputs/02_bom_handoff.json", "inputs/purchase_orders_5052.csv", "inputs/equipment.csv"],
        "geometry_estimate": {"document_ref": None, "approval": None, "note": "none in contract form; BOM handoff engineering_verdict Z"},
        "date_derived": "2026-11-14"})
json.dump({"quote": "Q-HARBOR-ROBOTICS-LAB-NOREF-20261112-01", "draft": 1, "inquiry": "NOREF-20261112", "customer": "Harbor Robotics Lab",
    "bid_decision_state": "draft", "gates_passed": [], "rates": {"labor": "not set", "burden": "not set", "margin_rules": "not set", "scrap_costing_basis": "not set"},
    "line_2": {"part": "MGN9-170 linear rail", "qty": 20, "geometry_path": "A", "price": None, "status": "unknown - no PO or supplier quote"},
    "operations": ops, "revision_history": [{"draft": 1, "date": "2026-11-14", "change": "first draft, no prices"}]},
    open(os.path.join(out, "operation-record.json"), "w", encoding="utf-8"), indent=1)

# Sales command-center page (offered, internal)
e = html.escape
page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sales Command Center</title><style>
:root{{--bg:#fff;--fg:#1b1b1b;--mut:#666;--bd:#ddd}}@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#161616;--fg:#eee;--mut:#aaa;--bd:#333}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0 auto;max-width:900px;padding:16px}}
table{{border-collapse:collapse;width:100%}}td,th{{border-bottom:1px solid var(--bd);padding:6px;text-align:left;vertical-align:top}}.m{{color:var(--mut)}}</style></head><body>
<h1>Sales Command Center</h1><p class="m">Internal. Generated 2026-11-14 by quote-build. SYNTHETIC test data. Site: not set (no plant profile).</p>
<h2>Commercial performance for the period</h2><p>No data: no ERP, prior-quote or sales-order export was available in this run ({sub['N_HIST']} of {sub['N_INPUTS']} input files). Quote turnaround, hit rate and unbid book are not computed.</p>
<h2>Open quotes</h2><table><tr><th>Inquiry</th><th>Customer</th><th>Quote</th><th>State</th><th>Blocked on</th></tr>
<tr><td>NOREF-20261112 (intake record: inquiries/harbor-robotics-lab-NOREF-20261112.intake.txt)</td><td>Harbor Robotics Lab</td><td>Q-HARBOR-ROBOTICS-LAB-NOREF-20261112-01, draft 1 (quote-build-reply.md)</td>
<td>Draft, no prices; not released (Gate 4 open); bid decision draft</td><td>Hours (no routing, actuals or confirmed geometry); labour, burden and margin rates not on file; forming and rail unsourced</td></tr></table>
<p>Requested delivery 2027-01-31, not checked against shop load.</p>
<p class="m">Offered page: save it over the previous Sales page wherever that lives. The dashboard was not updated: no publish in this run.</p></body></html>"""
open(os.path.join(out, "sales-command-center.html"), "w", encoding="utf-8").write(page)
for f in ("_material_table.md", "_figures_table.md"): os.remove(os.path.join(out, f))
print("ok", len(reply))
