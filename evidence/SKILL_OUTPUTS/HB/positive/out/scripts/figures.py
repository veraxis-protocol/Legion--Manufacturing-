# Computes every figure used in the RFQ work products from the input files. Writes figures.json and the BOM CSV.
import json, csv, re, sys, os
W = sys.argv[1]; I = os.path.join(W, 'inputs'); O = os.path.join(W, 'out')
bom = json.load(open(os.path.join(I, '02_bom_handoff.json')))
eng = json.load(open(os.path.join(I, '02_engineering.json')))
com = json.load(open(os.path.join(I, '06_commercial.json')))
inst = json.load(open(os.path.join(O, 'step_instance_counts.json')))['leaf_counts']
geo = json.load(open(os.path.join(O, 'step_leaf_geometry.json')))
readme = open(os.path.join(I, 'readme.md'), encoding='utf-8').read().splitlines()
SETS = 20  # rfq_rebot_email.txt: "for 20 sets"
# STEP product for each readme CNC part, matched on face count and instance count (text read of the STEP)
MAP = {'02_BASE_REINFORCEMENT_PART': '2-M1-STATOR-1', '02_ARM_YAW_LIMIT': '2-M1-ROTOR-1',
       '02_MOTOR_FRONT_SPACER': '2-SHAFT-SLEEVE-ROTATOR-1', '02_MOTOR_BACK_SPACER': '2-SPACE-STATOR-1',
       '02_FLANGE': '2-SHAFT-SLEEVE-STATOR-1', '02_WRIST_BRACKET': '2026-07-01-11-37-27-375',
       '02_GRIPPER_CONNECTOR_A': '2-M6-ROTOR', '02_GRIPPER_CONNECTOR_B': '2-M7-STATOR',
       '02_SLIDER_BRACKET': '2-RAIL-BASE-1', '02_SLIDER_EXTENSION': '2-SLIDER-FIX',
       '02_LOWER_UPPER_LINK_L': '2-CONNECTING-ROD-1-L', '02_LOWER_UPPER_LINK_R': '2-CONNECTING-ROD-1-R',
       '02_LOWER_WRIST_LINK_L': '2-CONNECTING-ROD-2-L', '02_LOWER_WRIST_LINK_R': '2-CONNECTING-ROD-2-R',
       '02_GEAR_CONNECTOR': '2-M7-ROTOR', '02_RACK': '2-RACK-1M', '03_LINK1': '2-U-PLATE-1',
       '03_LINK2': '2-LINK-1-ARM', '03_LINK3_L': '1-LINK-2-ARM-L', '03_LINK3_R': '2-LINK-2-ARM-R',
       '03_LINK5': '2-M5-ROTOR-L'}
assert len(set(MAP.values())) == len(MAP)
pos = []
for p in bom['cnc_parts']:
    sp = MAP[p['part_id']]; ln = int(p['material_source'].split()[-1])
    rq = readme[ln - 1].split('|'); readme_qty = int(rq[5].strip())
    pos.append(dict(part_id=p['part_id'], description=rq[1].strip(), file=rq[3].strip(), material=rq[4].strip(),
                    process=p['process'], readme_line=ln, qty_readme=readme_qty, qty_legion=p['quantity_per_arm'],
                    step_product=sp, qty_step=inst[sp], faces_legion=p['geometry_from_step']['faces'],
                    faces_step_text=geo[sp]['faces'], bbox_legion_mm=p['geometry_from_step']['bbox'],
                    vertex_extents_step_text_mm=geo[sp]['vertex_extents_sorted_mm'],
                    volume_legion_mm3=p['geometry_from_step']['volume'],
                    qty_agree=(readme_qty == p['quantity_per_arm'] == inst[sp]),
                    faces_agree=(p['geometry_from_step']['faces'] == geo[sp]['faces']),
                    qty_20_sets=readme_qty * SETS))
# readme CNC table rows actually present (lines starting with '| ' and containing 'Aluminum Alloy 5052')
readme_cnc_rows = [i + 1 for i, l in enumerate(readme) if 'Aluminum Alloy 5052' in l and l.startswith('|')]
po_rows = list(csv.DictReader([l for l in open(os.path.join(I, 'purchase_orders_5052.csv')) if not l.startswith('#')]))
stock = []
for r in po_rows:
    nums = [float(x) for x in re.findall(r'(\d+(?:\.\d+)?)', r['description'].split('H32')[1])]
    t, a, b = nums[:3]
    stock.append(dict(po=r['po_number'], date=r['po_date'], received=r['received_date'], item=r['item'],
                      description=r['description'], t=t, area_mm2=a * b, unit_price=float(r['unit_price_usd']),
                      usd_per_m2=round(float(r['unit_price_usd']) / (a * b / 1e6), 4)))
stock.sort(key=lambda s: s['t'])
mat = []
for q in pos:
    d = sorted(q['bbox_legion_mm']); tmin = d[0]; foot = d[1] * d[2]
    row = dict(part_id=q['part_id'], qty_per_set=q['qty_readme'], min_bbox_dim_mm=tmin, footprint_mm2=round(foot, 1))
    if q['process'] != 'CNC':
        row.update(status='blocked', reason='CNC + Sheet Metal: flat blank and sheet gauge are not in the inputs (the STEP holds the formed part only)')
    else:
        cand = [s for s in stock if s['t'] >= tmin]
        if not cand:
            row.update(status='blocked', reason='smallest bbox dimension %s mm exceeds the thickest PO stock (%s mm); no PO price for suitable stock' % (tmin, stock[-1]['t']))
        else:
            s = cand[0]; per = s['unit_price'] * foot / s['area_mm2']
            row.update(status='lower_bound', stock_po=s['po'], stock_po_date=s['date'], stock=s['description'], stock_t_mm=s['t'],
                       thickness_margin_mm=round(s['t'] - tmin, 3), fits_only_without_cleanup=(abs(s['t'] - tmin) < 1e-9),
                       usd_per_piece_lb=round(per, 4), usd_per_set_lb=round(per * q['qty_readme'], 4))
    mat.append(row)
priced = [m for m in mat if m['status'] == 'lower_bound']
fig = dict(
    cnc_positions=len(pos), readme_cnc_table_rows=len(readme_cnc_rows),
    cnc_pieces_per_set=sum(q['qty_readme'] for q in pos), cnc_pieces_20_sets=sum(q['qty_20_sets'] for q in pos),
    positions_qty_agree_readme_legion_step=sum(q['qty_agree'] for q in pos),
    positions_faces_agree_legion_vs_text_read=sum(q['faces_agree'] for q in pos),
    positions_cnc_only=sum(q['process'] == 'CNC' for q in pos), positions_cnc_plus_sheet=sum(q['process'] != 'CNC' for q in pos),
    pieces_cnc_plus_sheet_per_set=sum(q['qty_readme'] for q in pos if q['process'] != 'CNC'),
    material_positions_lower_bound=len(priced), material_positions_blocked=len(mat) - len(priced),
    material_pieces_per_set_lower_bound=sum(m['qty_per_set'] for m in priced),
    material_usd_per_set_lower_bound_priced_positions_only=round(sum(m['usd_per_set_lb'] for m in priced), 2),
    positions_fit_only_without_cleanup=[m['part_id'] for m in priced if m['fits_only_without_cleanup']],
    step_leaf_instances=sum(inst.values()), step_leaf_definitions=len(inst))
bids = {'X': dict(file='e2e_bids/rail_bid_X.txt', supplier='Xylem Linear Motion (fictitious)', ref='XL-5512', unit=11.40,
                  qty_quoted=100, moq=100, lead='3 weeks (from no named event)', incoterm='FOB origin',
                  validity='21 days (quote date not stated)', accuracy='standard accuracy', cut_tol='not stated',
                  currency='USD', scope='rail only (no carriage)'),
        'Y': dict(file='e2e_bids/rail_bid_Y.txt', supplier='Yarrow Motion Parts (fictitious)', ref='YMP-208', unit=9.90,
                  qty_quoted=None, moq=250, lead='5 weeks (from no named event)', incoterm='Delivered DDP',
                  validity='not stated', accuracy='not stated', cut_tol='+/-0.5 mm', currency='USD',
                  scope='MGN9 rail cut to 170 mm (carriage not stated)')}
need = SETS * bom['purchased_rail']['quantity_per_arm']
for k, b in bids.items():
    b['min_commitment_usd'] = round(b['unit'] * b['moq'], 2)
    b['moq_exceeds_need'] = b['moq'] > need
    b['excess_units_at_moq'] = b['moq'] - need
    b['excess_cost_at_moq_usd'] = round((b['moq'] - need) * b['unit'], 2)
    b['moq_spend_per_needed_rail_derived'] = round(b['min_commitment_usd'] / need, 2)
coal = list(csv.DictReader([l for l in open(os.path.join(I, 'coalition_demand.csv')) if not l.startswith('#')]))
pooled = sum(int(r['qty']) for r in coal)
fig.update(rails_needed_20_sets=need, rail_bids=bids, coalition_rows=len(coal), coalition_units=pooled,
           coalition_meets_X_moq=pooled >= bids['X']['moq'], coalition_meets_Y_moq=pooled >= bids['Y']['moq'],
           coalition_headroom_vs_X_units=pooled - bids['X']['moq'], coalition_shortfall_vs_Y_units=bids['Y']['moq'] - pooled,
           coalition_rows_no_signed_commitment=sum('no signed commitment' in r['status'] for r in coal),
           coalition_rows_rfq_customer=sum('RFQ customer' in r['status'] for r in coal),
           coalition_units_if_one_buyer_drops=pooled - max(int(r['qty']) for r in coal),
           legion_engineering_verdict=eng['verification']['engineering_verdict'],
           legion_predicates=eng['verification']['aggregate']['mandatory_predicates'],
           legion_bom_mismatches=eng['bom']['mismatches'], legion_gates=com['gates'])
json.dump(dict(figures=fig, positions=pos, material=mat, stock=stock), open(os.path.join(O, 'figures.json'), 'w'), indent=1)
with open(os.path.join(O, 'cnc_bom_per_arm.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['line', 'part_id', 'description (readme)', 'readme file', 'material', 'process', 'qty_per_arm_readme',
                'qty_per_arm_LEGION', 'STEP product (text read)', 'qty_per_arm_STEP', 'faces_LEGION', 'faces_STEP_text',
                'qty_agree', 'qty_20_sets', 'readme_line'])
    for n, q in enumerate(pos, 1):
        w.writerow([n, q['part_id'], q['description'], q['file'], q['material'], q['process'], q['qty_readme'], q['qty_legion'],
                    q['step_product'], q['qty_step'], q['faces_legion'], q['faces_step_text'], q['qty_agree'],
                    q['qty_20_sets'], q['readme_line']])
print(json.dumps(fig, indent=1))
for m in mat: print(m)
