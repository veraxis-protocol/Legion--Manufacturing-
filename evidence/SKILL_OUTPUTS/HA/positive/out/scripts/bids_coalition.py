import csv, json
bids = [
 {'supplier':'Xylem Linear Motion (fictitious)','supplier_id':'unlisted','ref':'XL-5512','file':'inputs/e2e_bids/rail_bid_X.txt','src':'rail_bid_X.txt lines 2-3',
  'item':'MGN9H miniature linear rail, length 170 mm, standard accuracy','unit_price':11.40,'currency':'USD','price_basis':'"Unit price 11.40 USD at 100 pcs"',
  'moq':100,'lead':'"Lead time 3 weeks" (no start event named)','freight':'FOB origin','validity':'"valid 21 days" - quote date not stated, so expiry date cannot be computed',
  'scope':'"Rail only (no carriage)"','accuracy':'standard accuracy','cut_tol':None,
  'fields_missing':['received_at / quote date (validity_until cannot be computed)','breaks[20].unit_price (priced only at 100 pcs)','lead_time_first_article','lead_time_production from a named event','tooling_price or statement none needed','tooling_ownership','quality_clause_acceptance (not_stated)','cut-length tolerance','exceptions list (none listed)']},
 {'supplier':'Yarrow Motion Parts (fictitious)','supplier_id':'unlisted','ref':'YMP-208','file':'inputs/e2e_bids/rail_bid_Y.txt','src':'rail_bid_Y.txt lines 2-3',
  'item':'MGN9 rail cut to 170 mm, accuracy class not stated','unit_price':9.90,'currency':'USD','price_basis':'"9.90 USD each, minimum order 250 pcs"',
  'moq':250,'lead':'"Lead 5 weeks" (no start event named)','freight':'Delivered DDP','validity':None,
  'scope':'not stated whether carriage included','accuracy':None,'cut_tol':'+/-0.5 mm',
  'fields_missing':['received_at / quote date','validity_until (not stated)','accuracy class','carriage included or not','breaks[20].unit_price and breaks[100].unit_price (quantity for 9.90 not tied to a break below MOQ)','lead_time_first_article','lead_time_production from a named event','tooling_price or statement none needed','tooling_ownership','quality_clause_acceptance (not_stated)','exceptions list (none listed)']},
]
breaks = [20, 100, 250]
table = []
for q in breaks:
    for b in bids:
        buyable = q >= b['moq']
        table.append({'break':q,'supplier':b['supplier'],'unit':b['unit_price'],'ext':round(b['unit_price']*q,2) if buyable else None,
                      'moq_flag': None if buyable else f"MOQ {b['moq']} > {q}: price does not buy this quantity",
                      'min_order_value': round(b['unit_price']*b['moq'],2)})
rows = list(csv.DictReader(l for l in open('inputs/coalition_demand.csv',encoding='utf-8') if not l.startswith('#')))
total = sum(int(r['qty']) for r in rows)
signed = sum(int(r['qty']) for r in rows if 'signed' in r['status'].lower() and 'no signed' not in r['status'].lower())
unsigned_interest = sum(int(r['qty']) for r in rows if 'no signed commitment' in r['status'])
rfq_customer = sum(int(r['qty']) for r in rows if 'RFQ customer' in r['status'])
n_unsigned = sum(1 for r in rows if 'no signed commitment' in r['status'])
cov = {}
for b in bids:
    cov[b['supplier']] = {'moq':b['moq'],'pooled_total':total,'meets_moq_if_all_buy': total>=b['moq'],'slack_or_short': total-b['moq'],
       'customer_only_short': rfq_customer-b['moq'],'excess_units_if_only_customer_buys_at_moq': b['moq']-rfq_customer,
       'excess_value_if_only_customer_buys': round((b['moq']-rfq_customer)*b['unit_price'],2),
       'pooled_without_one_buyer': total-20, 'meets_moq_if_one_drops': (total-20)>=b['moq']}
fig = {'buyers':len(rows),'pooled_qty_total':total,'qty_with_signed_commitment':signed,'qty_expressed_interest_no_signed_commitment':unsigned_interest,
       'buyers_no_signed_commitment':n_unsigned,'qty_rfq_customer':rfq_customer,'need_by_dates':sorted({r['need_by'] for r in rows})}
json.dump({'bids':bids,'table':table,'coalition':fig,'coverage':cov}, open('out/bid_and_coalition_figures.json','w'), indent=1)
print(json.dumps({'table':table,'coalition':fig,'coverage':cov}, indent=1))
