import csv, json, math, datetime as dt, os
os.chdir(r'C:/LMFG/runs/B06-positive/work')  # script kept in out/scripts
def rd(p): return list(csv.DictReader(l for l in open(p) if not l.startswith('#')))
R=rd('inputs/cost/routings.csv'); A=rd('inputs/cost/closed_jobs.csv'); P=rd('inputs/cost/purchase_orders.csv'); E=rd('inputs/plant/equipment.csv')
today=dt.date(2026,11,14); F=[]
def f(name,val,src,flt):
    F.append(dict(figure=name,value=val,computed_from=src,filter=flt)); print(name,'=',val)
f('routing rows / actuals rows / PO rows / equipment rows',f"{len(R)}/{len(A)}/{len(P)}/{len(E)}",'inputs csvs','all rows')
dates=[r['closed_date'] for r in A]+[r['po_date'] for r in P]+[r['received_date'] for r in P]
f('earliest / latest transaction date in cost files',f"{min(dates)} / {max(dates)}",'closed_jobs, purchase_orders','min/max of closed_date, po_date, received_date')
f('future-dated rows (after 2026-11-14)',sum(dt.date.fromisoformat(d)>today for d in dates),'same','date > run date')
f('routing rows for MB-2040 / actuals rows for MB-2040',f"{sum(r['part']=='MB-2040' for r in R)} / {sum(a['part']=='MB-2040' for a in A)}",'routings, closed_jobs',"part=='MB-2040'")
rt={(r['part'],r['rev'],r['op']):r for r in R}
out=[]
for a in A:
    r=rt[(a['part'],a['rev'],a['op'])]
    q=int(a['qty_completed']); qs=int(a['qty_scrapped'])
    rpu=float(a['actual_run_min_total'])/q
    std=float(r['run_min_per_unit']); var=(rpu-std)/std
    vs=(float(a['actual_setup_min'])-float(r['setup_min']))/float(r['setup_min'])
    conf='probable_standard' if abs(var)<=0.01 else 'recorded'
    out.append(dict(a, run_min_per_unit_actual=round(rpu,3), routing_run_min_per_unit=std, run_var_vs_routing=round(var,4), setup_var_vs_routing=round(vs,4), actuals_confidence=conf, time_unit='minutes (declared by header _min)', note='MB-1880 rev B similar-part history; not MB-2040'))
    f(f"{a['work_order']} op{a['op']} actual run min/pc",round(rpu,3),'closed_jobs.csv',f"{a['actual_run_min_total']}/{q} (qty_completed)")
    f(f"{a['work_order']} op{a['op']} run variance vs MB-1880 routing",f"{var:+.1%}",'closed_jobs vs routings',f"({rpu:.3f}-{std})/{std}")
    f(f"{a['work_order']} op{a['op']} setup variance vs routing",f"{vs:+.1%}",'closed_jobs vs routings',f"({a['actual_setup_min']}-{r['setup_min']})/{r['setup_min']}")
    f(f"{a['work_order']} op{a['op']} actuals_confidence",conf,'backflush check','|run var vs routing| <= 1%')
for op in ('20','30'):
    x=[o for o in out if o['op']==op]
    d=abs(x[0]['run_min_per_unit_actual']-x[1]['run_min_per_unit_actual'])/min(o['run_min_per_unit_actual'] for o in x)
    f(f"op{op} WO-7702 vs WO-7811 run/pc difference",f"{d:.1%}",'closed_jobs','|a-b|/min (probable_standard if about 1%)')
f('actuals rows flagged probable_standard',sum(o['actuals_confidence']=='probable_standard' for o in out),'backflush check','count')
for op in ('20','30'):
    x=sorted(o['run_min_per_unit_actual'] for o in out if o['op']==op); s=sorted(int(o['actual_setup_min']) for o in out if o['op']==op)
    f(f"MB-1880 op{op} actual run min/pc low/median/high",f"{x[0]}/{(x[0]+x[1])/2:.3f}/{x[1]}",'closed_jobs','2 WOs')
    f(f"MB-1880 op{op} actual setup min low/median/high",f"{s[0]}/{(s[0]+s[1])/2}/{s[1]}",'closed_jobs','2 WOs')
f('actuals rows for ops 10 and 40',sum(o['op'] in('10','40') for o in out),'closed_jobs','op in (10,40)')
setup_total=sum(float(r['setup_min']) for r in R); run_pc=sum(float(r['run_min_per_unit']) for r in R)
f('MB-1880 routing total setup min (ops 10-40)',setup_total,'routings.csv','sum setup_min')
f('MB-1880 routing total run min/pc (ops 10-40)',round(run_pc,2),'routings.csv','sum run_min_per_unit')
Q=[250,500,1000]
for q in Q:
    f(f'Q{q}: setup min per pc (routing setup amortised)',round(setup_total/q,4),'routings.csv',f'{setup_total}/{q}')
    for wc in ('MILL-V','INSP'):
        su=sum(float(r['setup_min']) for r in R if r['work_center']==wc); rn=sum(float(r['run_min_per_unit']) for r in R if r['work_center']==wc)
        f(f'Q{q}: {wc} work content h (setup+run, rung 4)',round((su+rn*q)/60,2),'routings.csv',f'({su}+{rn:.1f}*{q})/60')
pw,pl,pt=12*25.4,48*25.4,0.5*25.4
o1=math.floor(pw/80)*math.floor(pl/120); o2=math.floor(pw/120)*math.floor(pl/80); per=max(o1,o2)
f('plate size mm (t x w x l)',f"{pt:.1f} x {pw:.1f} x {pl:.1f}",'PO description 0.5in x 12in x 48in','inch*25.4')
f('plate thickness over finished 12 mm',f"{pt-12:.1f} mm",'PO vs spec','12.7-12')
f('blanks per plate, zero kerf/cleanup (upper bound)',f"{per} (orientations {o1} / {o2})",'geometry','floor(304.8/80)*floor(1219.2/120) vs floor(304.8/120)*floor(1219.2/80)')
p1,p2=212.40,219.90
f('plate price change PO-30411 to PO-30588',f"{(p2-p1)/p1:+.2%}",'purchase_orders.csv','(219.90-212.40)/212.40')
scr=[6/306,9/509]; sa=max(scr)
f('scrap allowance basis (higher MB-1880 observed rate)',f"{sa:.2%}",'closed_jobs','max(6/306, 9/509)')
for q in Q:
    starts=math.ceil(q*(1+sa)); plates=math.ceil(starts/per)
    f(f'Q{q}: blanks started / plates',f"{starts} / {plates}",'computed',f'ceil({q}*(1+{sa:.4f})); ceil(starts/{per})')
    f(f'Q{q}: material cost line before markup',f"{plates*p2:.2f} USD",'PO-30588 2026-09-30',f'{plates}*219.90')
    f(f'Q{q}: material cost per finished pc before markup',f"{plates*p2/q:.3f} USD",'PO-30588',f'{plates}*219.90/{q}')
    lots=math.ceil(q/300)
    f(f'Q{q}: anodize lots / cost before markup / per pc',f"{lots} / {lots*385:.2f} / {lots*385/q:.3f} USD",'PO-30602 2026-10-03',f'ceil({q}/300)*385.00')
for po in P:
    lt=(dt.date.fromisoformat(po['received_date'])-dt.date.fromisoformat(po['po_date'])).days
    f(f"{po['po_number']} order-to-receipt days",lt,'purchase_orders.csv','received_date-po_date')
f('days run date to 2027-01-15',(dt.date(2027,1,15)-today).days,'request','calendar days')
json.dump(F,open('out/figures-MB-2040-quote.json','w'),indent=1)
with open('out/dataset/operation_actuals.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
for name,rows in (('routings',R),('purchase_orders',P),('assets',E)):
    with open(f'out/dataset/{name}.csv','w',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
