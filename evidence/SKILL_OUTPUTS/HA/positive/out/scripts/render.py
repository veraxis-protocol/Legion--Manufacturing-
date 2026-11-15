import json, html
from datetime import date
E = html.escape
bom = json.load(open('out/bom_reconciliation.json')); bc = json.load(open('out/bid_and_coalition_figures.json'))
st = json.load(open('out/step_structure.json'))
DAYS = (date(2027, 1, 31) - date(2026, 11, 12)).days
CSS = """<style>:root{--bg:#fbfaf7;--fg:#1d1d1b;--mut:#5d5a53;--line:#dcd8cf;--acc:#8a4b14;--warn:#9a1f1f;--card:#fff}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#181816;--fg:#ecebe6;--mut:#a9a59b;--line:#3a3833;--acc:#e0a160;--warn:#f08a8a;--card:#22211e}}
:root[data-theme="dark"]{--bg:#181816;--fg:#ecebe6;--mut:#a9a59b;--line:#3a3833;--acc:#e0a160;--warn:#f08a8a;--card:#22211e}
body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;padding:16px;max-width:1100px;margin:auto}
h1{font-size:22px}h2{font-size:18px;border-bottom:1px solid var(--line);padding-bottom:4px;margin-top:32px}
table{border-collapse:collapse;width:100%;font-size:13px;display:block;overflow-x:auto}td,th{border:1px solid var(--line);padding:4px 6px;text-align:left;vertical-align:top}
th{background:var(--card)}.warn{color:var(--warn);font-weight:600}.mut{color:var(--mut)}pre{white-space:pre-wrap;background:var(--card);border:1px solid var(--line);padding:10px;font-size:13px}
.banner{border:2px solid var(--acc);padding:10px;background:var(--card)}</style>"""
def tbl(head, rows):
    return '<table><tr>' + ''.join(f'<th>{E(h)}</th>' for h in head) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</table>'
F = bom['figures']; C = bc['coalition']
HEAD = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{}</title>' + CSS + '</head><body>'

# ---------------- intake / readiness page ----------------
p = [HEAD.replace('{}', 'reBot RFQ Intake')]
p.append('<h1>RFQ intake, BOM check and engineering readiness - Harbor Robotics Lab (fictitious), reBot B601 DM CNC sets x20</h1>')
p.append('<p class="mut">SYNTHETIC test data, fictitious plant. Skill chain: rfq-to-quote (Chain 1) running customer-inquiry-intake steps 1-5; design step path C1 read as text; supplier-quote-request steps 11-13 for the rail bids. Draft only. Nothing has been sent to anyone.</p>')
p.append('<div class="banner"><b>Paused after step 5, at Gate 1 and Gate 2</b> - the questions are drafted for you to send, and the bid/no-bid is provisional until you confirm it. Steps 6 to 11 run when the customer answers, or when you tell me to quote with those questions as exclusions. <b>No price, lead time or terms have been drafted</b> (section 7 says why the requested cost estimate was not produced).</div>')
p.append('<h2>Where sign-off is needed</h2>' + tbl(['Gate', 'Step', 'What the estimator does', 'State'], [
    ['1', '4', 'Sends the open questions (section 5) from their own mailbox', 'waiting - questions drafted, not sent'],
    ['2', '5', 'Confirms or declines the bid/no-bid, per line (section 6)', 'waiting - recommendation is draft/provisional'],
    ['3', '8', 'Confirms the model / feature list, tolerance reading, datums and operation list before any hour is derived', 'not reached - no model built (Fusion not connected)'],
    ['4', '11', 'Reviews and releases the customer quote', 'not reached - no quote drafted']]))
p.append('<h2>1. Plant setup and what could not be checked</h2><ul>'
         '<li>plant_setup.py find: no plant profile (plant-setup/plant-context.md does not exist), no rates file, no Open work page; no artifact tools in this run. <b>No capability profile, so the manufacturability check did not run and the recommendation is constraint-free.</b></li>'
         '<li>No ERP and no closed work orders: <b>no actual-cost comparable</b>; the recommendation scores on stated requirements and dates alone.</li>'
         '<li>MFG_LABOR_RATE, MFG_BURDEN_RATE, MFG_MARGIN_RULES, MFG_RFQ_STALE_DAYS: checked by name, none set.</li>'
         '<li>Fusion not connected - no model built. STEP read as a text file (path C1, unverified).</li>'
         '<li>No Word or Excel writer (python-docx / openpyxl not installed; installing is not allowed): no .docx/.xlsx copies. Documents are on this page.</li></ul>')
rows = [[E(r['description']), E(r['file']), E(r['material']), E(r['machining']), str(r['readme_qty']), str(r['step_qty']), str(r['readme_qty'] * 20),
         f"{E(r['step_product_id'])} (#{r['step_entity']})", ('<span class="warn">' if r['status'] != 'match' else '') + E(r['status'])] for r in bom['rows']]
p.append('<h2>2. Bill of CNC parts per arm, checked against the STEP model</h2>')
p.append('<p>Readme CNC table (readme.md L119-141) reconciled by code (out/scripts/step_bom.py, reconcile.py) against the STEP assembly: each STEP PRODUCT name field matched to the readme file name; quantity = leaf instances flattened through NEXT_ASSEMBLY_USAGE_OCCURRENCE from root 00_REBOT_ARM_DM_ASM. <b>C1: STEP read without CAD (unverified)</b> - names and instance counts only; no geometry, volumes or tolerances were read.</p>')
p.append(tbl(['Part', 'Readme file', 'Material (readme)', 'Process (readme)', 'Qty/arm readme', 'Qty/arm STEP', 'Qty for 20 sets', 'STEP product (entity)', 'Check'], rows))
p.append(f"<p>Result: {F['rows_matching']} of {F['readme_cnc_rows']} part numbers match; {F['readme_cnc_qty_per_arm']} CNC pieces per arm in the readme, {F['step_qty_for_readme_cnc_rows']} in the STEP; {F['cnc_parts_for_20_sets']} pieces for 20 sets.</p>")
notes = {'03_Link3_L': 'Readme lists 03_Link3_L as CNC + Sheet Metal, but its STEP id carries the 1- prefix the STEP uses for 3D-printed parts (its mirror 03_Link3_R is 2-LINK-2-ARM-R). Counted in the CNC set per the readme; to confirm.',
         '01_Lower_Arm_Filler_M': 'Readme lists 01_Lower_Arm_Filler_M as a 3D-printed ABS part, but its STEP id carries the 2- prefix the STEP uses for metal parts. Not counted in the CNC set; to confirm.'}
p.append('<p class="warn">Two naming anomalies to confirm with the customer (not resolved here):</p><ul>' + ''.join(
    f"<li>STEP product {E(a['step_product_id'])} is named {E(a['name'])}. {notes[a['name']]}</li>" for a in bom['prefix_anomalies']) + '</ul>')
p.append(f"<p class='mut'>STEP facts (read as text): {st['entity_count']} entities, {st['product_count']} products, {st['nauo_count']} assembly-usage occurrences, length unit millimetre. Rail 6-RAIL-170 x1 and 6-SLIDER x2 per arm (Gripper purchase parts), matching readme L166-167 (rail 1, slider block 2).</p>")
p.append('<h2>3. Engineering readiness - verified and not verified</h2>')
p.append(tbl(['Requirement', 'Status', 'Evidence / what is missing'], [
    ['CNC part list and quantity per arm', '<b>Verified (STEP read as text, unverified import)</b>', f"{F['rows_matching']}/{F['readme_cnc_rows']} part names and {F['readme_cnc_qty_per_arm']} pcs/arm agree readme vs STEP, by code"],
    ['Model file identity', 'Verified', 'Email L9 names reBot_B601_DM_v1.1_20260625.step; STEP FILE_NAME header and root product name match'],
    ['Revision to price to', '<span class="warn">Not verified</span>', 'Readme L37-38: two different files both labelled v1.1 (20260425, 20260625); readme L62 says production tolerances/clearances will be adjusted'],
    ['Material', 'Partly verified', '5052 stated (email L11, readme L121-141); temper and stock thickness per part not stated'],
    ['Tolerances', '<span class="warn">Not verified</span>', 'Only "Key dimension tolerance ±0.02 mm GB/T1840-M" (readme L145) - key dimensions not identified, standard designation to confirm; STEP carries no tolerances; no 2D drawings (email L12)'],
    ['Fits', '<span class="warn">Not verified</span>', '"H7 / interference fit" recommended (readme L147); bores not identified'],
    ['Finish', '<span class="warn">Ambiguous</span>', 'Email L13 "Anodize not required" vs readme L146 "Anodizing / Sandblasting"'],
    ['Process for 5 Link parts', '<span class="warn">Not verified</span>', 'Readme: CNC + Sheet Metal (bending); plant capability not on file'],
    ['Datums', '<span class="warn">Not verified</span>', 'No drawing; any datum would be inferred at Gate 3'],
    ['Stock size, envelope, volume per part', 'Not read', 'Needs CAD import or a hand-entered feature list (design step 7, after the pause)'],
    ['Manufacturability vs plant', '<span class="warn">Not checked</span>', 'No capability profile on file'],
    ['Rail scope (line 2)', '<span class="warn">Not verified</span>', 'Rail only asked (email L11); BOM needs 2 MGN9 carriages per arm (readme L167); accuracy class not stated']]))
p.append('<h2>4. Missing and ambiguous registers</h2><h3>Missing (never stated)</h3>' + tbl(['Line', 'Field', 'Why it matters', 'Should have come from'], [
    ['1', 'Tolerances for features other than "key dimensions"; which dimensions are key', 'Machining strategy, inspection and price depend on them; never inferred', '2D drawings or a tolerance spec'],
    ['1', 'Material temper and stock form/thickness', 'Our recent 5052 buys are H32; a different temper or form changes stock and price', 'Customer spec / BOM'],
    ['1', 'Datums / inspection requirements', 'Fixturing and inspection plan', 'Drawings'],
    ['1', 'Whether parts the readme says "can be 3D printed" are wanted in aluminium', 'Changes set content and cost', 'Customer'],
    ['1,2', 'Pending design changes', 'Readme L62: production version will adjust tolerances and clearances - risk to the revision quoted', 'Customer'],
    ['2', 'Rail accuracy class, carriages included or not, cut tolerance', 'Decides which supplier bid is comparable', 'Customer'],
    ['all', 'RFQ reference and response deadline', 'Traceability and turnaround', 'Customer email'],
    ['all', 'Payment terms', 'Quote would default to plant standard', 'Customer terms'],
    ['all', 'Freight / delivery point', 'Bids are FOB origin vs DDP; our quote basis needs one', 'Customer terms'],
    ['all', 'Packaging / kitting per set', 'Unpriced if unknown', 'Customer terms'],
    ['all', 'Liability, certificates, inspection reports', 'Certs and reports add cost', 'Customer terms']]) +
    '<h3>Ambiguous (stated two ways)</h3>' + tbl(['Line', 'Field', 'Values found', 'Why it matters'], [
    ['1', 'Finish', '"Anodize not required" (email L13); "Anodizing / Sandblasting" (readme L146)', 'Outside processing and lead time'],
    ['1,2', 'Revision', 'v1.1 = ..._20260425.step (readme L37) and v1.1 = ..._20260625.step (readme L38, dated 2026-10-30); STEP header timestamp 2026-07-01', 'Quote must name the revision priced to'],
    ['1', '03_Link3_L process', 'CNC + Sheet Metal (readme L139); STEP id 1-LINK-2-ARM-L (printed-part prefix)', 'In or out of the CNC set'],
    ['1', '01_Lower_Arm_Filler_M', '3D printed ABS (readme L79); STEP id 2-SPACE-UP (metal-part prefix)', 'In or out of the CNC set'],
    ['1', 'Tolerance standard', '"GB/T1840-M" as written (readme L145)', 'Confirm the standard designation intended']]))
q = open('out/customer-questions-email.txt', encoding='utf-8').read()
p.append('<h2>5. Open questions - Gate 1 (draft, not sent)</h2><pre>=== CUSTOMER EMAIL - SENDABLE ===\n' + E(q) + '\n=== END ===</pre><p class="mut">Outbound check: block read alone; no price, rate, PO, supplier name or other buyer appears in it.</p>')
p.append('<h2>6. Provisional bid/no-bid - Gate 2 (draft)</h2>' + tbl(['Line', 'line_recommendation', 'Reasoning', 'Would change if'], [
    ['1 CNC sets x20', 'bid (provisional)', f'Material and processes stated are ordinary CNC aluminium work; part list fully reconciled to the STEP. Constraint-free: no capability profile, so manufacturability was not checked. No cost history: scored on stated requirements and dates alone. Delivery 31 Jan 2027 is {DAYS} days after receipt; shop load unknown.', 'Q2: tolerances tighter than the plant has demonstrated -> may become no_bid; Q5: bending required and no press brake -> no_bid for the 5 Link parts (partial); Q1: design about to change -> hold'],
    ['2 MGN9-170 rail x20', 'no_bid (provisional)', 'Neither supplier quote buys 20: MOQ 100 (Xylem) and 250 (Yarrow). Pooled demand reaches 100 only with 4 buyers who have no signed commitment.', 'Becomes bid if signed commitments reach the Xylem MOQ (100), the customer accepts a 100-piece buy, or a source with MOQ <= 20 is found; Q7 (carriages) also changes scope']]) +
    '<p>Roll-up: <b>partial</b>, provisional, bid_decision_state: draft. Hard disqualifier: none determinable from stated facts. Inquiry state: open; stale after 2026-11-19 (default 5 business days from received_at 2026-11-12, as no send is recorded; MFG_RFQ_STALE_DAYS not set).</p>')
p.append('<h2>7. Draft cost estimate for 20 sets - not produced</h2><p class="warn">Not drafted in this pass, for four reasons the skills make binding:</p><ol>'
         '<li><b>Chain pause.</b> rfq-to-quote: no price is drafted in the same pass as the open questions it depends on (tolerances, temper, finish and set content all change cost). Steps 6-11 run after answers, or when you tell me to quote with questions 1-9 as exclusions.</li>'
         '<li><b>No hours.</b> No routings, no closed-job actuals, no model (Fusion not connected) and no Gate 3 confirmation. No rung of the hours ladder is available, and machine hours are never invented.</li>'
         '<li><b>Rates not on file.</b> The rates memo is a document supplied in this run, not a rate in the plant rates file or an MFG_* variable. Per quote-build / secret-config a rate supplied this way is not used and not repeated; record it once through onboarding ("update our labour rate") and later quotes price from it.</li>'
         '<li><b>Material quantity unknown.</b> PO prices exist, but the stock each part consumes needs part envelopes (design step), which were not read.</li></ol>'
         '<p>Material price basis available once the design step runs (internal; actual purchase prices, 1st preference):</p>' + tbl(['PO', 'Date', 'Item', 'Unit price USD', 'Received'], [
             ['PO-30710', '2026-10-20', 'AL5052-SH-3, 5052-H32 sheet 3 mm x 1220 x 2440', '148.60', '2026-10-27'],
             ['PO-30711', '2026-10-20', 'AL5052-PL-6, 5052-H32 plate 6.35 mm x 610 x 1220', '171.25', '2026-10-27'],
             ['PO-30744', '2026-11-02', 'AL5052-PL-10, 5052-H32 plate 10 mm x 610 x 1220', '262.80', '2026-11-09']]) + '<p class="mut">Source: inputs/purchase_orders_5052.csv. Internal only. H32 is our temper; the customer has not stated one (Q3).</p>')
cx = bc['coverage']['Xylem Linear Motion (fictitious)']; cy = bc['coverage']['Yarrow Motion Parts (fictitious)']
p.append(f"<h2>8. Rail quotes and pooled MOQ</h2><p>See out/sourcing-output/bid-comparison.html. Pooled {C['pooled_qty_total']} meets Xylem MOQ {cx['moq']} with {cx['slack_or_short']} slack only if all {C['buyers']} buyers buy; Yarrow MOQ {cy['moq']} is short by {-cy['slack_or_short']}. {C['qty_with_signed_commitment']} of {C['pooled_qty_total']} pooled units carry a signed commitment, so the pool cannot be relied on.</p>")
fb = [['CNC part numbers in readme table', F['readme_cnc_rows'], 'readme.md L119-141', 'rows whose file ends .step'],
      ['CNC pieces per arm (readme)', F['readme_cnc_qty_per_arm'], 'readme.md', 'sum Qty'],
      ['CNC pieces per arm (STEP)', F['step_qty_for_readme_cnc_rows'], 'STEP NAUO tree', 'flattened leaf instances whose PRODUCT name = readme file stem'],
      ['Rows matching', F['rows_matching'], 'reconcile.py', 'readme qty == STEP qty'],
      ['CNC pieces for 20 sets', F['cnc_parts_for_20_sets'], 'reconcile.py', '20 x pieces per arm'],
      ['STEP entities / products / NAUO', f"{st['entity_count']} / {st['product_count']} / {st['nauo_count']}", 'step_bom.py', 'regex over DATA section'],
      ['Pooled rail qty', C['pooled_qty_total'], 'coalition_demand.csv', 'sum qty, 5 rows'],
      ['Qty with signed commitment', C['qty_with_signed_commitment'], 'coalition_demand.csv', "status contains 'signed' and not 'no signed'"],
      ['Days receipt to delivery', DAYS, 'email L4, L12', '2026-11-12 to 2027-01-31']]
p.append('<h2>Figures block (computed by code)</h2>' + tbl(['Figure', 'Value', 'Computed from', 'Filter'], [[E(str(c)) for c in r] for r in fb]))
p.append('<h2>Intake form (field table)</h2>' + tbl(['Field', 'Value', 'Source', 'reading_basis'], [
    ['customer', 'Harbor Robotics Lab (fictitious)', 'email L15', ''], ['contact', 'Lena Okafor, lena.okafor@harbor-robotics-lab.example', 'email L2', ''],
    ['rfq_reference', 'null', 'not stated', ''], ['received_at', '2026-11-12T11:20:00+00:00', 'email L4', ''], ['response_deadline', 'null', 'not stated', ''],
    ['payment / freight / packaging / liability', 'null (all four)', 'not stated', ''], ['site', 'null - no plant profile', '', ''],
    ['L1 quantities', '20 set', 'email L10', ''], ['L1 material', 'Aluminium 5052 (temper null)', 'email L11; readme L121-141', ''],
    ['L1 revision', 'v1.1 (20260625 file) - ambiguous', 'email L9; readme L37-38', ''], ['L1 spec: key dimension tolerance', '±0.02 mm GB/T1840-M (which dims not identified)', 'readme L145', 'from_text'],
    ['L1 spec: mating fits', 'H7 / interference (recommended)', 'readme L147', 'from_text'], ['L1 spec: all other features', 'null', 'STEP has no tolerances', 'unreadable_flagged'],
    ['L1 finish', 'null - ambiguous', 'email L13 vs readme L146', ''], ['L1 required_delivery', '2027-01-31', 'email L12', ''],
    ['L1 geometry_path', 'C1', 'STEP, no drawing', ''], ['L2 description', 'MGN9-170 mm linear rail, one per arm', 'email L11', ''], ['L2 quantities', '20 each', 'email L10-11', ''],
    ['L2 geometry_path', 'none (catalogue item)', '', ''], ['recommendation', 'partial (L1 bid, L2 no_bid), provisional', '', ''],
    ['bid_decision_state', 'draft', '', ''], ['inquiry_state', 'open', '', ''], ['paused_at_step', '5', '', '']]) +
    '<p class="mut">Full record: out/open-work/inquiries/harbor-robotics-lab-rebot-b601-20sets.intake.txt. Not saved to an Open work page: no artifact tools in this run.</p>')
p.append('</body></html>')
open('out/rfq-intake-harbor-robotics.html', 'w', encoding='utf-8').write('\n'.join(p))

# ---------------- bid comparison page ----------------
b = bc['bids']
s = [HEAD.replace('{}', 'Rail Bid Comparison')]
s.append('<h1>Bid comparison SRC-2026-11-14-MGN9-170 - MGN9 170 mm rail (reBot RFQ line 2)</h1><p class="mut">Internal. SYNTHETIC supplied test quotes. No selection, no award, no PO; nothing sent to any supplier.</p>')
s.append(f"<div class='banner'><b>Provisional recommendation:</b> pursue Xylem Linear Motion (XL-5512) for clarification - the only bid whose MOQ ({cx['moq']}) the pooled demand can reach. Main tradeoff: Yarrow is cheaper per piece and delivered DDP, but its MOQ of {cy['moq']} is {-cy['slack_or_short']} above the whole pool. <b>Both bids are provisional, not ready for buyer review</b>: neither supplier is on an approved list (none on file), quality clauses not stated, lead times have no start event, Xylem's validity date cannot be computed (quote date not given) and it excludes carriages; Yarrow states no accuracy class, carriage scope or validity. <b>Do not rely on the pool</b>: {C['qty_with_signed_commitment']} of {C['pooled_qty_total']} units are signed; if any one buyer drops out the pool is {cx['pooled_without_one_buyer']}, below the Xylem MOQ.<br><br><b>Next step:</b> Pursue Xylem, look into a lower-MOQ source, or ask both suppliers to restate?</div>")
rows = []
for t in bc['table']:
    bb = next(x for x in b if x['supplier'] == t['supplier'])
    note = ' (price quoted at 100 pcs, not at this break)' if (t['supplier'].startswith('Xylem') and t['break'] == 250) else ''
    ext = (f"{t['ext']:.2f}{note}" if t['ext'] is not None else 'not buyable at this qty')
    rows.append([str(t['break']), E(t['supplier']), 'not_confirmed_approved', f"{t['unit']:.2f} {bb['currency']} - {E(bb['price_basis'])}", ext, 'not stated',
                 str(bb['moq']) + (f" <span class='warn'>{E(t['moq_flag'])}</span>" if t['moq_flag'] else ''), E(bb['lead']), 'not stated',
                 E(bb['scope'] + '; ' + bb['freight']), E(bb['validity'] or 'not stated'), 'provisional', E(bb['src'])])
s.append('<h2>Comparison per quantity (20 = customer need, 100 = pooled interest, 250 = Yarrow MOQ)</h2>' + tbl(['Qty', 'Supplier', 'Approval', 'Unit price as quoted', 'Extended USD', 'Tooling', 'MOQ', 'Lead time', 'Clauses', 'Scope / freight', 'Validity', 'Readiness', 'Source'], rows))
s.append('<p>Freight bases differ (FOB origin vs delivered DDP) and Yarrow states no accuracy class or carriage scope, so the unit prices are not like-for-like. Both in USD, so shown side by side.</p>')
s.append('<h2>Pooled demand vs MOQ - can we rely on it?</h2>' + tbl(['Supplier', 'MOQ', 'Pooled qty (all 5 buyers)', 'Slack (+) / short (-)', 'Pool if one buyer drops', 'Excess if only our customer buys at MOQ', 'Value of that excess USD'],
    [[E(k), str(v['moq']), str(v['pooled_total']), str(v['slack_or_short']), str(v['pooled_without_one_buyer']) + (' - below MOQ' if not v['meets_moq_if_one_drops'] else ''), str(v['excess_units_if_only_customer_buys_at_moq']), f"{v['excess_value_if_only_customer_buys']:.2f}"] for k, v in bc['coverage'].items()]))
s.append(f"<p><b>Answer:</b> pooling the {C['buyers']} buyers in coalition_demand.csv gives {C['pooled_qty_total']} rails, which exactly reaches Xylem's MOQ of {cx['moq']} and does not reach Yarrow's {cy['moq']}. <b>It cannot be relied on:</b> {C['buyers_no_signed_commitment']} of the {C['buyers']} rows ({C['qty_expressed_interest_no_signed_commitment']} units) are 'expressed interest by email; no signed commitment', and the remaining {C['qty_rfq_customer']} are our own RFQ customer, who has not ordered either - {C['qty_with_signed_commitment']} units are committed. There is zero slack. A forecast is never inflated to reach a price; a supplier package should state the demand as {C['qty_rfq_customer']} for a current enquiry plus up to {C['qty_expressed_interest_no_signed_commitment']} unconfirmed interest. Relying on the pool needs signed purchase commitments (or the customer accepting a 100-piece buy) before any order.</p>")
s.append('<h2>Draft supplier emails (restatement requests) - HELD, not sent</h2><p class="mut">Held for all: no supplier address on file, no released RFQ package, no approved supplier list, and the line-2 bid decision (Gate 2) is undecided.</p>')
for bb in b:
    body = open(f"out/sourcing-output/restatement-{bb['ref']}.txt", encoding='utf-8').read()
    s.append(f"<pre>=== SUPPLIER EMAIL - HELD - {E(bb['supplier'])} ===\n[recipient: not on file]\n{E(body)}\n=== END ===</pre>")
s.append('<p class="mut">Outbound check: each draft read alone; it names no other supplier, no other bid price, no PO price and no rate.</p>')
s.append('<h2>Detail: bid records (fields_missing)</h2>' + tbl(['Supplier', 'Ref', 'Item as quoted', 'conformance', 'fields_missing', 'Source'], [[E(x['supplier']), E(x['ref']), E(x['item']), 'off_format', E('; '.join(x['fields_missing'])), E(x['file'])] for x in b]))
s.append('<h2>Figures block</h2>' + tbl(['Figure', 'Value', 'From'], [[E(f"Extended {t['supplier']} at {t['break']}"), E(str(t['ext'])), 'unit x qty where qty >= MOQ'] for t in bc['table']] + [[k, E(str(v)), 'coalition_demand.csv'] for k, v in C.items()]))
s.append('</body></html>')
open('out/sourcing-output/bid-comparison.html', 'w', encoding='utf-8').write('\n'.join(s))
print('ok', DAYS)
