# quote-build — Northwind Robotics MB-2040 Rev C (DRAFT, not released)

*Full reply as the skill prints it. SYNTHETIC test data. Skill followed: `quote-build`, with its intake input built per `customer-inquiry-intake` (steps 1–6) because no intake form existed. No Word or Excel copy this session: no Word or Excel writer is available (python-docx and openpyxl are not installed, and nothing was installed).*

## Summary for the estimator

- **Priced so far:** material at the price paid on a named PO, the outside anodize at the price paid on a named PO, a scrap allowance from closed-job actuals, and setup/run hours per operation with setup re-amortized at 250, 500 and 1,000.
- **Blocked — no unit price and no job total at any break.** No labor rate, burden rate or margin rules are on file: no `MFG_LABOR_RATE`, `MFG_BURDEN_RATE` or `MFG_MARGIN_RULES` in the environment (checked by name) and no plant profile or rates file (`plant_setup.py find`: `exists: false`, `rates_exists: false`). The labor, machine/burden, setup-dollar and margin lines are blocked, and so are the price and total at every break.
- **The finance memo (`inputs/rates_memo.txt`, 1 Oct 2026) was not used.** It is not the plant's rates file and was not recorded through onboarding. A rate supplied inside a quote run is not used, and its figures are not repeated here. To price on it, use onboarding's *"update our labour rate"*. That records each rate on the plant's rates page with the name of the person who gave it and the date. Or set `MFG_LABOR_RATE` / `MFG_BURDEN_RATE` / `MFG_MARGIN_RULES` in the environment. The quote completes as soon as they are set.
- **Path A: this is a budgetary estimate, never a firm quote.** The package holds a Rev C text specification and no drawing. A firm quotation needs the released Rev C drawing, and that goes back to `rfq-to-quote` step 7 as path C2.
- **Every hour is rung 4.** No MB-2040 routing exists, no MB-2040 actuals exist, and no geometry estimate exists. The hours come from the MB-1880 Rev B routing for a similar part, cross-checked against 2 closed MB-1880 work orders.
- **Delivery date not checked against shop load.** No planning export was supplied.
- **Proceeded on an unconfirmed recommendation.** The intake's `bid_decision_state` is `draft`, and Gate 2 has not been passed. The request "build the quote" was taken as the instruction to proceed. This is recorded on the internal sheet.

### Intake form (summary; full record saved at `out/inquiries/northwind-robotics-MB-2040.intake.txt`)

| Field | Value | Source | reading_basis |
|---|---|---|---|
| customer / contact | Northwind Robotics / Dana Whitfield | spec header; rfq_email msg 1 | — |
| received_at | 2026-11-02T09:14:00-05:00 | rfq_email msg 1 Date | — |
| part_number / revision | MB-2040 / C | spec title; rfq_email msg 2 | — |
| quantities | 250, 500, 1,000 each (breaks, not averaged) | rfq_email msg 1 | — |
| material | Al 6061-T6 plate, ASTM B209 | spec row Material | — |
| main bore | Ø22.000 +0.021/−0.000 (H7), through, Ra 1.6 | spec rows Main bore, Surface finish | from_text |
| 4x M5x0.8 through, 100 x 60 pattern | ISO 2768-m (general tolerance) | spec rows Mounting holes, General tolerance | from_text |
| slot 8 x 40 through | ISO 2768-m per general note | spec rows Slot, General tolerance | from_text |
| flatness, mounting face | TBD (not stated) | spec row; rfq_email msg 2 | from_text |
| finish | Type II sulfuric anodize, black, MIL-A-8625 | spec row Finish | — |
| certifications_required | material cert each lot; AS9102 FAI first lot | rfq_email msg 1; spec row Inspection | — |
| required_delivery | first articles by 2027-01-15; monthly after | rfq_email msg 1 | — |
| eau | ~4,000 (not a commitment) | rfq_email msg 3 | — |
| geometry_path | **A** (text spec, no drawing) | source_documents | — |
| payment / freight / packaging / liability | null (missing register) | not stated | — |
| recommendation | bid, **provisional**, constraint-free (no capability profile) | — | — |
| bid_decision_state / line_bid_decision | draft / draft | — | — |
| inquiry_state | open | — | — |

**Ambiguous register:** revision. Rev C (the spec sheet, and Raj Patel's email of 29 Oct) against Rev B (drawings that procurement circulated, which the customer said to ignore). Quoted against **Rev C**. Rev B is named here as not the basis.

**Missing register:** flatness value (a pending change); the drawing; the marking location and lot-code format; monthly release quantities; the first-article quantity and delivery point; whether the bore tolerance applies before or after anodize, and masking; payment, freight, packaging and liability; the response deadline; the site (no plant profile).

### Open questions to the customer (Gate 1 — the estimator sends them; nothing was sent)

> Hi Dana,
>
> Thanks for the MB-2040 Rev C package. A few points so we can firm up our pricing for 250, 500 and 1,000 pcs:
>
> 1. Flatness of the mounting face is shown as TBD on the Rev C spec sheet, and Raj mentioned your design team will confirm it. What value should we quote to, and when do you expect to confirm it?
> 2. We have the Rev C specification sheet but no drawing. Can you send the released Rev C drawing (with datums and the M5 hole positions)? Until we have it, anything we send will be a budgetary figure rather than a firm quotation.
> 3. The 22 mm H7 bore (+0.021/-0.000, Ra 1.6) and the black Type II anodize: does the bore tolerance apply after anodize, and should the bore be masked?
> 4. Laser marking: where on the part should the part number and lot code go, and is there a required lot-code format?
> 5. Deliveries: how many first-article pieces do you need by 15 January 2027, and where should they be delivered? After that, what monthly quantities should we plan against for each of the 250 / 500 / 1,000 options?
> 6. Commercial terms: please let us know your payment terms, freight terms and delivery point, any packaging requirement for the anodized parts, and any liability terms that apply.
> 7. Is there a date you need our quotation by?
>
> Thanks,
> [estimator name]

---

```
=== CUSTOMER QUOTE — SENDABLE ===
```

**BUDGETARY ESTIMATE — DRAFT, NOT RELEASED**
*(Plant quote template not on file: neutral structure used.)*

To: Dana Whitfield, Northwind Robotics
Re: Motor bracket MB-2040, Revision C
Estimate ref: [to be assigned at release]   Date: [release date]

| Line | Part | Description | Quantity | Unit price (USD) | Extended (USD) |
|---|---|---|---|---|---|
| 1a | MB-2040 Rev C | Motor bracket, 6061-T6 aluminium, black Type II anodize | 250 | [pending] | [pending] |
| 1b | MB-2040 Rev C | as above | 500 | [pending] | [pending] |
| 1c | MB-2040 Rev C | as above | 1,000 | [pending] | [pending] |

**Lead time:** [to be confirmed]. First articles were requested by 15 January 2027; that date is not yet confirmed.
**Validity:** [to be set at release]. Material pricing is subject to change.
**Terms:** payment, freight, packaging and liability were not stated in your request. They will be quoted on our standard terms [standard terms to be attached], and are listed below as assumptions.

**Scope included**
- Material: aluminium 6061-T6 plate per ASTM B209, with a material certificate supplied with each lot.
- Machining to the MB-2040 specification sheet, Revision C dated 27 October 2026.
- Finish: Type II sulfuric anodize, black, per MIL-A-8625.
- Edge break 0.2–0.5 mm on all edges.
- Laser-etched part number and lot code (location to be advised by you).
- First article inspection report in AS9102 format on the first lot.

**Assumptions and exclusions**
1. This is a budgetary estimate based on the written specifications you provided, for planning only. It is not an offer; we will send a firm quotation on receipt of a released drawing.
2. Priced to MB-2040 Revision C (specification sheet dated 27 October 2026). Revision B drawings are not the basis of this estimate.
3. Tolerances as read: main bore Ø22.000 mm +0.021/−0.000 (H7), Ra 1.6 µm; all other features to ISO 2768-m per the general tolerance note, Ra 3.2 µm.
4. Flatness of the mounting face is excluded until you confirm the requirement. A confirmed value may change the price.
5. Whether the bore tolerance applies before or after anodize, and whether the bore is masked, is to be confirmed. The price assumes it will be agreed before order.
6. Delivery schedule after first articles (monthly quantities) to be confirmed. Prices assume each quantity is produced as a single run.
7. Payment, freight and delivery point, packaging, and liability terms were not stated; our standard terms apply until agreed.
8. The annual volume of about 4,000 pcs was noted as not a commitment and is not reflected in these prices.

```
=== END ===
```

**Outbound document check (run in code on the block alone; result in `out/calc/outbound_check.json`):** pass. The block holds no hours, rung, path, basis label, variance, rate, PO number, supplier name, or any form of the margin word. Its only customer name is the addressee's. It cannot be released anyway: no prices.

---

```
=== INTERNAL COST SHEET — NOT FOR CUSTOMER ===
```

**ROM — rough order of magnitude. Path A: text specs, no drawing. Not a firm quote and not releasable as one.**

**Status:** dollar lines for labor, machine/burden, setup and margin are **BLOCKED (rate not on file)**. No unit price and no job total is produced at any break.
**Proceeded on an unconfirmed recommendation.** The intake's `bid_decision_state` is `draft` and its recommendation is a provisional bid. The instruction to proceed was the request in this run ("Build the quote"). The approver's name was not given; it is asked below, not inferred.
**Geometry estimate:** none. The design step did not run: this was a quote-build run with no Fusion, and the package is a text spec (path A). There is no rung 3.
**Capability:** not checked. No plant capability profile is on file, so the H7 bore (0.021 mm band), Ra 1.6 and anodized-bore condition could not be checked against demonstrated capability. Each is listed here by name, value and "capability unknown".
**Variance threshold:** 15% — default threshold, not plant-set.

#### Rates (source of each)

| Rate | Source | State | Lines it blocks |
|---|---|---|---|
| Labor rate | `MFG_LABOR_RATE` not set; no plant rates file | not set | Labor, Setup $ (all ops, all breaks), unit price, totals |
| Burden / machine rate | `MFG_BURDEN_RATE` not set; no plant rates file | not set | Machine & burden, Setup $, unit price, totals |
| Margin rules | `MFG_MARGIN_RULES` not set; no plant rates file | not set | Margin line, unit price, totals |
| Scrap costing basis | `MFG_SCRAP_COSTING_BASIS` not set; no plant rates file | not set | Scrap valued at material only (below); labor in scrapped pieces is unvalued |

The finance memo `inputs/rates_memo.txt` (dated 1 Oct 2026) holds commercial figures: work-centre shop rates, markups, a margin target and a scrap-costing rule. It was not used, because it is not the plant's rates file. Record it through onboarding's "update our labour rate" (who gave it, and the date) or through the `MFG_*` variables. Note for that step: the memo states its rates as fully burdened, so onboarding should record how labor and burden map onto them.

#### Cost buildup per quantity break (USD)

| Line | Source | 250 | 500 | 1,000 |
|---|---|---|---|---|
| Starts incl. scrap allowance (1.84%) | pooled MB-1880 scrap, WO-7702 + WO-7811 | 255 | 510 | 1,019 |
| **Material** — plates at $219.90 | PO-30588, 2026-09-30, Metals Supply Co, AL6061-PL-0.5, 0.5 x 12 x 48 in | 9 plates = $1,979.10 ($7.9164/pc) | 17 = $3,738.30 ($7.4766/pc) | 34 = $7,476.60 ($7.4766/pc) |
| Material, if a cut allowance >1.92 mm/blank (27 per plate) | same PO | 10 = $2,199.00 ($8.7960/pc) | 19 = $4,178.10 ($8.3562/pc) | 38 = $8,356.20 ($8.3562/pc) |
| **Outside processing** — anodize lots at $385.00/lot (≤300 pcs, ≤150 mm) | PO-30602, 2026-10-03, Bright Anodize LLC, OSP-ANOD-II-BLK | 1 lot = $385.00 ($1.5400/pc) | 2 = $770.00 ($1.5400/pc) | 4 = $1,540.00 ($1.5400/pc) |
| **Labor** (setup + run hours below × labor rate) | hours rung 4; rate | BLOCKED | BLOCKED | BLOCKED |
| **Machine & burden** (same hours × burden rate) | hours rung 4; rate | BLOCKED | BLOCKED | BLOCKED |
| **Setup** — 105 min per run (1.75 h), per-piece contribution | MB-1880 routing ops 10–40 | 0.42 min/pc; $ BLOCKED | 0.21 min/pc; $ BLOCKED | 0.105 min/pc; $ BLOCKED |
| **Tooling / fixtures** | none identified in inputs | not sourced | not sourced | not sourced |
| Laser marking; AS9102 FAI; material certs | no op, no hours, no price in inputs | NOT COSTED | NOT COSTED | NOT COSTED |
| **Margin** (its own line) | margin rules | BLOCKED | BLOCKED | BLOCKED |
| **Unit price / job total** | — | not produced | not produced | not produced |

Material notes:
- **Nesting.** The 120 x 80 mm blank fits 30 per 12 x 48 in plate with zero cut allowance. That count leaves 19.2 mm spare along the 48 in length for 10 blanks, or 1.92 mm per blank. The plant's saw-kerf and facing allowance is not in the inputs. If it is above 1.92 mm per blank, the plate yields 27, and the second material row applies. The estimator should confirm which.
- **Thickness.** Plate is 12.7 mm against a 12 mm finished part, leaving 0.7 mm of facing stock.
- **Price movement.** The plate price rose 3.53% between PO-30411 (2026-08-14, $212.40) and PO-30588 (2026-09-30, $219.90). The newer price is used, and the material price needs a validity caveat.
- **Anodize lots.** Lots are counted on the starts at each break, assuming a single run. Monthly releases could add lots: each release under 300 pcs is a lot of its own. That is a missing-register item.

#### Hours-basis table (per operation; all rung 4)

| Op | Work center | Rung / why not higher | Path | Cutting data | Setup min (low / exp / high) | Run min/pc (low / exp / high) | Other sources and variance vs basis | Drivers |
|---|---|---|---|---|---|---|---|---|
| 10 Saw and face blank | MILL-V | 4 — no MB-2040 routing (rung 1), no MB-2040 actuals (rung 2), no geometry estimate (rung 3) | Similar-part routing MB-1880 Rev B | n/a | 20 / 20 / 20 (no spread available) | 1.5 / 1.5 / 1.5 (no spread available) | none | — |
| 20 Mill profile, bore, holes (op 1) | MILL-V | 4 — as above | MB-1880 Rev B routing | n/a | 45 / 45 / 52 | 6.2 / 6.2 / 6.7 | WO-7702 (closed 2026-07-18, recorded): setup 52 **+15.6% FLAG**, run 6.70 +8.1%. WO-7811 (closed 2026-09-26, recorded): setup 47 +4.4%, run 6.48 +4.5% | Setup flag on WO-7702: the driver cannot be determined from the inputs (WO-7702 is the earlier of the 2 runs). Feature content differs: MB-2040 has an H7 bore at Ra 1.6, 4x M5 tapped holes in the Rev C position and an 8 x 40 slot, and the inputs do not show MB-1880's features |
| 30 Op 2 flip and finish | MILL-V | 4 — as above | MB-1880 Rev B routing | n/a | 29 / 30 / 34 | 3.1 / 3.1 / 3.35 | WO-7702: setup 34 +13.3%, run 3.35 +8.1%. WO-7811: setup 29 −3.3%, run 3.18 +2.6% | Within threshold |
| 40 Deburr and inspect | INSP | 4 — as above | MB-1880 Rev B routing | n/a | 10 / 10 / 10 (no spread available) | 2.0 / 2.0 / 2.0 (no spread available) | none | AS9102 FAI content is not included |
| — Laser mark | — | no source | — | — | not estimated | not estimated | — | Not in the MB-1880 routing |
| — Anodize | outside | outside process, no machine time | PO-30602 | — | — | — | — | Lead time goes to the date check |

- The low/high bounds are the minimum and maximum of the MB-1880 routing and the recorded MB-1880 actuals. Actual run min/pc = `actual_run_min_total` ÷ `qty_completed`.
- No actuals are `probable_standard`: none agree with the routing to within 1%.
- No toolpath check: the CAM path did not run, and no Fusion was used.
- **What would firm these hours up:** a current MB-2040 Rev C routing, or a confirmed geometry estimate built from a released Rev C drawing (Gate 3).

#### Work content per break (setup + run, on starts; routing basis, rung 4)

| Break | MILL-V setup / run h | INSP setup / run h | Total h |
|---|---|---|---|
| 250 | 1.583 / 45.9 | 0.167 / 8.5 | 56.15 |
| 500 | 1.583 / 91.8 | 0.167 / 17.0 | 110.55 |
| 1,000 | 1.583 / 183.42 | 0.167 / 33.97 | 219.14 |

These assume one setup per break (a single run). Monthly releases would repeat the 1.75 h setup for each release.

#### Comparables

| Comparable | What made it comparable | How MB-2040 differs |
|---|---|---|
| MB-1880 Rev B routing (inputs/cost/routings.csv, labelled "current routing (similar bracket)") | A bracket the input labels similar; same work centres (MILL-V, INSP) | A different part. Its geometry, material and finish are not in the inputs. MB-2040 adds an H7 bore at Ra 1.6, black Type II anodize, laser marking and AS9102 FAI, and none of these is visible in the MB-1880 ops |
| WO-7702, MB-1880 Rev B, 300 pcs + 6 scrapped, closed 2026-07-18 | Same similar part; actual hours for ops 20 and 30 | About 4 months old; no cost recorded; ops 10 and 40 not recorded |
| WO-7811, MB-1880 Rev B, 500 pcs + 9 scrapped, closed 2026-09-26 | As above | About 7 weeks old; no cost recorded |

No MB-2040 history: 0 routing rows and 0 closed-job rows. No prior Northwind orders or quotes: no quote-history or sales-order file was supplied, and no ERP was reached. That is absent, not zero.

**Quantity range:** 1,000 is 2x the largest MB-1880 run (500). This is a modest extrapolation, and the scrap and run figures come from a different part.

#### Date check (Step 7)

**Not checked against shop load.** No planning export was supplied. The work content the job adds is in the table above: MILL-V and INSP hours, rung 4 (similar-part routing).

Lead times seen in the PO history:
- Plate, PO-to-receipt: 7 days on both PO-30411 and PO-30588.
- Anodize, PO-to-receipt: 12 days on PO-30602, one lot.

Those are order-to-receipt intervals on past POs, not quoted supplier lead times. The requested first-article date, 15 Jan 2027, is 62 days from today (2026-11-14). It cannot be confirmed or refused without the shop load, and the earliest achievable date cannot be given. Confirm with scheduling before release.

#### Figures block

Every number above comes from `out/calc/compute_mb2040.py`. The full block, with its filter or arithmetic for each figure, is in `out/calc/figures_MB-2040.json`. Key rows:

| Figure | Value | Filter / arithmetic |
|---|---|---|
| MB-2040 routing rows / closed-job rows | 0 / 0 | `part == "MB-2040"` |
| MB-1880 closed WOs | 2 (WO-7702, WO-7811), 2026-07-18 to 2026-09-26 | distinct work_order |
| Pooled scrap | 0.0184 | 15 / (800+15) |
| Setup per run | 105 min = 1.75 h | sum setup_min ops 10–40 |
| Run per piece | 12.8 min/pc | sum run_min_per_unit ops 10–40 |
| Starts 250/500/1,000 | 255 / 510 / 1,019 | ceil(q / (1−0.0184)) |
| Plates (30/plate) | 9 / 17 / 34 | ceil(starts/30) |
| Anodize lots | 1 / 2 / 4 | ceil(starts/300) |
| Plate price change | +3.53% | (219.9−212.4)/212.4 |
| Op 20 WO-7702 setup variance | +15.6% FLAG | (52−45)/45 |
| Days to 15 Jan 2027 | 62 | 2027-01-15 − 2026-11-14 |

#### Operation record

Saved at `out/operation-record_MB-2040.json`. It holds part, revision priced to, op_seq, work center, rung, path, setup and run (low, expected, high), quantity breaks, sources, geometry estimate state (none) and date derived. A counter re-derives from that record.

#### Gaps (names only)

- Labor rate: not set.
- Burden rate: not set.
- Margin rules: not set.
- Scrap costing basis: not set.
- Plant profile: none. That means no site, no capability profile, no machining data (machine classes, cutting data, variance threshold), no quote template and no standard commercial terms.
- No planning export.
- No quote history.
- No drawing.

```
=== END ===
```

---

## Notes to the estimator (outside both documents)

**Questions this run would ask** (recorded rather than asked, per the run rules):

1. **Gate 2.** Do you confirm the bid recommendation for MB-2040 (currently a provisional `bid`, `draft`)? Who should I record as approving it?
2. **Rates.** Should the finance memo of 1 Oct 2026 be recorded as the plant's rates through onboarding's "update our labour rate"? If yes:
   - Who gave the figures, and on what date?
   - How should its fully burdened work-centre rates map to labor and burden?
   - Should its markups and margin target become the margin rules?
3. **Gate 1.** Will you send the open questions above to Dana Whitfield? When were they sent, and by whom?
4. **Path A.** Do you want this released as a budgetary estimate once priced, or held until the Rev C drawing arrives so a firm quote can be built (back to `rfq-to-quote` step 7, path C2)?
5. **Nesting.** What is the saw-kerf and facing allowance per blank? It decides 30 or 27 blanks per plate.
6. **Site and standard terms.** Which plant builds this, and what are its standard payment, freight, packaging and liability terms? Onboarding has not run.
7. **Gate 4.** Who releases the quote? Nothing goes to the customer without the estimator's release.

**Not done:**
- No Open work page was saved (no artifact tools in this run). The intake record is saved only in `out/inquiries/`.
- No Sales command-center page was produced, because it is written at quote release and this quote is not released.
- No data-consolidate dataset was built: the routing, actuals and PO CSVs were read directly.
