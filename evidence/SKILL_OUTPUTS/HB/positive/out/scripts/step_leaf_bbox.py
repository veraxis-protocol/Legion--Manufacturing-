# Text read of the STEP (unverified, no CAD kernel): per leaf product, approximate local bbox from
# VERTEX_POINT coordinates plus circle radii reachable from its shape representation; counts faces.
import re, sys, json, collections
txt = open(sys.argv[1], encoding='latin-1').read()
ents = {}
for m in re.finditer(r'#(\d+)\s*=\s*(.*?);\s*(?=#\d+\s*=|ENDSEC)', txt, re.S):
    ents[int(m.group(1))] = ' '.join(m.group(2).split())
typ = {i: s.split('(')[0].strip() for i, s in ents.items()}
refs = lambda i: [int(x) for x in re.findall(r'#(\d+)', ents[i])]
prod={};pdf={};pd={}
for i,s in ents.items():
    t=typ[i]
    if t=='PRODUCT': prod[i]=re.match(r"PRODUCT\('([^']*)'",s).group(1)
    elif t=='PRODUCT_DEFINITION_FORMATION' or t=='PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE': pdf[i]=refs(i)[-1]
    elif t=='PRODUCT_DEFINITION': pd[i]=refs(i)[0]
pds={i:refs(i)[-1] for i in ents if typ[i]=='PRODUCT_DEFINITION_SHAPE'}
sdr={}
for i in ents:
    if typ[i]=='SHAPE_DEFINITION_REPRESENTATION':
        a,b=refs(i)[:2]; sdr[a]=b
rel=collections.defaultdict(list)
for i,s in ents.items():
    if s.startswith('SHAPE_REPRESENTATION_RELATIONSHIP') or 'SHAPE_REPRESENTATION_RELATIONSHIP(' in s and 'REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION' not in s:
        r=refs(i)
        if len(r)>=2: rel[r[0]].append(r[1]); rel[r[1]].append(r[0])
nauo_parents=set()
for i in ents:
    if typ[i]=='NEXT_ASSEMBLY_USAGE_OCCURRENCE': nauo_parents.add(refs(i)[0])
skip={'GEOMETRIC_REPRESENTATION_CONTEXT','SHAPE_REPRESENTATION','PRESENTATION_STYLE_ASSIGNMENT','STYLED_ITEM'}
out={}
for pdid,prodf in pd.items():
    if pdid in nauo_parents: continue
    name=prod[pdf[prodf]]
    sh=[k for k,v in pds.items() if v==pdid]
    reps=set()
    for k in sh:
        if k in sdr: reps.add(sdr[k])
    allreps=set(reps)
    for r in list(reps): allreps.update(rel.get(r,[]))
    seen=set(); stack=[]
    for r in allreps:
        if typ.get(r,'').startswith('ADVANCED_BREP') or typ.get(r,'')=='MANIFOLD_SURFACE_SHAPE_REPRESENTATION':
            stack += [x for x in refs(r) if typ.get(x)!='GEOMETRIC_REPRESENTATION_CONTEXT' and not ents[x].startswith('(')]
    pts=[];faces=0;solids=0
    while stack:
        x=stack.pop()
        if x in seen: continue
        seen.add(x); t=typ[x]
        if t=='ADVANCED_FACE': faces+=1
        if t=='MANIFOLD_SOLID_BREP': solids+=1
        if t=='VERTEX_POINT':
            cp=refs(x)[0]; pts.append([float(v) for v in re.findall(r'[-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?', ents[cp].split(',(')[1])])
        if t in ('VERTEX_POINT','CARTESIAN_POINT','DIRECTION'): continue
        stack += refs(x)
    if pts:
        mn=[min(p[k] for p in pts) for k in range(3)]; mx=[max(p[k] for p in pts) for k in range(3)]
        ext=sorted(round(mx[k]-mn[k],3) for k in range(3))
    else: ext=None
    out[name]={'solids':solids,'faces':faces,'vertex_extents_sorted_mm':ext,'vertices':len(pts)}
print(json.dumps(out,indent=1))
