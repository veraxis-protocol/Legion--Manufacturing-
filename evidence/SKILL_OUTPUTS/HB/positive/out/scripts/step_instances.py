# Reads the STEP as text (C1: STEP read without CAD, unverified): products and assembly instance counts.
import re, sys, collections, json
p = sys.argv[1]
txt = open(p, encoding='latin-1').read()
ents = {}
for m in re.finditer(r'#(\d+)\s*=\s*(.*?);\s*(?=#\d+\s*=|ENDSEC)', txt, re.S):
    ents[int(m.group(1))] = ' '.join(m.group(2).split())
prod = {}; pdf = {}; pd = {}
for i, s in ents.items():
    if s.startswith("PRODUCT("):
        prod[i] = re.match(r"PRODUCT\('([^']*)'", s).group(1)
    elif s.startswith("PRODUCT_DEFINITION_FORMATION"):
        r = re.findall(r'#(\d+)', s); pdf[i] = int(r[-1])
    elif s.startswith("PRODUCT_DEFINITION(") or s.startswith("PRODUCT_DEFINITION ("):
        r = re.findall(r'#(\d+)', s); pd[i] = int(r[0])
def pname(pdid): return prod[pdf[pd[pdid]]]
children = collections.defaultdict(list); is_child=set()
for i, s in ents.items():
    if s.startswith("NEXT_ASSEMBLY_USAGE_OCCURRENCE"):
        r = [int(x) for x in re.findall(r'#(\d+)', s)][:2]
        children[r[0]].append((r[1], i)); is_child.add(r[1])
roots = [d for d in pd if d not in is_child]
count = collections.Counter()
def walk(d, mult):
    count[d] += mult
    for c, _ in children[d]: walk(c, mult)
for r in roots: walk(r, 1)
leaf = {pname(d): n for d, n in count.items() if not children[d]}
asm = {pname(d): n for d, n in count.items() if children[d]}
print(json.dumps({"file": p.split('/')[-1], "entities": len(ents), "products": len(prod),
  "roots": [pname(r) for r in roots], "assemblies": len(asm), "leaf_definitions": len(leaf),
  "leaf_instances": sum(leaf.values()), "leaf_counts": dict(sorted(leaf.items()))}, indent=1))
