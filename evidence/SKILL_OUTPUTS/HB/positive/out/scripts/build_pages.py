# Builds the HTML work-up page and the bid comparison page from figures.json (numbers printed, never retyped).
import json, os, sys, html
W = sys.argv[1]; O = os.path.join(W, 'out')
D = json.load(open(os.path.join(O, 'figures.json')))
F = D['figures']; P = D['positions']; M = {m['part_id']: m for m in D['material']}; S = D['stock']
X = F['rail_bids']['X']; Y = F['rail_bids']['Y']
e = html.escape

CSS = """
:root{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#5f5e58;--line:#dedbd2;--card:#ffffff;--accent:#2f5d8a;--warn:#9a5b00;--bad:#a23b2a;--ok:#2d6a3e;--code:#f2efe8}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#17181a;--fg:#e9e7e1;--muted:#a3a19a;--line:#33353a;--card:#1f2124;--accent:#8db4dc;--warn:#e0a54a;--bad:#e2806f;--ok:#7cc18e;--code:#25272b}}
:root[data-theme="dark"]{--bg:#17181a;--fg:#e9e7e1;--muted:#a3a19a;--line:#33353a;--card:#1f2124;--accent:#8db4dc;--warn:#e0a54a;--bad:#e2806f;--ok:#7cc18e;--code:#25272b}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px 64px}h1{font-size:1.6rem;margin:.2em 0}h2{font-size:1.2rem;margin-top:2em;border-bottom:1px solid var(--line);padding-bottom:.3em}h3{font-size:1rem;margin-top:1.4em}
.muted{color:var(--muted)}.banner{border:1px solid var(--line);border-left:4px solid var(--warn);background:var(--card);padding:12px 14px;margin:12px 0}
.tbl{overflow-x:auto;margin:8px 0}table{border-collapse:collapse;width:100%;font-size:13px;background:var(--card)}th,td{border:1px solid var(--line);padding:5px 7px;text-align:left;vertical-align:top}th{background:var(--code)}
td.n{text-align:right;font-variant-numeric:tabular-nums}.T{color:var(--ok);font-weight:600}.Z{color:var(--warn);font-weight:600}.F{color:var(--bad);font-weight:600}
pre{background:var(--code);border:1px solid var(--line);padding:12px;white-space:pre-wrap;font-size:13px}code{background:var(--code);padding:0 3px}
details{margin:8px 0}summary{cursor:pointer;color:var(--accent)}
"""
def table(head, rows, num=()):
    h = ''.join('<th>%s</th>' % e(str(x)) for x in head)
    b = ''
    for r in rows:
        b += '<tr>' + ''.join('<td%s>%s</td>' % (' class="n"' if i in num else '', c if isinstance(c, str) and c.startswith('<') else e(str(c))) for i, c in enumerate(r)) + '</tr>'
    return '<div class="tbl"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (h, b)
def v(x): return '<span class="%s">%s</span>' % (x, x)

QUESTIONS = """Subject: RE: RFQ - CNC aluminium part sets for reBot B601 DM arm (v1.1 STEP)

Hello Lena,

Thank you for the RFQ for 20 sets of the reBot B601 DM CNC parts. We have read the STEP file and the
project readme: we count 21 different CNC parts, 31 pieces per arm, and the counts in the model agree
with the readme. Before we can give you a firm price we need a few answers. Numbered so you can reply inline.

1. Revision. We will price to reBot_B601_DM_v1.1_20260625.step as sent. The readme notes the published
   BOM is not the final version and that tolerances may be adjusted later. Is v1.1 frozen for this order,
   or do you expect a change before 31 January?

2. Tolerances. The readme gives "Key dimension tolerance: ±0.02 mm GB/T1840-M" but does not say which
   dimensions are key, and the model itself carries no tolerances. Could you tell us, per part, which
   dimensions or features are key (a marked-up screenshot or a short list is fine), and confirm the
   general tolerance standard and class you want for every other dimension? Please also confirm the
   standard designation, which is written "GB/T1840-M" in the readme.

3. Fits. The readme recommends H7 / interference fits for mating parts. Which bores or pins does that
   apply to (for example the bearing seats for the 6707ZZ, 6803ZZ and AXK5578 bearings)?

4. Finish. You say anodize is not required; the readme lists "Anodizing / Sandblasting". Should the parts
   ship as machined and deburred, or do you want them sandblasted?

5. Formed parts. Link 1, Link 2 (x2), Link 3 Left, Link 3 Right and Link 5 are listed as "CNC + Sheet
   Metal" and the model shows them already formed. Could you send the flat patterns, or confirm the sheet
   thickness and bend radii you expect?

6. Material. The readme says Aluminum Alloy 5052 without a temper. Is 5052-H32 acceptable, and do you need
   material certificates with the parts?

7. Linear rail. You asked for one MGN9 170 mm rail per arm. Do you need the rail only, or also the MGN9
   carriages (the readme lists two slider blocks per arm)? Is there an accuracy class or a length
   tolerance on the 170 mm? Rail suppliers' minimum order quantities are well above 20 pieces, so please
   also tell us whether you would rather source the rails yourselves.

8. Inspection and paperwork. What inspection record do you need per set (for example a certificate of
   conformance, or a dimensional report on the key dimensions)?

9. Delivery and terms. Delivery by 31 January 2027 to which address? Do you have preferences for freight,
   packaging (kitted per arm set?), and payment terms, and is there a date by which you need our quote?
   Please also confirm that all 21 parts are wanted in aluminium, including the three the readme says
   can be 3D printed (Motor 1 Bearing Mount, Motor 2-5 Front Spacer, Gripper Slider Metal Bracket).

Best regards,
[estimator name]
"""
open(os.path.join(O, 'open-questions-HRL-REBOT-20261112.eml.txt'), 'w', encoding='utf-8').write(QUESTIONS)

# ---------- BOM table
bom_rows = []
for n, q in enumerate(P, 1):
    bom_rows.append([n, q['part_id'], q['description'], q['process'], q['qty_readme'], q['qty_legion'], q['step_product'],
                     q['qty_step'], '%s / %s' % (q['faces_legion'], q['faces_step_text']), 'yes' if q['qty_agree'] else 'NO', q['qty_20_sets'],
                     ' x '.join('%g' % x for x in q['bbox_legion_mm']), 'readme.md:L%d' % q['readme_line']])
bom_tbl = table(['Line', 'Part (readme file stem)', 'Description', 'Process', 'Qty/arm readme', 'Qty/arm LEGION', 'STEP product', 'Qty/arm STEP (text read)',
                 'Faces LEGION / text read', 'Qty agree', 'Qty for 20 sets', 'Bbox mm (LEGION XCAF)', 'Source'], bom_rows, num=(0, 4, 5, 7, 10))

# ---------- material table
mat_rows = []
for q in P:
    m = M[q['part_id']]
    if m['status'] == 'lower_bound':
        mat_rows.append([q['part_id'], m['qty_per_set'], '%g' % m['min_bbox_dim_mm'], '%s (%s, %s)' % (m['stock'], m['stock_po'], m['stock_po_date']),
                         '%g' % m['thickness_margin_mm'] + (' - fits only without cleanup' if m['fits_only_without_cleanup'] else ''),
                         '%g' % m['footprint_mm2'], '%.2f' % m['usd_per_piece_lb'], '%.2f' % m['usd_per_set_lb'], 'lower bound'])
    else:
        mat_rows.append([q['part_id'], m['qty_per_set'], '%g' % m['min_bbox_dim_mm'], '-', '-', '%g' % m['footprint_mm2'], '-', '-', 'BLOCKED: ' + m['reason']])
mat_tbl = table(['Part', 'Qty/set', 'Smallest bbox dim mm', 'Candidate stock (PO, date) - assumption for Gate 3', 'Thickness margin mm', 'Footprint mm2',
                 'USD/pc material, lower bound', 'USD/set, lower bound', 'Status'], mat_rows, num=(1, 2, 5, 6, 7))
stock_tbl = table(['PO', 'PO date', 'Received', 'Item', 'Description', 'Unit price USD', 'USD per m2 (computed)'],
                  [[s['po'], s['date'], s['received'], s['item'], s['description'], '%.2f' % s['unit_price'], '%.2f' % s['usd_per_m2']] for s in S], num=(5, 6))

# ---------- bids
def bidrow(b):
    return [b['supplier'], b['ref'], 'not on any approved list (no ASL on file)', '%.2f %s' % (b['unit'], b['currency']) + (' (quoted at %d pcs)' % b['qty_quoted'] if b['qty_quoted'] else ' (each, no quantity named)'),
            '%d - above the 20 needed' % b['moq'], '%.2f' % b['min_commitment_usd'], '%d rails / %.2f' % (b['excess_units_at_moq'], b['excess_cost_at_moq_usd']),
            '%.2f (derived, not quoted)' % b['moq_spend_per_needed_rail_derived'], b['lead'], b['incoterm'], b['accuracy'] + '; cut tolerance ' + b['cut_tol'],
            b['scope'], b['validity'], 'provisional', b['file']]
bid_head = ['Supplier', 'Ref', 'Approval', 'Unit price as quoted', 'MOQ', 'Spend at MOQ USD (unit x MOQ)', 'Excess over 20 at MOQ (units / USD)',
            'MOQ spend / 20 needed rails USD', 'Lead time', 'Freight basis', 'Accuracy / length tol.', 'Scope', 'Validity', 'Readiness', 'Source']
bid_tbl = table(bid_head, [bidrow(X), bidrow(Y)])
bid100 = table(['Supplier', 'Qty', 'Unit USD', 'Extended USD', 'MOQ met?', 'Freight', 'Source'],
               [[X['supplier'], F['coalition_units'], '%.2f' % X['unit'], '%.2f' % (X['unit'] * F['coalition_units']), 'yes (MOQ %d)' % X['moq'], 'FOB origin - freight not included, amount unknown', X['file']],
                [Y['supplier'], F['coalition_units'], '%.2f' % Y['unit'], 'not purchasable at %d' % F['coalition_units'], 'NO (MOQ %d, short %d)' % (Y['moq'], F['coalition_shortfall_vs_Y_units']), 'DDP', Y['file']]], num=(1, 2))

fig_rows = [
 ['CNC positions (readme table rows with Aluminum Alloy 5052)', F['readme_cnc_table_rows'], 'readme.md', "lines starting '|' containing 'Aluminum Alloy 5052'"],
 ['CNC positions in LEGION BOM handoff', F['cnc_positions'], '02_bom_handoff.json', 'len(cnc_parts)'],
 ['CNC pieces per arm', F['cnc_pieces_per_set'], 'readme.md L105-125', 'sum of Qty'],
 ['CNC pieces for 20 sets', F['cnc_pieces_20_sets'], 'same', 'sum(qty x 20)'],
 ['Positions where readme = LEGION = STEP quantity', '%d of %d' % (F['positions_qty_agree_readme_legion_step'], F['cnc_positions']), 'readme, 02_bom_handoff.json, out/step_instance_counts.json', 'per-position equality'],
 ['Positions where LEGION face count = independent text-read face count', '%d of %d' % (F['positions_faces_agree_legion_vs_text_read'], F['cnc_positions']), '02_bom_handoff.json, out/step_leaf_geometry.json', 'per-position equality'],
 ['STEP leaf definitions / leaf instances (text read)', '%d / %d' % (F['step_leaf_definitions'], F['step_leaf_instances']), 'out/step_instance_counts.json', 'NAUO tree walk from root 00_REBOT_ARM_DM_ASM'],
 ['Positions CNC only / CNC + Sheet Metal', '%d / %d' % (F['positions_cnc_only'], F['positions_cnc_plus_sheet']), 'readme.md Machining column', 'process field'],
 ['Material positions with a lower bound / blocked', '%d / %d' % (F['material_positions_lower_bound'], F['material_positions_blocked']), 'figures.py', 'thinnest PO stock >= smallest bbox dim; CNC only'],
 ['Material lower bound per set, priced positions only (USD)', '%.2f covering %d of %d pieces' % (F['material_usd_per_set_lower_bound_priced_positions_only'], F['material_pieces_per_set_lower_bound'], F['cnc_pieces_per_set']), 'purchase_orders_5052.csv, 02_bom_handoff.json bbox', 'sum(footprint / sheet area x PO price x qty)'],
 ['Rails needed for 20 sets', F['rails_needed_20_sets'], 'rfq_rebot_email.txt L11', '20 x 1'],
 ['Xylem spend at MOQ (USD)', '%.2f' % X['min_commitment_usd'], 'rail_bid_X.txt L3', '11.40 x 100'],
 ['Yarrow spend at MOQ (USD)', '%.2f' % Y['min_commitment_usd'], 'rail_bid_Y.txt L3', '9.90 x 250'],
 ['Xylem excess if plant buys MOQ for 20 (units / USD)', '%d / %.2f' % (X['excess_units_at_moq'], X['excess_cost_at_moq_usd']), 'same', '(100-20) x 11.40'],
 ['Pooled units (coalition_demand.csv)', F['coalition_units'], 'coalition_demand.csv', 'sum(qty), %d rows' % F['coalition_rows']],
 ['Rows with "no signed commitment" / RFQ customer', '%d / %d' % (F['coalition_rows_no_signed_commitment'], F['coalition_rows_rfq_customer']), 'coalition_demand.csv', 'status text'],
 ['Headroom over Xylem MOQ (units)', F['coalition_headroom_vs_X_units'], 'same', 'pooled - 100'],
 ['Pooled units if any one 20-unit buyer drops', F['coalition_units_if_one_buyer_drops'], 'same', 'pooled - 20'],
 ['Shortfall vs Yarrow MOQ (units)', F['coalition_shortfall_vs_Y_units'], 'same', '250 - pooled'],
 ['Days from receipt to requested delivery', 80, 'rfq_rebot_email.txt L4, L12', '2027-01-31 minus 2026-11-12'],
]
fig_tbl = table(['Figure', 'Value', 'Computed from', 'Filter or arithmetic'], fig_rows)

pred = F['legion_predicates']
ready_rows = [
 ['CAD/BOM extraction (STEP via XCAF, reconciled to readme)', v(pred['cad_bom_extraction']), 'LEGION 02_engineering.json verification', 'Independently re-checked here: %d of %d quantities and %d of %d face counts agree (text read of STEP, unverified method)' % (F['positions_qty_agree_readme_legion_step'], F['cnc_positions'], F['positions_faces_agree_legion_vs_text_read'], F['cnc_positions'])],
 ['Rail length within tolerance (MGN9-170)', v(pred['rail_length_tolerance']), 'LEGION predicate', 'No manufacturer or customer tolerance. The T/F "controlled cases" used a synthetic ±0.02 mm test tolerance and are marked admissible_for_rebot: false - they are test evidence, not reBot evidence'],
 ['Joint 2 load / torque', v(pred['joint2_load_torque']), 'LEGION predicate', 'No functional requirement or load case in the inputs'],
 ['CNC material evidence (grade, temper, certificates)', v(pred['cnc_material_evidence']), 'LEGION predicate; receipt refused PART_FIELD_MISSING_MATERIAL_GRADE', 'Alloy stated (5052), temper and certs not'],
 ['Tolerances per feature', v('Z'), 'readme.md L129', '±0.02 mm on "key dimensions" - which ones is not stated; STEP carries no tolerances'],
 ['Fits (H7 / interference)', v('Z'), 'readme.md L131', 'Recommended, features not identified'],
 ['Surface finish per part', v('Z'), 'readme.md L130 vs email L13', 'Ambiguous: anodize dropped, sandblast not addressed'],
 ['Inspection requirements', v('Z'), 'none in inputs', 'Not stated'],
 ['Drawing revision', v('Z'), '02_engineering.json revision_evidence', 'No drawing; STEP v1.1 20260625 at repo commit 22f002a only'],
 ['Sheet-metal flat patterns (lines 17-21)', v('Z'), 'readme.md L121-125', 'Formed geometry only'],
 ['Independent attestation (CAD-025)', v('Z'), '02_engineering.json', 'Not present'],
 ['Overall engineering verdict', v(F['legion_engineering_verdict']), 'LEGION aggregate', 'procurement_authorized false, manufacturing_release false'],
]
ready_tbl = table(['Requirement', 'State', 'Evidence', 'Detail'], ready_rows)

gates_tbl = table(['Gate', 'Step', 'What the estimator does', 'State'], [
 ['1', '4', 'Sends the open questions (below). Nothing was sent in this run.', 'waiting'],
 ['2', '5', 'Confirms or declines the provisional bid/no-bid, per line where lines differ.', 'waiting'],
 ['3', '8', 'Confirms the model, tolerance reading, datums and operation list. No model built (no Fusion).', 'not reached'],
 ['4', '11', 'Releases the customer quote. No quote drafted.', 'not reached']])

page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>reBot RFQ Work-up</title><style>{CSS}</style></head><body><main>
<p class="muted">INTERNAL - estimator work-up. SYNTHETIC TEST DATA for a fictitious plant. Draft only; nothing has been sent to the customer or any supplier.</p>
<h1>RFQ HRL-REBOT-20261112 - Harbor Robotics Lab, reBot B601 DM CNC sets x 20</h1>
<div class="banner"><b>Paused after step 5, at Gate 1 and Gate 2</b> - the questions are drafted for you to send, and the bid/no-bid is provisional until you confirm it. Steps 6 to 11 run when the customer answers, or when you tell me to quote with those questions as exclusions. No customer quote (no price, lead time or terms) is drafted in this pass.<br>
<b>Safety status:</b> not assessed (not applicable to an RFQ intake). <b>Plant profile:</b> none on file (plant_setup.py find: exists false) - the manufacturability check did not run. <b>ERP:</b> not connected - no routings, actuals or comparables. <b>Fusion:</b> not connected - no model built. <b>Freshness:</b> POs dated 2026-10-20 and 2026-11-02; rates memo 2026-10-01; RFQ received 2026-11-12; run 2026-11-15.</div>

<h2>1. Bill of CNC parts per arm, checked against the STEP model</h2>
<p>{F['cnc_positions']} CNC positions, {F['cnc_pieces_per_set']} pieces per arm, {F['cnc_pieces_20_sets']} pieces for 20 sets. Per-arm quantity agrees between the readme, LEGION's XCAF extraction and an independent text read of the STEP on {F['positions_qty_agree_readme_legion_step']} of {F['cnc_positions']} positions. The STEP uses its own product names (e.g. <code>2-M1-STATOR-1</code>); each was matched to its readme part by face count and instance count, and the face counts agree with LEGION's on {F['positions_faces_agree_legion_vs_text_read']} of {F['cnc_positions']}. <b>Method label: "C1: STEP read without CAD (unverified)"</b> - the file was parsed as text (NAUO assembly tree from root <code>00_REBOT_ARM_DM_ASM</code>), not imported into a CAD kernel. Sheet-metal parts (lines 17-21) are {F['positions_cnc_plus_sheet']} positions / {F['pieces_cnc_plus_sheet_per_set']} pieces per arm. LEGION's one BOM mismatch (DM_MOTOR1_WIRING_HARNESS_CLIP, readme 2, STEP 0) is a printed part, outside this RFQ.</p>
{bom_tbl}
<p class="muted">Also saved: out/cnc_bom_per_arm.csv, out/step_instance_counts.json, out/step_leaf_geometry.json.</p>

<h2>2. Engineering readiness - verified and not verified</h2>
{ready_tbl}
<p>Only the BOM extraction is verified. Every requirement a tolerance-driven quote rests on is open, so no geometry estimate can pass Gate 3 yet. Per-line geometry estimates (path C1, text read, approval <code>draft</code>) are summarised in out/geometry-estimates-HRL-REBOT-20261112.txt.</p>

<h2>3. Open questions - sendable draft (Gate 1, NOT SENT)</h2>
<pre>{e(QUESTIONS)}</pre>
<p class="muted">No Word copy this session: no Word writer available. Text copy: out/open-questions-HRL-REBOT-20261112.eml.txt.</p>

<h2>4. Intake form, registers and provisional bid/no-bid</h2>
<p>Full record: out/open-work/inquiries/harbor-robotics-lab-HRL-REBOT-20261112.intake.txt.</p>
{table(['Field', 'Value', 'Source', 'Reading basis'], [
 ['customer / contact', 'Harbor Robotics Lab (fictitious) / Lena Okafor', 'rfq_rebot_email.txt L2, L15', '-'],
 ['rfq_reference', 'null (none given); internal HRL-REBOT-20261112', 'email L5', '-'],
 ['received_at', '2026-11-12T11:20:00+00:00', 'email L4', '-'],
 ['quantities', '20 sets (one quantity, no breaks); per line qty/arm x 20', 'email L10', '-'],
 ['material', 'Aluminum Alloy 5052 (temper not stated)', 'readme.md L105-125; email L11', 'from_text'],
 ['specs: key dimensions', '±0.02 mm GB/T1840-M (as written); features not identified', 'readme.md L129', 'from_text'],
 ['specs: fits', 'H7 / interference fit, recommended; features not identified', 'readme.md L131', 'from_text'],
 ['finish', 'AMBIGUOUS: "Anodizing / Sandblasting" vs "Anodize not required"', 'readme.md L130; email L13', 'from_text'],
 ['required_delivery', '2027-01-31 (all lines)', 'email L12', '-'],
 ['geometry_path', 'C1 on lines 1-22 (STEP, no drawing)', 'email L12 "We have no 2D drawings"', '-'],
 ['payment / freight / packaging / liability', 'null (missing register)', '-', '-'],
 ['recommendation', 'bid (provisional), lines 1-22 bid; constraint-free and scored on dates alone', '-', '-'],
 ['bid_decision_state', 'draft', '-', '-'],
 ['paused_at_step / waiting_on', '5 / estimator Gate 1 and Gate 2, then customer', '-', '-'],
 ['stale_after', '2026-11-19 (5 business days - default, not plant-set)', '-', '-']])}
<h3>Would change the recommendation</h3>
<ul><li>Q2 (key dimensions, tolerance standard) - lines 1-21: no_bid or bid-with-exclusion wherever ±0.02 mm exceeds demonstrated capability (capability not on file, so not checked).</li>
<li>Q5 (formed parts) - lines 17-21: no_bid on those lines (inquiry becomes partial) if the plant cannot bend 5052 or the flat patterns cannot be agreed.</li>
<li>Q7 (rail scope) - line 22: no_bid if carriages or an accuracy class are needed that neither bid offers, or if you will not carry the MOQ excess.</li>
<li>Q1 (revision freeze) - all lines: hold if a change is pending.</li></ul>

<h2>5. Draft cost estimate - partial, internal</h2>
<pre>=== INTERNAL COST SHEET - NOT FOR CUSTOMER ===
Status: PARTIAL. Proceeding to a cost buildup before Gate 2 was at the requester's instruction; the bid/no-bid is unconfirmed (draft).
Fusion not connected - no model built. Geometry path C1, STEP read as text (unverified). No geometry estimate is confirmed (Gate 3 not reached).

Hours: NONE DERIVED. Rung 1 (routing) - none on file. Rung 2 (closed-job actuals) - none on file. Rung 3 (geometry-derived) -
refused: no confirmed geometry estimate, no Plant context machine classes or cutting data. Rung 4 (first principles) - not
produced: it would need operation-by-operation assumptions (setups, tooling, feeds) that are not in the inputs.
What would firm it up: the customer's answers to Q2-Q5, a Gate 3 confirmation of the operation list, and plant setup hours and
cutting data for 5052 in the Plant context.

Rates: NOT ON FILE. No MFG_LABOR_RATE / MFG_BURDEN_RATE / MFG_MARGIN_RULES in the environment and no plant rates file.
The finance memo in inputs/rates_memo.txt is a document supplied in this run, not a rate recorded on the plant's rates page,
so its values are not used here and not repeated. Say "update our labour rate" (onboarding) to record them, or set the MFG_*
variables. Blocked lines: labour, machine and burden, setup, material markup, outside processing markup, margin.
Per quote-build step 4, no job total and no unit price for this job is produced while these are unset.

Material (what can be produced): PO prices, lower bound only - blank footprint (two largest bbox dimensions) on the thinnest
PO stock at least as thick as the part's smallest bbox dimension, priced at that PO's price per sheet area. Excludes kerf,
cleanup allowance, nesting yield and scrap allowance (none of which is in the inputs). The stock choice is an estimating
assumption for Gate 3, not a customer requirement.
=== END ===</pre>
{mat_tbl}
<p><b>Per set, priced positions only:</b> {F['material_usd_per_set_lower_bound_priced_positions_only']:.2f} USD lower bound, covering {F['material_pieces_per_set_lower_bound']} of {F['cnc_pieces_per_set']} pieces per set. Not extended to 20 sets: a job-quantity figure is withheld while labour, burden and margin are blocked. Flagged: {', '.join(F['positions_fit_only_without_cleanup'])} fit 3 mm sheet only without cleanup (part thickness equals sheet thickness).</p>
{stock_tbl}
<p class="muted">Material basis: actual purchase prices, 1st preference, dated 2026-10-20 and 2026-11-02. Material prices move: validity caveat applies. Outside processing: none priced (finish ambiguous). Tooling/fixtures: not determined. Date check: not checked against shop load (no planning export).</p>

<h2>6. Rail quotes compared (MGN9, 170 mm)</h2>
<p>Full page: out/sourcing-output/bid-comparison.html. Both are supplied test quotes, off-format, not awarded.</p>
{bid_tbl}

<h2>7. Pooling the buyers to reach the MOQ - and can we rely on it?</h2>
<p><b>Arithmetic: yes for Xylem, no for Yarrow.</b> {F['coalition_rows']} rows x 20 = {F['coalition_units']} units, exactly Xylem's MOQ of {X['moq']} (headroom {F['coalition_headroom_vs_X_units']}); {F['coalition_shortfall_vs_Y_units']} short of Yarrow's {Y['moq']}.</p>
{bid100}
<p><b>Reliance: no.</b> {F['coalition_rows_no_signed_commitment']} of the {F['coalition_rows']} rows say "expressed interest by email; no signed commitment", and the fifth is this RFQ's own customer, who has asked for a quote, not placed an order. There is zero headroom: if any one buyer drops, the pool is {F['coalition_units_if_one_buyer_drops']} and misses the MOQ. LEGION's own evaluation agrees - the pooled route is T only in its "simulated demand demonstration"; treated as real it is Z (synthetic_opt_in_not_live_authority), buyer_signatures Z, real_supplier_quote Z, and the marketplace route is BLOCKED on licensing. Xylem's 21-day validity has no quote date, so it may already have lapsed, and FOB origin leaves freight unpriced.</p>
<p><b>Options for the estimator (not decisions):</b> (a) quote line 22 on buying Xylem's MOQ of 100 and carrying {X['excess_units_at_moq']} rails ({X['excess_cost_at_moq_usd']:.2f} USD at the quoted unit price, plus unknown freight) as stock; (b) offer the rail only if the customer sources it themselves (Q7); (c) pursue the pool only after each buyer signs a commitment, and never share one buyer's name or demand with another without their consent.</p>

<h2>8. Where sign-off is needed</h2>
{gates_tbl}

<h2>9. Figures block</h2>
{fig_tbl}
<p class="muted">Every figure above is computed by out/scripts/figures.py from the input files; STEP counts by out/scripts/step_instances.py and step_leaf_bbox.py.</p>

<h2>10. Not done in this run</h2>
<ul><li>No customer quote and no lead time: chain paused at Gates 1 and 2 (rfq-to-quote step 5).</li>
<li>No machining hours: no routing, actuals, confirmed model, Fusion, or plant cutting data.</li>
<li>Labour, burden, markup and margin not applied: no rates on file; the memo's values are not used.</li>
<li>Manufacturability check not run: no plant capability profile.</li>
<li>No Word/Excel copies: no python-docx or openpyxl in this session.</li>
<li>Not saved to an Open work page: no artifact tools in this run; open-work block written to out/open-work/open-work.md only.</li>
<li>Sales command-center page not produced: no quote or period data exists to report.</li></ul>
</main></body></html>"""
open(os.path.join(O, 'rfq-workup-HRL-REBOT-20261112.html'), 'w', encoding='utf-8').write(page)

# ---------- bid comparison page
os.makedirs(os.path.join(O, 'sourcing-output'), exist_ok=True)
REST_X = """Subject: XL-5512 - MGN9H rail 170 mm - restatement request

Hello,

Thank you for quote XL-5512. To compare it we need it restated with:
1. The quote date (so the 21-day validity has a start).
2. Unit price at 20 pcs and at 100 pcs, in USD.
3. Lead time from receipt of order, for the first delivery.
4. Freight cost or Incoterm with delivered price to our dock.
5. Rail length tolerance on the 170 mm cut, and the accuracy class name for "standard accuracy".
6. Carriage (MGN9H block) price, if available, per piece.
7. Any exclusions or assumptions.

Regards,
[buyer name]"""
REST_Y = """Subject: YMP-208 - MGN9 rail cut to 170 mm - restatement request

Hello,

Thank you for reference YMP-208. To compare it we need it restated with:
1. The quote date and validity period.
2. Unit price at 20 pcs and at 100 pcs, in USD, with the minimum order quantity at each.
3. The rail accuracy class.
4. Lead time from receipt of order.
5. Whether carriages (MGN9 blocks) are included or available, and their price.
6. Any exclusions or assumptions.

Regards,
[buyer name]"""
bidpage = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rail Bid Comparison</title><style>{CSS}</style></head><body><main>
<p class="muted">INTERNAL. SYNTHETIC TEST QUOTES (not real offers). Sourcing event SRC-HRL-REBOT-RAIL-MGN9-170, for RFQ HRL-REBOT-20261112. Nothing sent, nothing awarded.</p>
<h1>MGN9 170 mm rail - bid comparison</h1>
<h2>Provisional recommendation</h2>
<p><b>Pursue Xylem XL-5512 (provisional), only if 100 rails can be justified.</b> At any purchasable quantity it is the lower spend: {X['min_commitment_usd']:.2f} USD for its MOQ of {X['moq']} against {Y['min_commitment_usd']:.2f} USD for Yarrow's MOQ of {Y['moq']}, and 3 weeks against 5. Main tradeoff: Yarrow is cheaper per piece ({Y['unit']:.2f} vs {X['unit']:.2f} USD) and delivered DDP, but its MOQ is {Y['excess_units_at_moq']} rails beyond our need and its accuracy class is not stated. Neither bid buys 20.</p>
<p><b>Open before any award:</b> neither supplier is on an approved supplier list (none on file); both off-format; Xylem quote date missing, so validity cannot be checked, and freight is excluded (FOB origin); Yarrow accuracy class and validity not stated; no length tolerance from Xylem; customer has not stated accuracy class or carriage scope (Q7); no price at 20 from either.</p>
<p><b>Next step:</b> pursue Xylem, look into the alternatives, or ask both suppliers to restate (drafts below)?</p>
<h2>At the 20 rails needed</h2>
{bid_tbl}
<h2>At 100 rails (pooled demand - see reliance caveat on the work-up page)</h2>
{bid100}
<h2>Draft supplier emails (HELD - not sent; recipient: not on file)</h2>
<h3>Xylem Linear Motion (fictitious) - restatement</h3><pre>=== SUPPLIER EMAIL - HELD - Xylem Linear Motion ===
{e(REST_X)}
=== END ===</pre>
<h3>Yarrow Motion Parts (fictitious) - restatement</h3><pre>=== SUPPLIER EMAIL - HELD - Yarrow Motion Parts ===
{e(REST_Y)}
=== END ===</pre>
<details><summary>Bid records summary (fields_missing)</summary>
{table(['Supplier', 'Source file', 'Break prices as quoted', 'fields_missing'], [
 [X['supplier'], X['file'], '11.40 USD at 100 pcs', 'quote date; unit price at 20; lead time from a named event; tooling statement; quality clause acceptance; length tolerance; freight amount'],
 [Y['supplier'], Y['file'], '9.90 USD each (no quantity break named)', 'quote date; validity; unit price at 20 and 100; accuracy class; lead time from a named event; tooling statement; quality clause acceptance']])}
</details>
<details><summary>Readiness evidence</summary><ul>
<li>Cost comparable: both partly - unit and currency stated, MOQ known; Xylem freight excluded; neither priced at 20.</li>
<li>Supplier approved: not evidenced for either (no approved supplier list on file).</li>
<li>Delivery evidenced: lead times stated without a named start event; LEGION assumed an order date of 2026-12-15 to place Xylem at 2027-01-15 - an assumption, not a quote.</li>
<li>Technical and quality terms: not stated by either; no rail spec from the customer yet.</li></ul></details>
</main></body></html>"""
open(os.path.join(O, 'sourcing-output', 'bid-comparison.html'), 'w', encoding='utf-8').write(bidpage)

# ---------- geometry estimates summary (record)
lines = ['# Geometry estimates, contract shared/contracts/geometry-estimate.md - one per line. Record. SYNTHETIC TEST DATA.',
         '# All: geometry_path C1, origin customer_step, cad_backend none, document_integrity not_applicable (STEP read as text),',
         '# drawing_revision_priced_to null (no drawing; STEP reBot_B601_DM_v1.1_20260625.step), approval.status draft.',
         '# Every feature tolerance: null, reading_basis unreadable_flagged ("no tolerance in the STEP file; ask the customer for the drawing or a tolerance spec").',
         '# datums: none identified (a STEP identifies none; any datum would be inferred and is a Gate 3 question). operations: not proposed (no Plant context machine classes).',
         'line_no | part | step_product | qty_per_arm | bbox_mm (LEGION XCAF) | volume_mm3 (LEGION) | faces | stock assumption | unreadables | approval']
for n, q in enumerate(P, 1):
    m = M[q['part_id']]
    st = ('%s (%s), margin %g mm%s' % (m['stock'], m['stock_po'], m['thickness_margin_mm'], ', fits only without cleanup' if m['fits_only_without_cleanup'] else '')) if m['status'] == 'lower_bound' else 'none: ' + m['reason']
    lines.append('%d | %s | %s | %d | %s | %s | %d | %s | all tolerances; key dimensions; fits; finish%s | draft' % (
        n, q['part_id'], q['step_product'], q['qty_readme'], ' x '.join('%g' % x for x in q['bbox_legion_mm']), q['volume_legion_mm3'], q['faces_step_text'], st,
        '; flat pattern and gauge' if q['process'] != 'CNC' else ''))
lines.append('22 | MGN9-170 rail (purchased) | 6-RAIL-170 | 1 | text-read vertex extents 6.5 x 9 x 170 | - | 47 | buy-out, no stock | accuracy class; length tolerance | draft')
open(os.path.join(O, 'geometry-estimates-HRL-REBOT-20261112.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('pages written')
