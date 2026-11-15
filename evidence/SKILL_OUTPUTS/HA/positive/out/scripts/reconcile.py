import json, re, collections
d = json.load(open('out/step_structure.json'))
name_of = {k: v['name'] for k, v in d['products'].items()}
step_by_file = collections.Counter()
for pid, n in d['leaf_instance_counts'].items():
    step_by_file[name_of[pid]] += n
pid_of = {v['name']: k for k, v in d['products'].items()}
txt = open('inputs/readme.md', encoding='utf-8').read()
sec = txt.split('## 🔩 CNC Machined Metal Parts')[1].split('### 🧩 Machining')[0]
rows = []
for line in sec.splitlines():
    c = [x.strip() for x in line.strip().strip('|').split('|')]
    if len(c) >= 7 and c[2].endswith('.step'):
        rows.append({'description': c[0], 'file': c[2], 'material': c[3], 'readme_qty': int(c[4]), 'machining': c[5], 'notes': c[6]})
out = []
for r in rows:
    stem = r['file'][:-5]
    sq = step_by_file.get(stem)
    pid = pid_of.get(stem)
    r.update({'step_product_id': pid, 'step_entity': d['products'][pid]['entity'] if pid else None, 'step_qty': sq,
              'status': 'match' if sq == r['readme_qty'] else ('not in STEP' if sq is None else 'QTY MISMATCH')})
    out.append(r)
cnc_files = {r['file'][:-5] for r in rows}
# STEP leaf parts whose product id has metal prefix '2-' or whose name starts '02_'/'03_' but not in readme CNC table
extra = []
for pid, n in d['leaf_instance_counts'].items():
    nm = name_of[pid]
    if (pid.startswith('2-') or nm.startswith('02_') or nm.startswith('03_')) and nm not in cnc_files:
        extra.append({'step_product_id': pid, 'name': nm, 'step_qty': n})
prefix_anom = [{'step_product_id': pid, 'name': name_of[pid]} for pid in d['leaf_instance_counts']
               if (name_of[pid].startswith(('02_', '03_')) and not pid.startswith('2-') and not pid.startswith('20'))
               or (name_of[pid].startswith('01_') and pid.startswith('2-'))]
fig = {'readme_cnc_rows': len(rows), 'readme_cnc_qty_per_arm': sum(r['readme_qty'] for r in rows),
       'step_qty_for_readme_cnc_rows': sum(r['step_qty'] or 0 for r in rows),
       'rows_matching': sum(r['status'] == 'match' for r in rows),
       'rows_mismatch_or_missing': sum(r['status'] != 'match' for r in rows),
       'cnc_parts_for_20_sets': 20 * sum(r['readme_qty'] for r in rows),
       'step_leaf_instances_total': d['leaf_instances_total'], 'step_products': d['product_count'],
       'step_nauo': d['nauo_count']}
json.dump({'rows': out, 'extra_metal_named_in_step': extra, 'prefix_anomalies': prefix_anom, 'figures': fig},
          open('out/bom_reconciliation.json', 'w'), indent=1)
for r in out: print(r['readme_qty'], r['step_qty'], r['status'], r['file'], r['step_product_id'], r['step_entity'], r['machining'])
print('extra', extra); print('prefix anomalies', prefix_anom); print(fig)
