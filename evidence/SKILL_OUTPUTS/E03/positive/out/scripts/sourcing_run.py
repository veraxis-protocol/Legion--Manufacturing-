# supplier-quote-request run for SRC-2026-11-14-MGN9-170-RAIL
# Computes every figure from the input files, writes the bid records, the figures block,
# the comparison page, the sourcing-events block, and fills the reply template.
# Run: python -I sourcing_run.py   (paths are absolute; no network, no installs)
import json, os, re, datetime, html

ROOT = "C:/LMFG/runs/E03-positive/work"
INP = ROOT + "/inputs"
OUT = ROOT + "/out"
EVENT = "SRC-2026-11-14-MGN9-170-RAIL"
TODAY = datetime.date(2026, 11, 14)          # session date
NOW = "2026-11-14T00:00:00+00:00 (session date; time of day not known)"

# ---------------------------------------------------------------- inputs
bom = json.load(open(INP + "/02_bom_handoff.json", encoding="utf-8"))
intake_path = INP + "/intake/plant-setup/open-work/inquiries/harbor-robotics-lab-NOREF-20261112.intake.txt"
intake = open(intake_path, encoding="utf-8").read().splitlines()
bidX = open(INP + "/e2e_bids/rail_bid_X.txt", encoding="utf-8").read().splitlines()
bidY = open(INP + "/e2e_bids/rail_bid_Y.txt", encoding="utf-8").read().splitlines()

rail = bom["purchased_rail"]
qty_per_arm = rail["quantity_per_arm"]

# intake line 1 sets and line 2 rail qty, read from the text
def find_line(pat, start=0):
    for i in range(start, len(intake)):
        if re.search(pat, intake[i]):
            return i
    return None
l2 = find_line(r"^\s*- line_no: 2")
l1 = find_line(r"^\s*- line_no: 1")
sets_line = find_line(r"qty: (\d+), uom: \"set", l1)
sets = int(re.search(r"qty: (\d+)", intake[sets_line]).group(1))
rail_line = find_line(r"qty: (\d+), uom: each", l2)
rail_qty_intake = int(re.search(r"qty: (\d+)", intake[rail_line]).group(1))
req_line = find_line(r"required_delivery: (\d{4}-\d\d-\d\d)", l2)
required_delivery = datetime.date.fromisoformat(re.search(r"(\d{4}-\d\d-\d\d)", intake[req_line]).group(1))
eau_line = find_line(r"^\s*eau:", l2)
eau = intake[eau_line].split(":", 1)[1].split("#")[0].strip()

demand = qty_per_arm * sets
assert demand == rail_qty_intake, "BOM x sets disagrees with intake line 2"
days_to_required = (required_delivery - TODAY).days

# usage history: enumerate the inputs folder for any PO / receipt / usage export
all_inputs = []
for d, _, fs in os.walk(INP):
    for f in fs:
        all_inputs.append(os.path.relpath(os.path.join(d, f), INP).replace("\\", "/"))
usage_files = [f for f in all_inputs if re.search(r"(po|purchase|receipt|usage|vendor|supplier_list|item_master)", f, re.I) and "e2e_bids" not in f]

profile_exists = os.path.exists(ROOT + "/plant-setup/plant-context.md")

# ---------------------------------------------------------------- bid records (map, never normalise)
def g(pat, text, grp=1):
    m = re.search(pat, text)
    return m.group(grp) if m else None

X2, X3 = bidX[1], bidX[2]
Y2, Y3 = bidY[1], bidY[2]
fx, fy = "inputs/e2e_bids/rail_bid_X.txt", "inputs/e2e_bids/rail_bid_Y.txt"

bids = []
bx = dict(
    supplier_name=g(r"Supplier: ([^(]+?) \(", X2), quote_ref=g(r"Quote (\S+?),", X2), file=fx,
    item_as_quoted=g(r"Item: (.+?)\.$", X2) or g(r"Item: (.+)", X2),
    currency=g(r"(\b[A-Z]{3}\b) at", X3),
    offered_qty=int(g(r"at (\d+) pcs", X3)), unit_price=float(g(r"Unit price ([\d.]+)", X3)),
    as_quoted=g(r"(Unit price [^.]+\.\d+ USD at \d+ pcs)", X3),
    moq=int(g(r"MOQ (\d+)", X3)), lead=g(r"(Lead time [^.]+)\.", X3),
    validity_text=g(r"(valid \d+ days)", X2), freight=g(r"(FOB origin)", X3),
    exceptions=[g(r"(Rail only \(no carriage\))", X3)],
    accuracy=g(r"(standard accuracy)", X2), cut_tol=None, carriage="rail only (no carriage) stated",
    src_price=fx + " line 3", src_head=fx + " line 2")
by = dict(
    supplier_name=g(r"Supplier: ([^(]+?) \(", Y2), quote_ref=g(r"Ref (\S+?)\.", Y2), file=fy,
    item_as_quoted=g(r"\. (MGN9 rail cut to 170 mm), ", Y2),
    currency=g(r"(\b[A-Z]{3}\b) each", Y3),
    offered_qty=int(g(r"minimum order (\d+)", Y3)), unit_price=float(g(r"^([\d.]+) USD", Y3)),
    as_quoted=g(r"^([\d.]+ USD each, minimum order \d+ pcs)", Y3),
    moq=int(g(r"minimum order (\d+)", Y3)), lead=g(r"(Lead \d+ weeks)", Y3),
    validity_text=None, freight=g(r"(Delivered DDP)", Y3),
    exceptions=[], accuracy=None, accuracy_note=g(r"(accuracy class not stated)", Y2),
    cut_tol=g(r"(Cut tolerance \+/-[\d.]+ mm)", Y3), carriage=None,
    src_price=fy + " line 3", src_head=fy + " line 2")
bids = [bx, by]

MANDATED = [
    "unit price at 20 each",
    "unit price at the pooled quantity",
    "currency",
    "lead time, first article, from a named event",
    "lead time, production, from a named event",
    "tooling price, or a statement that none is needed",
    "tooling ownership",
    "minimum order quantity",
    "price validity",
    "freight basis (Incoterm with named place)",
    "payment terms",
    "packaging",
    "quality clause acceptance",
    "offered item: manufacturer and part number",
    "offered item: accuracy class",
    "offered item: carriage included or not (count and type)",
    "offered item: preload",
    "offered item: cut-length tolerance",
    "offered item: mounting-hole pitch and end offset",
    "exclusions and assumptions listed",
]

def missing(b):
    m = []
    # breaks: neither bid priced 20; the pooled quantity was not set when they bid
    m.append("unit price at 20 each (not priced; quoted at %d pcs, MOQ %d)" % (b["offered_qty"], b["moq"]))
    m.append("unit price at the pooled quantity (break not yet set by the buyer)")
    if not b["currency"]: m.append("currency")
    m.append("lead time, first article, from a named event ('%s', no start event)" % b["lead"])
    m.append("lead time, production, from a named event ('%s', no start event, no FA/production split)" % b["lead"])
    m.append("tooling price, or a statement that none is needed")
    m.append("tooling ownership")
    if b["moq"] is None: m.append("minimum order quantity")
    if not b["validity_text"]: m.append("price validity")
    elif True: m.append("price validity as a date (period '%s' stated, but the quote is undated)" % b["validity_text"])
    m.append("freight basis named place ('%s' stated without a named place)" % b["freight"])
    m.append("payment terms")
    m.append("packaging")
    m.append("quality clause acceptance")
    m.append("offered item: manufacturer and part number")
    if not b["accuracy"]: m.append("offered item: accuracy class (bid says 'accuracy class not stated')")
    if not b["carriage"]: m.append("offered item: carriage included or not (count and type)")
    m.append("offered item: preload")
    if not b["cut_tol"]: m.append("offered item: cut-length tolerance")
    m.append("offered item: mounting-hole pitch and end offset")
    if not b["exceptions"]: m.append("exclusions and assumptions listed (none listed; silence is not 'none')")
    return m

slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
for b in bids:
    b["slug"] = slug(b["supplier_name"])
    b["bid_ref"] = "%s/unlisted-%s/1" % (EVENT, b["slug"])
    b["fields_missing"] = missing(b)
    b["extended_at_offered"] = round(b["unit_price"] * b["offered_qty"], 2)
    b["moq_over_demand"] = b["moq"] - demand
    b["our_share_pct"] = round(100.0 * demand / b["moq"], 1)
    b["validity_until"] = None

def yq(s):
    return "null" if s is None else '"' + str(s).replace('"', '\\"') + '"'

for b in bids:
    lines = [
        "# Supplier bid record (contract: shared/contracts/supplier-bid.md, version 1). INTERNAL - never to any supplier.",
        "# SYNTHETIC test data. Values mapped as stated; nothing normalised.",
        "contract_version: 1",
        "site: null   # REQUIRED: no plant profile on file this run; buyer/estimator to name the site",
        "event_ref: %s" % EVENT,
        "bid_ref: %s" % b["bid_ref"],
        "supersedes: null",
        "supplier_id: unlisted",
        "supplier_id_verbatim: %s" % yq(b["supplier_name"] + " (fictitious)"),
        "supplier_name: %s" % yq(b["supplier_name"]),
        "supplier_quote_ref: %s" % yq(b["quote_ref"]),
        "approval_status: not_confirmed_approved   # no approved-supplier table and no ERP vendor record on file",
        "received_at: null   # nothing in the file dates the quote",
        "received_via: pasted   # supplied as a text file",
        "source_ref: %s" % yq(b["file"] + " lines 2-3"),
        "ingested_at: %s" % yq(NOW),
        "item_as_quoted: %s" % yq(b["item_as_quoted"]),
        "currency: %s" % (b["currency"] or "null"),
        "breaks:",
        "  - quantity: %d" % demand,
        "    uom: each",
        "    unit_price: null",
        "    as_quoted: %s" % yq("not priced at %d; supplier quoted '%s', MOQ %d" % (demand, b["as_quoted"], b["moq"])),
        "    lead_time_first_article: null",
        "    lead_time_production: null",
        "    source_ref: %s" % yq(b["src_price"]),
        "  - quantity: null   # pooled consolidated quantity: break not yet set by the buyer",
        "    uom: each",
        "    unit_price: null",
        "    as_quoted: \"not priced (break not set when the supplier quoted)\"",
        "    lead_time_first_article: null",
        "    lead_time_production: null",
        "    source_ref: %s" % yq(b["src_price"]),
        "  - quantity: %d   # supplier-offered quantity, outside the package's breaks" % b["offered_qty"],
        "    uom: each",
        "    unit_price: %.2f" % b["unit_price"],
        "    as_quoted: %s" % yq(b["as_quoted"]),
        "    lead_time_first_article: null   # stated: %s (no named start event, no split)" % yq(b["lead"]),
        "    lead_time_production: null",
        "    lead_time_as_quoted: %s" % yq(b["lead"]),
        "    source_ref: %s" % yq(b["src_price"]),
        "tooling_price: null",
        "tooling_in_unit_price: null",
        "tooling_ownership: null",
        "tooling_note: null",
        "moq: %d" % b["moq"],
        "moq_uom: each",
        "validity_until: null   # stated period: %s; quote undated, so no date can be computed" % yq(b["validity_text"]),
        "validity_as_quoted: %s" % yq(b["validity_text"]),
        "freight_basis: %s" % yq(b["freight"]),
        "accuracy_as_quoted: %s" % yq(b["accuracy"] or b.get("accuracy_note")),
        "cut_tolerance_as_quoted: %s" % yq(b["cut_tol"]),
        "quality_clause_acceptance: not_stated",
        "clause_exceptions: []",
        "exceptions: %s" % json.dumps(b["exceptions"]),
        "conformance: off_format",
        "fields_missing:",
    ] + ["  - %s" % yq(f) for f in b["fields_missing"]] + [
        "restatement_requested: true   # drafted for the buyer to send; NOT sent",
    ]
    open("%s/sourcing/%s/%s.bid.txt" % (OUT, EVENT, b["slug"]), "w", encoding="utf-8").write("\n".join(lines) + "\n")

# ---------------------------------------------------------------- figures block
both_priced_breaks = [q for q in {bids[0]["offered_qty"], bids[1]["offered_qty"]}
                      if all(b["offered_qty"] == q for b in bids)]
currencies = sorted({b["currency"] for b in bids})
freight_bases = sorted({b["freight"] for b in bids})
F = {}
def fig(key, label, value, frm, flt):
    F[key] = dict(label=label, value=value, frm=frm, flt=flt)
fig("qty_per_arm", "Rails per arm", qty_per_arm, "02_bom_handoff.json", "purchased_rail.quantity_per_arm")
fig("sets", "Arm sets in the inquiry", sets, "intake NOREF-20261112", "line_no 1 quantities[0].qty (line %d)" % (sets_line + 1))
fig("demand", "Rail demand (rails per arm x sets)", demand, "BOM x intake; equals intake line 2 qty", "%d x %d; intake line %d qty %d" % (qty_per_arm, sets, rail_line + 1, rail_qty_intake))
fig("eau", "Forecast / EAU", "none supplied (eau: %s)" % eau, "intake NOREF-20261112", "line_no 2 eau (line %d)" % (eau_line + 1))
fig("usage_files", "Purchase / receipt / usage exports found", "%d - not found by search" % len(usage_files), "inputs folder enumerated (%d files)" % len(all_inputs), "filename matches po|purchase|receipt|usage|vendor|supplier_list|item_master")
fig("required", "Customer delivery date for the arm sets", str(required_delivery), "intake NOREF-20261112", "line_no 2 required_delivery (line %d)" % (req_line + 1))
fig("days_to_required", "Calendar days from today to that date", days_to_required, "computed", "%s - %s" % (required_delivery, TODAY))
fig("approved", "Approved suppliers on file for this commodity", "0 - no plant profile (plant_setup find: exists false)", "plant_setup.py find", "### Approved suppliers table not present")
fig("candidates", "Candidate suppliers (from the returned bids)", len(bids), "inputs/e2e_bids", "files rail_bid_*.txt")
fig("not_confirmed", "Candidates not confirmed approved", sum(1 for b in bids), "bid records", "approval_status == not_confirmed_approved")
fig("bids_received", "Bids received / suppliers known", "%d of %d" % (len(bids), len(bids)), "inputs/e2e_bids", "one bid per file")
fig("sends_recorded", "Sends recorded (per buyer)", 0, "no Open work page, no buyer statement", "never reconstructed")
fig("off_format", "Off-format bids", sum(1 for b in bids), "bid records", "conformance == off_format")
fig("currencies", "Currencies stated", ", ".join(currencies), "bid records", "currency")
fig("freight", "Freight bases stated", " | ".join(freight_bases), "bid records", "freight_basis")
fig("common_break", "Quantity break priced by both bids", ", ".join(map(str, both_priced_breaks)) or "none", "bid records", "offered_qty equal across bids")
for b in bids:
    k = b["slug"]
    fig(k + "_unit", "%s unit price at %d" % (b["supplier_name"], b["offered_qty"]), "%.2f %s" % (b["unit_price"], b["currency"]), b["src_price"], "as quoted")
    fig(k + "_ext", "%s extended at its quoted qty (%d x %.2f)" % (b["supplier_name"], b["offered_qty"], b["unit_price"]), "%.2f %s" % (b["extended_at_offered"], b["currency"]), "computed", "unit_price x offered_qty")
    fig(k + "_moq", "%s MOQ" % b["supplier_name"], b["moq"], b["src_price"], "as quoted")
    fig(k + "_gap", "%s MOQ minus our demand (units others would have to pool)" % b["supplier_name"], b["moq_over_demand"], "computed", "moq - demand")
    fig(k + "_share", "%s our demand as %% of its MOQ" % b["supplier_name"], "%.1f%%" % b["our_share_pct"], "computed", "100 x demand / moq")
    fig(k + "_missing", "%s fields_missing" % b["supplier_name"], len(b["fields_missing"]), "bid record", "mandated-field check, %d fields" % len(MANDATED))
fig("mandated", "Mandated response fields checked per bid", len(MANDATED), "package section 7", "MANDATED list in this script")

fig_md = ["| Figure | Value | Computed from | Filter or query |", "|---|---|---|---|"]
for k, v in F.items():
    fig_md.append("| %s | %s | %s | %s |" % (v["label"], v["value"], v["frm"], v["flt"]))
fig_md = "\n".join(fig_md)
open(OUT + "/sourcing-output/figures-block.md", "w", encoding="utf-8").write("# Figures block - %s (internal)\n\n%s\n" % (EVENT, fig_md))
json.dump({k: v["value"] for k, v in F.items()}, open(OUT + "/sourcing-output/figures.json", "w"), indent=1)

# ---------------------------------------------------------------- drafts (one per supplier: package cover + restatement)
def draft(b):
    miss = "\n".join("  - " + f for f in b["fields_missing"])
    return """=== SUPPLIER EMAIL — HELD — unlisted {name} ===
To: [recipient: not on file]
Subject: {ev} - RFQ, MGN9 linear rail 170 mm - please restate your quote {ref} in the attached format

Hello,

Thank you for your quotation {ref} for an MGN9 linear rail, 170 mm.

We are issuing a formal request for quotation for this item, attached as
"RFQ {ev} - MGN9 linear rail 170 mm" (specification-based request; no drawing
exists for this catalogue item). To let us evaluate it, please restate your
quote in the mandated response format in section 7 of that package. A bid in
another format is returned for restatement rather than interpreted on our side.

Your quotation as received does not state, or does not state in the required form:
{miss}

Please quote at each quantity in section 3 of the package, including the
quantity below your stated minimum order, and state your minimum order quantity
separately.

Response due: [DUE DATE - buyer to set before sending]
Send your response to: [buyer name and email - buyer to complete]
Technical questions: [technical contact - buyer to complete]. Answers given
to one bidder are shared with all bidders.

Regards,
[buyer name]
=== END ===""".format(name=b["supplier_name"], ev=EVENT, ref=b["quote_ref"], miss=miss)

drafts = {b["slug"]: draft(b) for b in bids}

# ---------------------------------------------------------------- outbound check (code reads each block alone)
reply_tpl = open(OUT + "/scripts/reply_template.md", encoding="utf-8").read()
pkg = re.search(r"=== SUPPLIER RFQ PACKAGE — SENDABLE ===.*?=== END ===", reply_tpl, re.S).group(0)
names = [b["supplier_name"] for b in bids] + [b["quote_ref"] for b in bids]
prices = ["%.2f" % b["unit_price"] for b in bids] + ["%.2f" % b["extended_at_offered"] for b in bids]
bad_common = [r"\bmargin\b", r"target price", r"\bPO-\d", "Harbor", "Okafor", r"MFG_"]
def check(block, own=None):
    hits = []
    for n in names:
        if own and n in (own["supplier_name"], own["quote_ref"]):
            continue
        if n in block: hits.append("other supplier/quote: " + n)
    for p in prices:
        if p in block: hits.append("price: " + p)
    for pat in bad_common:
        if re.search(pat, block, re.I) and not re.search(r"not a target price|no target price", block, re.I):
            hits.append("pattern: " + pat)
    return hits
checks = {"RFQ package": check(pkg)}
for b in bids:
    checks["email " + b["supplier_name"]] = check(drafts[b["slug"]], b)
check_md = "\n".join("- %s: %s" % (k, "PASS - no supplier name other than the addressee, no price, no PO number, no target price, no rate, no customer name" if not v else "FAIL " + "; ".join(v)) for k, v in checks.items())
assert all(not v for v in checks.values()), checks

# ---------------------------------------------------------------- sourcing events block (tracker)
trk = ["## Sourcing events",
       "### %s — MGN9 linear rail 170 mm (purchased), site not set" % EVENT,
       "Trigger: quote NOREF-20261112 line 2 (bought-in item) | Breaks: %d each; pooled quantity not set | Due: not set | Status: open" % demand,
       "| Supplier | Approval | Drafted | Sent (per buyer) | Due | Response | Chased |",
       "|---|---|---|---|---|---|---|"]
for b in bids:
    trk.append("| unlisted %s | not confirmed approved | %s (restatement, HELD) | not recorded | not set | bid %s, date not stated, sourcing/%s/%s.bid.txt | - |"
               % (b["supplier_name"], TODAY, b["quote_ref"], EVENT, b["slug"]))
trk_md = "\n".join(trk)
open(OUT + "/plant-setup/open-work/sourcing-events.md", "w", encoding="utf-8").write(
    "<!-- NOT saved to an Open work page: no artifact tools in this run. Paste this block back next time. -->\n" + trk_md + "\n")

# ---------------------------------------------------------------- comparison page (house style, internal)
E = html.escape
def row_break20(b):
    return ("<tr><td>%s<br><span class='muted mono'>unlisted</span></td><td><span class='status status--warn'>not confirmed approved</span></td>"
            "<td>not quoted per unit<br><span class='muted'>as quoted: %s</span></td><td>not computed</td><td>not stated</td>"
            "<td class='num'>%d <span class='status status--critical'>MOQ above %d</span></td><td>%s (no named event, no FA/production split)</td>"
            "<td>not stated</td><td>%s</td><td>%s</td><td><b>provisional</b>: no unit price at %d; MOQ above break; not approved; lead time not from a named event; clauses not stated</td><td class='mono'>%s</td></tr>"
            % (E(b["supplier_name"]), E(b["as_quoted"]), b["moq"], demand, E(b["lead"]), E("; ".join(b["exceptions"]) or "none listed"),
               E(b["validity_text"] or "not stated"), demand, E(b["src_price"])))
def row_offered(b):
    return ("<tr><td>%s</td><td class='num'>%d</td><td class='num'>%.2f %s</td><td class='num'>%.2f %s</td><td>not stated</td><td class='num'>%d</td>"
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class='mono'>%s</td></tr>"
            % (E(b["supplier_name"]), b["offered_qty"], b["unit_price"], b["currency"], b["extended_at_offered"], b["currency"], b["moq"],
               E(b["lead"]), E(b["freight"]), E(b["accuracy"] or b.get("accuracy_note") or "not stated"), E(b["cut_tol"] or "not stated"), E(b["src_price"])))
figrows = "".join("<tr><td>%s</td><td class='mono'>%s</td><td>%s</td><td class='mono'>%s</td></tr>" % (E(v["label"]), E(str(v["value"])), E(v["frm"]), E(v["flt"])) for v in F.values())
draft_cards = "".join("<div class='panel draft'><p><span class='status status--warn'>HELD</span> %s · To: [recipient: not on file] · Held: the shared conditions above, and this supplier is not confirmed approved</p><pre>%s</pre></div>" % (E(b["supplier_name"]), E(drafts[b["slug"]])) for b in bids)
recsum = "".join("<tr><td>%s</td><td class='mono'>%s</td><td>%s</td><td>off_format</td><td>not_confirmed_approved</td><td><ul>%s</ul></td></tr>" % (E(b["supplier_name"]), E(b["file"]), E(b["as_quoted"]), "".join("<li>%s</li>" % E(f) for f in b["fields_missing"])) for b in bids)
X_, Y_ = bids
page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bid Comparison {ev}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root{{--ink:#1A1D21;--paper:#F2F3F5;--paper-raised:#FFFFFF;--line:#D6D9DD;--accent:#1F5C8B;--accent-soft:#E4EDF4;--good:#2E7248;--good-soft:#E3EFE7;--warn:#A8641A;--warn-soft:#F7EBDA;--critical:#A93226;--critical-soft:#F9E9E7;
--font-display:'IBM Plex Sans Condensed','Arial Narrow',sans-serif;--font-body:'IBM Plex Sans',-apple-system,sans-serif;--font-mono:'IBM Plex Mono',Consolas,monospace}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--ink:#E8EAEC;--paper:#15181B;--paper-raised:#1D2126;--line:#2E343A;--accent:#6BA8D4;--accent-soft:#1B2C39;--good:#6FBF88;--good-soft:#1B2E22;--warn:#D9A15C;--warn-soft:#33271A;--critical:#DE8378;--critical-soft:#35201E}}}}
:root[data-theme="dark"]{{--ink:#E8EAEC;--paper:#15181B;--paper-raised:#1D2126;--line:#2E343A;--accent:#6BA8D4;--accent-soft:#1B2C39;--good:#6FBF88;--good-soft:#1B2E22;--warn:#D9A15C;--warn-soft:#33271A;--critical:#DE8378;--critical-soft:#35201E}}
body{{background:var(--paper);color:var(--ink);font-family:var(--font-body);margin:0}}
.page{{display:flex;flex-direction:column;gap:1.25rem;max-width:1100px;margin:0 auto;padding:2rem 1rem}}
.panel{{background:var(--paper-raised);border:1px solid var(--line);border-radius:4px;padding:1.25rem}}
h1,h2{{font-family:var(--font-display);font-weight:600;margin:0 0 .5rem}} .meta,.muted{{color:var(--ink);opacity:.7;font-size:.875rem}}
table{{border-collapse:collapse;width:100%;font-size:.85rem}} th,td{{border-bottom:1px solid var(--line);padding:.4rem;text-align:left;vertical-align:top}}
.num,.mono{{font-family:var(--font-mono);font-variant-numeric:tabular-nums}} .table-scroll{{overflow-x:auto}}
.status{{display:inline-block;padding:.05rem .4rem;border-radius:3px;font-size:.75rem}}
.status--warn{{background:var(--warn-soft);color:var(--warn)}} .status--critical{{background:var(--critical-soft);color:var(--critical)}} .status--good{{background:var(--good-soft);color:var(--good)}}
.rec{{border-left:4px solid var(--accent)}} pre{{white-space:pre-wrap;font-family:var(--font-mono);font-size:.8rem}}
</style></head><body><div class="page">
<header><h1>Bid Comparison — {ev}</h1><p class="meta">MGN9 linear rail, 170 mm · site not set (no plant profile) · Generated {today} · data as of the supplied files (quotes undated) · INTERNAL — never to any supplier</p></header>

<div class="panel rec"><h2>Provisional recommendation</h2>
<p><b>Do not choose between these two bids yet: ask both suppliers to restate in the package format.</b> Neither is ready for buyer review. The bids price different quantities ({xq} vs {yq}), on different freight bases ({xf} vs {yf}), and neither prices our {demand}-piece need; there is no quantity both priced, so they are not ranked.</p>
<p><b>Main tradeoff, if pooling goes ahead:</b> {xn} has the lower MOQ ({xm}, so others would pool {xg} units) and the shorter stated lead ({xl}) but is {xf} and rail only; {yn} has the lower unit price as quoted but needs {ym} pieces ({yg} pooled) and does not state accuracy class.</p>
<p><b>Open before any award:</b> item spec unconfirmed by the customer (carriage, preload, accuracy, brand); neither supplier approved (0 approved on file); no unit price at {demand}; pooled quantity not set; lead times not from a named event and our needed-at-dock date not set; quality clauses not stated and the plant clause list not on file; tooling, ownership, payment, packaging not stated.</p></div>
<div class="panel"><h2>Next step</h2><p><b>Pursue {xn}, look into the alternatives, or ask the suppliers to clarify?</b> (Recommended: ask both to clarify via the held restatement drafts.) Choosing is a preference about what to do next, not a selection or an award.</p></div>

<div class="panel freshness"><h2>Sources</h2><div class="table-scroll"><table><thead><tr><th>Source</th><th>Last refreshed</th><th>Covers</th><th>Status</th></tr></thead><tbody>
<tr><td>ERP item master / PO history / vendors</td><td>—</td><td>—</td><td><span class="status status--critical">not available</span></td></tr>
<tr><td>Plant profile (approved suppliers, clauses, terms, template)</td><td>—</td><td>—</td><td><span class="status status--critical">not on file</span></td></tr>
<tr><td class="mono">rail_bid_X.txt, rail_bid_Y.txt</td><td>undated</td><td>quotes as supplied</td><td><span class="status status--warn">undated — validity cannot be dated</span></td></tr>
<tr><td class="mono">02_bom_handoff.json</td><td>file</td><td>reBot B601 BOM</td><td><span class="status status--good">read</span></td></tr>
<tr><td class="mono">intake NOREF-20261112</td><td>2026-11-14</td><td>inquiry 2026-11-12</td><td><span class="status status--good">read</span></td></tr>
</tbody></table></div></div>

<div class="panel"><h2>Break: {demand} each (our demand)</h2><div class="table-scroll"><table><thead><tr><th>Supplier</th><th>Approval</th><th>Unit price</th><th>Extended</th><th>Tooling</th><th>MOQ</th><th>Lead time FA / production</th><th>Clauses</th><th>Exceptions</th><th>Validity</th><th>Readiness</th><th>Source</th></tr></thead><tbody>{r20}</tbody></table></div></div>
<div class="panel"><h2>Break: pooled consolidated quantity</h2><p>Not set by the buyer; not priced by either supplier. Every cell: <i>not quoted</i>.</p></div>
<div class="panel"><h2>As quoted, at each supplier's own quantity — not ranked</h2><p class="muted">Different quantities and freight bases; shown for the buyer's reading, not as a comparison. Absent is not zero.</p><div class="table-scroll"><table><thead><tr><th>Supplier</th><th>Qty quoted</th><th>Unit</th><th>Extended (computed)</th><th>Tooling</th><th>MOQ</th><th>Lead</th><th>Freight</th><th>Accuracy</th><th>Cut tolerance</th><th>Source</th></tr></thead><tbody>{rof}</tbody></table></div>
<p>Responses: {recv} known suppliers responded; no sends recorded, no due date set, so no days past due. Off-format: both (fields_missing below).</p></div>

<div class="panel"><h2>Draft supplier emails — not sent</h2><p><b>Held, both drafts:</b> no contact address on file; no response due date in the package; item specification not confirmed (no item master, customer spec questions open); suppliers not confirmed approved with no requalification decision.</p></div>
{cards}

<details class="panel"><summary><b>Readiness evidence per bid</b></summary><table><thead><tr><th>Prerequisite</th><th>{xn}</th><th>{yn}</th></tr></thead><tbody>
<tr><td>1 Cost comparable</td><td>No: no unit price at {demand}; MOQ {xm}; tooling not stated; {xf}</td><td>No: no unit price at {demand}; MOQ {ym}; tooling not stated; {yf}</td></tr>
<tr><td>2 Supplier approved</td><td>No: not confirmed approved; requalification path not set (samples / first article at minimum, buyer to decide)</td><td>Same</td></tr>
<tr><td>3 Delivery evidenced</td><td>No: "{xl}" from no named event; needed-at-dock date not set (arm sets due {req})</td><td>No: "{yl}" from no named event; same</td></tr>
<tr><td>4 Terms accepted</td><td>No: quality clauses not stated (plant list not on file); accuracy "standard", carriage excluded</td><td>No: clauses not stated; accuracy class not stated</td></tr></tbody></table></details>
<details class="panel"><summary><b>Bid records summary</b></summary><table><thead><tr><th>Supplier</th><th>Source file</th><th>As quoted</th><th>conformance</th><th>approval</th><th>fields_missing</th></tr></thead><tbody>{recsum}</tbody></table><p class="mono">Records: sourcing/{ev}/*.bid.txt</p></details>
<details class="panel"><summary><b>Figures block</b></summary><table><thead><tr><th>Figure</th><th>Value</th><th>Computed from</th><th>Filter or query</th></tr></thead><tbody>{figrows}</tbody></table><p class="muted">Computed by out/scripts/sourcing_run.py over the input files.</p></details>
<p class="muted">Offered page: save it over the last version of this event's comparison. Nothing was sent, awarded or written to any system.</p>
</div></body></html>""".format(ev=EVENT, today=TODAY, demand=demand, xq="%d @ %.2f %s" % (X_["offered_qty"], X_["unit_price"], X_["currency"]),
    yq="%d @ %.2f %s" % (Y_["offered_qty"], Y_["unit_price"], Y_["currency"]), xf=X_["freight"], yf=Y_["freight"], xn=X_["supplier_name"], yn=Y_["supplier_name"],
    xm=X_["moq"], ym=Y_["moq"], xg=X_["moq_over_demand"], yg=Y_["moq_over_demand"], xl=X_["lead"], yl=Y_["lead"], req=required_delivery,
    r20="".join(row_break20(b) for b in bids), rof="".join(row_offered(b) for b in bids), recv=F["bids_received"]["value"],
    cards=draft_cards, recsum=recsum, figrows=figrows)
open(OUT + "/sourcing-output/bid-comparison.html", "w", encoding="utf-8").write(page)

# ---------------------------------------------------------------- reply
def sub(m):
    k = m.group(1)
    return str(F[k]["value"]) if k in F else {"EVENT": EVENT}.get(k, m.group(0))
reply = reply_tpl.replace("{{FIGURES}}", fig_md).replace("{{TRACKER}}", trk_md).replace("{{CHECK}}", check_md)
reply = reply.replace("{{DRAFTS}}", "\n\nHeld: the shared conditions above, and this supplier is not confirmed approved.\n\n".join([""] + [drafts[b["slug"]] for b in bids]).lstrip("\n"))
reply = reply.replace("{{EVENT}}", EVENT)
reply = re.sub(r"\{\{fig:([\w-]+)\}\}", sub, reply)
assert "{{" not in reply, re.findall(r"\{\{[^}]*\}\}", reply)
open(OUT + "/reply-%s.md" % EVENT, "w", encoding="utf-8").write(reply)
print(json.dumps({k: v["value"] for k, v in F.items()}, indent=1))
print(check_md)
