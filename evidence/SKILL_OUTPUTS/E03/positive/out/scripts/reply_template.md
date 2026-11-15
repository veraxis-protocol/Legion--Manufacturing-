# supplier-quote-request — reply for {{EVENT}}

*The skill's reply, as it would be printed in the conversation. SYNTHETIC test data. Nothing was sent to any supplier, nothing was awarded, nothing was written to any system.*

**Skill followed:** `skills/supplier-quote-request` (steps 1–13). Trigger: a quote — inquiry NOREF-20261112 line 2, a bought-in item ("if you can source it"). Not a supplier-caused flag, so the flag gate does not apply.

## Hard stops and gates (read first)

- **Revision check: not applicable as a drawing check, and unverified.** The MGN9-170 mm rail is a catalogue part with no drawing, so this is a **specification-based request** (skill edge case *No drawing exists*). There is no ERP item master this run, so nothing can confirm the item specification. The specification itself is incomplete: carriage count and type, preload, accuracy grade and brand/equivalents are open questions to the customer (intake question Q5, not yet sent — intake is paused at Gate 1), and the BOM handoff lists "manufacturer tolerance for the purchased MGN9-170 rail" as missing. **The package is drafted but must not be released until the buyer confirms the item specification.**
- **Restricted data: none found.** No ITAR, EAR, export-control marking or distribution statement in any input; the design source is an open-hardware project (CERN-OHL-W-2.0 per the BOM handoff). No plant profile exists to say whether the customer program is controlled; *not assessed against a profile*.
- **Plant setup:** `plant_setup.py find` returned no profile, no rates and no Open work page (`exists: false`), and no artifact tools are used this run. So: no approved-supplier table, no standard quality clause list, no commercial terms, no RFQ template, no site.
- **Pooling with other buyers:** the package quotes our demand of {{fig:demand}} as ours and asks for a separate price at a pooled quantity that is labelled contingent. It is never presented as our forecast (the skill's *never inflate a forecast* rule). Other buyers are not named in anything that goes to a supplier.

## The supplier RFQ package

Neutral structure: the plant's controlled RFQ template is not on file (flag kept here, outside the package). No Word copy this session: no Word writer available (python-docx not installed; nothing was installed).

=== SUPPLIER RFQ PACKAGE — SENDABLE ===
REQUEST FOR QUOTATION — {{EVENT}}
Miniature linear guide rail, size MGN9, length 170 mm (purchased catalogue component)

Issued by: [BUYER TO COMPLETE: company, buyer name]
Request type: specification-based request. No drawing exists for this catalogue item.

1. SCOPE
Supply of MGN9 miniature linear guide rails cut to 170 mm, one rail per assembly.

2. TECHNICAL REQUIREMENT
Stated requirement: rail size MGN9; rail length 170 mm; one rail per assembly.
[BUYER TO COMPLETE BEFORE RELEASE — not yet confirmed by our customer:
 carriage — rail only, or rail with carriage(s), with count and type;
 preload; accuracy grade; specified brand, or equivalents accepted;
 length tolerance, if any.]
Your bid must identify the item you are offering: manufacturer and part number,
accuracy class, preload, whether carriages are included (count and type), rail
material, cut-length tolerance, mounting-hole pitch and end offset.

3. QUANTITIES AND DEMAND
Historical usage: none. This is a new requirement; we hold no purchase or
receipt history for this item.
Open demand: {{fig:demand}} pieces for a single build of {{fig:sets}} assemblies, one rail per
assembly. This requirement is pending our customer's order.
Forecast: no annual volume has been established; no repeat demand is stated.
Possible consolidated quantity: we may combine this requirement with other
purchasers' identical requirements into one order. Please also quote at
[POOLED QUANTITY — buyer to set once confirmed]. This quantity is contingent and
is not a commitment.
Quote each quantity above separately. State your minimum order quantity
separately; if it exceeds a quantity above, quote that quantity anyway or say
plainly that you will not supply it.

4. DELIVERY REQUIREMENTS
Required at our dock by: [DATE — buyer to set]
Ship-to: [ADDRESS — buyer to complete]
First article / sample: [buyer to state whether a sample is required before the order]

5. QUALITY REQUIREMENTS
[BUYER TO INSERT the plant's standard supplier quality clause list at its
current revision.] State acceptance of each clause, or your exception to it in
your own words. Silence on a clause is treated as not accepted.

6. COMMERCIAL BASIS — all bids must assume these terms
Incoterm and named place: [buyer to set]
Payment terms: [buyer to set]
Packaging: [buyer to set]

7. MANDATED RESPONSE FORMAT
Reply with one line per quantity in section 3, and each item below:
 a. Unit price at each quantity, separately (not a lot price, not a blended rate)
 b. Currency, stated explicitly
 c. Tooling or NRE, priced separately, or a statement that none is needed
 d. Tooling ownership
 e. Lead time for first article / sample, from receipt of order
 f. Lead time for production quantity, from receipt of order
 g. Minimum order quantity
 h. Price validity, as a date
 i. Confirmation that the price is on the section 6 basis
 j. Acceptance of, or exception to, each section 5 clause
 k. The offered item identification required in section 2
 l. Every exclusion or assumption, listed — not implied
A bid in a different format is returned for restatement rather than
interpreted on our side.

8. RESPONSE SCHEDULE
Response due: [DATE — buyer to set]
Send your bid to: [buyer name and email]
Technical questions: [technical contact]. Answers given to one bidder are
shared with all bidders.
=== END ===

**Outbound check (run in code on each delimited block alone):**
{{CHECK}}

## Missing items (internal)

| What is missing | Why it matters | Where it should have come from |
|---|---|---|
| Item specification: carriage (rail only vs with carriage, count, type), preload, accuracy grade, brand or equivalents | Price and lead time depend on all of them; the two returned bids already differ here (one rail only at standard accuracy, one silent on accuracy and carriage) | Customer (intake Q5, not yet sent); the project BOM gives only "MGN9-170mm" (`02_bom_handoff.json` purchased_rail.model) |
| Manufacturer tolerance for the rail | Listed as missing by engineering | `02_bom_handoff.json` engineering_missing |
| ERP item master / revision for the rail | Revision check cannot clear; no part number exists (intake line 2 part_number: null) | ERP item master — not available this run |
| Purchase / receipt / usage history | No current price paid to compare against; usage stated as none | ERP PO history — {{fig:usage_files}} in the inputs folder |
| Needed-at-dock date and first article requirement | Lead time cannot be judged; only the customer's arm-set date {{fig:required}} is known | Planning data / buyer |
| Pooled quantity, and the pooling partners' spec | Pooling only works for an identical item; the break cannot be priced until set | Buyer |
| Response due date, send-to address, technical contact | Every draft is held without them | Buyer |
| Plant standard quality clause list | Section 5 is a placeholder; the set is flagged unverified, no plausible list was assembled | `## Plant context` from onboarding — not on file |
| Commercial terms (Incoterm, payment, packaging, liability, tooling ownership standard) | The two bids came back FOB origin and DDP — not on one basis | `## Plant context` — not on file |
| Approved supplier table / vendor records | No supplier can be shown approved | `### Approved suppliers` / ERP vendors — not on file |
| Plant RFQ template | Package uses a neutral structure | onboarding — not on file |
| Site | Required on bid records; left null | plant profile — not on file |

## Candidate suppliers (internal)

**No approved supplier on file for this commodity ({{fig:approved}}).** That is the finding, ahead of the package: any award here needs a requalification decision first.

| Supplier | ID | Approval status | Basis | Requalification |
|---|---|---|---|---|
| Xylem Linear Motion (fictitious) | unlisted | **not confirmed approved** | Named only by its returned bid `rail_bid_X.txt`; no approved table, no vendor record | Buyer to decide (catalogue part: at minimum incoming check of a sample / first lot against the confirmed spec) |
| Yarrow Motion Parts (fictitious) | unlisted | **not confirmed approved** | Named only by its returned bid `rail_bid_Y.txt`; same | Same |

No incumbent: no purchase history for this item.

## Supplier emails — drafts, not sent

Because both suppliers have already quoted, each supplier gets **one** email that carries the package and asks for the restatement.

**Held, both drafts:** no contact address on file; no response due date in the package; item specification not confirmed; suppliers not confirmed approved with no requalification decision. I have not sent anything — the buyer sends each from their own mailbox.

{{DRAFTS}}

## Bid records (saved, summarised)

| bid_ref | Source file | As quoted | approval | conformance | fields_missing |
|---|---|---|---|---|---|
| {{EVENT}}/unlisted-xylem-linear-motion/1 | inputs/e2e_bids/rail_bid_X.txt | {{fig:xylem-linear-motion_unit}} at 100 pcs, MOQ {{fig:xylem-linear-motion_moq}}, 3 weeks, FOB origin, rail only, valid 21 days | not_confirmed_approved | off_format | {{fig:xylem-linear-motion_missing}} fields — see record |
| {{EVENT}}/unlisted-yarrow-motion-parts/1 | inputs/e2e_bids/rail_bid_Y.txt | {{fig:yarrow-motion-parts_unit}} each, minimum order {{fig:yarrow-motion-parts_moq}}, 5 weeks, DDP, cut tol ±0.5 mm | not_confirmed_approved | off_format | {{fig:yarrow-motion-parts_missing}} fields — see record |

Full records: `out/sourcing/{{EVENT}}/xylem-linear-motion.bid.txt`, `out/sourcing/{{EVENT}}/yarrow-motion-parts.bid.txt`. Neither quote is dated, so `received_at` and `validity_until` are null (Xylem's "valid 21 days" kept as stated). Ambiguity for the restatement: Xylem names "MGN9H" yet says "rail only (no carriage)"; the restatement asks for the offered part number.

## Comparison and recommendation

Comparison page (internal, house style): `out/sourcing-output/bid-comparison.html`.

**Provisional recommendation: do not choose yet — ask both suppliers to restate in the package format.** No quantity was priced by both bids ({{fig:common_break}}), neither prices our {{fig:demand}} pieces, and the freight bases differ ({{fig:freight}}), so they are not ranked. Both are provisional: no unit price at {{fig:demand}}, MOQ above the break, not approved, lead time not from a named event, clauses not stated.

**Tradeoff if pooling goes ahead:** Xylem's MOQ of {{fig:xylem-linear-motion_moq}} needs {{fig:xylem-linear-motion_gap}} pooled units (our share {{fig:xylem-linear-motion_share}}) with a 3-week stated lead, FOB origin and rail only; Yarrow's {{fig:yarrow-motion-parts_unit}} is lower as quoted but needs {{fig:yarrow-motion-parts_gap}} pooled units (our share {{fig:yarrow-motion-parts_share}}) and states no accuracy class. Extended at each supplier's own quantity: Xylem {{fig:xylem-linear-motion_ext}}, Yarrow {{fig:yarrow-motion-parts_ext}} — different quantities, not comparable.

**Next step: pursue Xylem Linear Motion, look into the alternatives, or ask the suppliers to clarify?** Choosing is a preference about the next step, not a selection. No selection record was written; none will be until the buyer names a supplier and gives a name to record it under.

## Response tracker

Not saved to your Open work page: no artifact tools in this run. Paste this table back next time and I'll pick up from it. (Copy at `out/plant-setup/open-work/sourcing-events.md`.)

{{TRACKER}}

Bids in hand: {{fig:bids_received}}. Sends recorded: {{fig:sends_recorded}} — I have not reconstructed a send history; which suppliers were sent what, and when?

## Figures block (internal)

{{FIGURES}}

## Supply Chain command-center page

Offered, not published: the sourcing signal (no approved source for the rail, two off-format bids, package held on spec) and the package are on the comparison page above; save it where the last Supply Chain page lives. The dashboard was not updated: Supply Chain is an offered page, and no artifact tools are used this run.

## Questions recorded for the buyer (not asked live)

1. Confirm the rail specification (carriage, preload, accuracy, brand/equivalent) — or should intake question Q5 go to the customer first?
2. The pooled quantity, the pooling partners, and confirmation their item is identical; who is buyer of record and how delivery is split. (Joint purchasing with other companies may need a competition-law check by your own advisers.)
3. Response due date, send-to address, technical contact, needed-at-dock date, ship-to, sample requirement.
4. Incoterm, payment and packaging terms; the plant quality clause list.
5. Requalification path for these two unlisted suppliers.
6. Which suppliers were sent what, and when (none recorded)?
7. Which site, and the name to record on any later decision.
