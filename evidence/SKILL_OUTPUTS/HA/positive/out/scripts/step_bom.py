"""Read a STEP AP214/AP242 assembly as text: products, assembly tree (NAUO), flattened instance counts.
No CAD kernel; values are read from entity text only (C1: STEP read without CAD, unverified)."""
import re, sys, json, collections
path = sys.argv[1]; out = sys.argv[2]
ent = {}
buf = ''
with open(path, 'r', encoding='latin-1') as f:
    data = f.read()
datasec = data.split('DATA;',1)[1]
for m in re.finditer(r'#(\d+)\s*=\s*(.*?);\s*(?=#\d+\s*=|ENDSEC)', datasec, re.S):
    ent[int(m.group(1))] = m.group(2).replace('\n',' ').replace('\r','')
def refs(s): return [int(x) for x in re.findall(r'#(\d+)', s)]
prod = {}; pdf = {}; pd = {}
for i,s in ent.items():
    if s.startswith('PRODUCT('):
        a = re.findall(r"'([^']*)'", s); prod[i] = {'id':a[0],'name':a[1] if len(a)>1 else '','desc':a[2] if len(a)>2 else ''}
for i,s in ent.items():
    if s.startswith('PRODUCT_DEFINITION_FORMATION'):
        r = refs(s); pdf[i] = r[-1]
for i,s in ent.items():
    if s.startswith('PRODUCT_DEFINITION(') :
        r = refs(s); pd[i] = r[0]
def pd_name(p): return prod[pdf[pd[p]]]['id']
children = collections.defaultdict(list); nauo_rows=[]
for i,s in ent.items():
    if s.startswith('NEXT_ASSEMBLY_USAGE_OCCURRENCE('):
        r = refs(s); a = re.findall(r"'([^']*)'", s)
        parent, child = r[0], r[1]
        children[parent].append(child); nauo_rows.append((i,a[1] if len(a)>1 else '',pd_name(parent),pd_name(child)))
allchild = {c for v in children.values() for c in v}
roots = [p for p in children if p not in allchild]
flat = collections.Counter(); direct = {}
def walk(p, mult, depth, lines):
    cnt = collections.Counter(children[p])
    for c,n in sorted(cnt.items(), key=lambda x: pd_name(x[0])):
        lines.append(('  '*depth)+f"{pd_name(c)} x{n} (per parent; cumulative x{mult*n}) [#{c}]")
        if children.get(c): walk(c, mult*n, depth+1, lines)
        else: flat[pd_name(c)] += mult*n
tree=[]
for r in roots:
    tree.append(f"ROOT {pd_name(r)} [#{r}]"); walk(r,1,1,tree)
units = sorted(set(re.findall(r'SI_UNIT\(([^)]*)\)', datasec)))[:10]
res = {'file':path,'entity_count':len(ent),'product_count':len(prod),'nauo_count':len(nauo_rows),
       'roots':[pd_name(r) for r in roots],'leaf_instances_total':sum(flat.values()),
       'leaf_instance_counts':dict(sorted(flat.items())),'si_units':units,
       'products':{prod[k]['id']:{'entity':k,'name':prod[k]['name'],'desc':prod[k]['desc']} for k in prod},'tree':tree}
json.dump(res, open(out,'w'), indent=1)
print('entities',len(ent),'products',len(prod),'nauo',len(nauo_rows),'roots',res['roots'],'leaf instances',sum(flat.values()))
print('\n'.join(tree))
