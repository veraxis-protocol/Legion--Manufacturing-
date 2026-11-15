# quote-build — Northwind Robotics MB-2040 Rev C (DRAFT D2, not released)

*Full reply as the skill prints it. SYNTHETIC test data. Skill followed: `quote-build`, with its intake input built per `customer-inquiry-intake` (steps 1–6) because no intake form existed, and the rates recorded per `onboarding` step 10 ("update our labour rate") on the operator's yes. No Word or Excel copy this session: no Word or Excel writer is available (python-docx and openpyxl are not installed, and nothing was installed).*

## Revision history

| Rev | Date | What changed | Why |
|---|---|---|---|
| D1 | 2026-11-14 | Unpriced draft: material, anodize, hours and setup structure only. Labor, burden and margin were blocked | No rate on file (no `MFG_*` variable, no plant rates file) |
| D2 | 2026-11-14 | Priced at 250 / 500 / 1,000 on the confirmed plant rates. Customer block now carries prices; marking and FAI moved to "not included" | Rates recorded through onboarding step 10: confirmed, given by Test Estimator (LEGION WO-LMFG-004 test operator) on 2026-11-14, from the finance memo of 1 Oct 2026. Written to `plant-setup/plant-rates.md` |

Neither draft has been released (Gate 4 is open). Nothing was sent.

## Summary for the estimator

- **Priced (draft, budgetary, path A):** unit prices of $36.09, $35.20 and $34.98 at 250, 500 and 1,000 pcs. These are priced on the **27 blanks per plate** case. At 30 blanks per plate they would be $35.10, $34.22 and $34.00.
- **Rates:** labor and burden come from the plant rates file as a combined, fully burdened rate per work centre, and so do the margin rules. Cite: *plant profile, confirmed by Test Estimator (LEGION WO-LMFG-004 test operator) on 2026-11-14*. No `MFG_*` variable is set (checked by name).
- **How margin was applied — an interpretation to confirm.** Each uplift is applied to its own cost category, and none is stacked:
  - the material markup on material;
  - the outside-processing markup on anodize;
  - the default margin, as a fraction of price, on conversion (setup and run).

  Two other readings are shown on the internal sheet, and both are higher.
- **Path A: a budgetary estimate, never a firm quote.** The package is a Rev C text spec with no drawing. A firm quotation needs the released Rev C drawing, which goes back to `rfq-to-quote` step 7 as path C2.
- **Every hour is rung 4.** The hours come from the MB-1880 Rev B routing for a similar part, cross-checked against 2 closed MB-1880 work orders. No MB-2040 routing, actuals or geometry estimate exists.
- **Not in the price:** laser marking, AS9102 FAI, material certificates and tooling. The inputs hold no hours or cost for them, so they are listed as not included.
- **Delivery date not checked against shop load.** No planning export was supplied.
- **Proceeded on an unconfirmed recommendation.** `bid_decision_state` is `draft`, so Gate 2 has not been passed. This is recorded on the internal sheet.

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

**Missing register:**
- flatness value (a pending change);
- the drawing;
- marking location and lot-code format;
- monthly release quantities;
- first-article quantity and delivery point;
- whether the bore tolerance applies before or after anodize, and masking;
- payment, freight, packaging and liability;
- the response deadline;
- the site (no plant setup profile).

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
| 1a | MB-2040 Rev C | Motor bracket, 6061-T6 aluminium, black Type II anodize | 250 | 36.09 | 9,022.50 |
| 1b | MB-2040 Rev C | as above | 500 | 35.20 | 17,600.00 |
| 1c | MB-2040 Rev C | as above | 1,000 | 34.98 | 34,980.00 |

The quantity options are alternatives, each priced as a single production quantity.

**Lead time:** [to be confirmed]. First articles were requested by 15 January 2027; that date is not yet confirmed.
**Validity:** [to be set at release]. Material pricing is subject to change.
**Terms:** payment, freight, packaging and liability were not stated in your request. They are quoted on our standard terms [standard terms to be attached], and are listed below as assumptions.

**Scope included**
- Material: aluminium 6061-T6 plate per ASTM B209.
- Machining to the MB-2040 specification sheet, Revision C dated 27 October 2026.
- Finish: Type II sulfuric anodize, black, per MIL-A-8625.
- Edge break 0.2–0.5 mm on all edges.

**Not included in the prices above (quoted separately once details are confirmed)**
- Laser-etched part number and lot code (location and format to be advised by you).
- First article inspection report in AS9102 format on the first lot.
- Material certificate with each lot.
- Any special fixtures or tooling.

**Assumptions and exclusions**
1. This is a budgetary estimate based on the written specifications you provided, for planning only. It is not an offer; we will send a firm quotation on receipt of a released drawing.
2. Priced to MB-2040 Revision C (specification sheet dated 27 October 2026). Revision B drawings are not the basis of this estimate.
3. Tolerances as read: main bore Ø22.000 mm +0.021/−0.000 (H7), Ra 1.6 µm; all other features to ISO 2768-m per the general tolerance note, Ra 3.2 µm.
4. Flatness of the mounting face is excluded until you confirm the requirement. A confirmed value may change the price.
5. Whether the bore tolerance applies before or after anodize, and whether the bore is masked, is to be confirmed. The price assumes it will be agreed before order.
6. The delivery schedule after first articles (monthly quantities) is to be confirmed. Prices assume each quantity is produced as a single run; split deliveries may change the price.
7. Payment, freight and delivery point, packaging, and liability terms were not stated; our standard terms apply until agreed.
8. The annual volume of about 4,000 pcs was noted as not a commitment and is not reflected in these prices.
9. Prices are in US dollars, excluding tax, freight and packaging.

```
=== END ===
```

**Outbound document check (run in code on the block alone; result in `out/calc/outbound_check.json`):** pass. The check found:
- no hours, rung, path or basis label;
- no variance;
- no rate value (each confirmed rate figure was tested);
- no PO number or supplier name;
- no form of the margin word;
- no customer name other than the addressee's.

The block is a draft only: not released (Gate 4).

---

```
=== INTERNAL COST SHEET — NOT FOR CUSTOMER ===
```

**ROM — rough order of magnitude. Path A: text specs, no drawing. Not a firm quote and not releasable as one.**

**Status:** priced draft D2. Not released.

**Proceeded on an unconfirmed recommendation.** The intake's `bid_decision_state` is `draft` (a provisional bid). The instruction to proceed was the request in this run ("Build the quote"), repeated by the test operator ("complete the priced draft quote"). No Gate 2 approver's name was given, and none is inferred.

**Geometry estimate:** none. The design step did not run: there was no Fusion and the package is a text spec (path A). There is no rung 3.

**Capability:** not checked. No capability profile is on file. These items are flagged "capability unknown":
- H7 bore (0.021 mm band);
- Ra 1.6;
- the bore condition after anodize.

**Variance threshold:** 15% — default threshold, not plant-set.

#### Rates (value against source)

| Rate | Value used | Source |
|---|---|---|
| Labor + burden, MILL-V (combined, fully burdened) | 95.00 USD/h | plant profile, confirmed by Test Estimator (LEGION WO-LMFG-004 test operator) on 2026-11-14 (finance memo of 2026-10-01) |
| Labor + burden, INSP (combined, fully burdened) | 60.00 USD/h | same |
| Burden, separately | included in the combined rate; no split | same |
| Margin rules, default (fraction of price) | 0.18 | same |
| Material markup (recorded as said; outside the margin-rules JSON shape) | 12% | same |
| Outside-processing markup (recorded as said; outside the JSON shape) | 10% | same |
| Scrap costing basis | not set | The memo's rule was not part of the confirmation. The scrap allowance is costed through starts: every scrapped piece carries material and full run time on all ops, which is conservative against the memo's "to the work centre where scrapped" rule |

#### Cost buildup per quantity break (USD; priced case: 27 blanks per plate)

| Line | Source | 250 | 500 | 1,000 |
|---|---|---|---|---|
| Starts incl. scrap allowance (1.84%) | pooled MB-1880 scrap, WO-7702 + WO-7811 | 255 | 510 | 1,019 |
| **Material** — plates at $219.90, 27/plate (PRICED) | PO-30588, 2026-09-30, Metals Supply Co, AL6061-PL-0.5 0.5 x 12 x 48 in | 10 plates = 2,199.00 | 19 = 4,178.10 | 38 = 8,356.20 |
| Material, 30/plate (alternative, not priced) | same PO | 9 = 1,979.10 | 17 = 3,738.30 | 34 = 7,476.60 |
| **Outside processing** — anodize at $385.00/lot (≤300 pcs, ≤150 mm) | PO-30602, 2026-10-03, Bright Anodize LLC, OSP-ANOD-II-BLK | 1 lot = 385.00 | 2 = 770.00 | 4 = 1,540.00 |
| **Setup** — MILL-V 1.583 h × 95 + INSP 0.167 h × 60 | hours rung 4 x confirmed rates | 160.40 (0.6416/pc) | 160.40 (0.3208/pc) | 160.40 (0.1604/pc) |
| **Labor + machine/burden, run** — MILL-V run h × 95 + INSP run h × 60 | hours rung 4 x confirmed rates | 4,360.50 + 510.00 = 4,870.50 | 8,721.00 + 1,020.00 = 9,741.00 | 17,424.90 + 2,038.20 = 19,463.10 |
| Conversion subtotal (setup + run) | — | 5,030.90 | 9,901.40 | 19,623.50 |
| Tooling / fixtures | none identified in inputs | not included | not included | not included |
| Laser marking; AS9102 FAI; material certs | no op, no hours, no cost in inputs | not included (excluded on quote) | not included | not included |
| **Cost total** | sum | **7,614.90** (30.4596/pc) | **14,849.50** (29.6990/pc) | **29,519.70** (29.5197/pc) |
| Material markup 12% | margin rules (as said) | 263.88 | 501.37 | 1,002.74 |
| Outside-processing markup 10% | margin rules (as said) | 38.50 | 77.00 | 154.00 |
| Margin 0.18 of price, on conversion | margin rules default | 1,104.34 | 2,173.48 | 4,307.60 |
| **Margin line (total uplift)** | sum of the three above | **1,406.72** (15.59% of price) | **2,751.85** (15.63%) | **5,464.34** (15.62%) |
| Price (unrounded) | cost + margin line | 9,021.62 | 17,601.35 | 34,984.04 |
| **Unit price (rounded to cents)** | price ÷ qty | **36.09** | **35.20** | **34.98** |
| Extended at rounded unit price | unit × qty | 9,022.50 | 17,600.00 | 34,980.00 |
| *Alternative 1 — 30 blanks per plate* | same method | 35.10 | 34.22 | 34.00 |
| *Alternative 2 — markups, then 0.18 margin on the whole (stacked)* | (mat×1.12 + OSP×1.10 + conv) ÷ 0.82 | 38.62 | 37.63 | 37.41 |
| *Alternative 3 — 0.18 margin on whole cost, no markups* | cost ÷ 0.82 | 37.15 | 36.22 | 36.00 |

**Why the price curve is flat.** Setup is only 160.40 a run, so its per-piece contribution falls from 0.64 to 0.16. Material per piece also falls from 250 to 500, because the 10th plate at 250 is only partly used. Run time dominates at every break.

**Room to negotiate.** The margin line is 15.6% of price at every break. That is lower than the 18% default because the material and outside-processing markups are smaller than the default margin.

Material notes:
- **Nesting.** The 120 x 80 mm blank nests 30 per 12 x 48 in plate with zero cut allowance. That leaves 19.2 mm spare along the 48 in length, or 1.92 mm per blank. The kerf and facing allowance is unknown, per the operator. The 27-per-plate case is priced because 30 per plate holds only if the total allowance is ≤1.92 mm per blank. Both cases are shown.
- **Thickness.** Plate is 12.7 mm against a 12 mm finished part, leaving 0.7 mm of facing stock.
- **Price movement.** The plate price rose 3.53% between PO-30411 (2026-08-14, $212.40) and PO-30588 (2026-09-30, $219.90). The newer price is used, and the quote carries a validity caveat.
- **Anodize lots.** Lots are counted on the starts at each break, assuming a single run. Monthly releases under 300 pcs would each be a lot of their own.

#### Hours-basis table (per operation; all rung 4)

| Op | Work center | Rung / why not higher | Path | Cutting data | Setup min (low / exp / high) | Run min/pc (low / exp / high) | Other sources and variance vs basis | Drivers |
|---|---|---|---|---|---|---|---|---|
| 10 Saw and face blank | MILL-V | 4 — no MB-2040 routing (rung 1), no MB-2040 actuals (rung 2), no geometry estimate (rung 3) | Similar-part routing MB-1880 Rev B | n/a | 20 / 20 / 20 (no spread available) | 1.5 / 1.5 / 1.5 (no spread available) | none | — |
| 20 Mill profile, bore, holes (op 1) | MILL-V | 4 — as above | MB-1880 Rev B routing | n/a | 45 / 45 / 52 | 6.2 / 6.2 / 6.7 | WO-7702 (closed 2026-07-18, recorded): setup 52 **+15.6% FLAG**, run 6.70 +8.1%. WO-7811 (closed 2026-09-26, recorded): setup 47 +4.4%, run 6.48 +4.5% | Setup flag on WO-7702: driver not determinable from inputs (WO-7702 is the earlier of the 2 runs). MB-2040's features (H7 bore at Ra 1.6, 4x M5 tapped holes, 8 x 40 slot) are not shown for MB-1880 |
| 30 Op 2 flip and finish | MILL-V | 4 — as above | MB-1880 Rev B routing | n/a | 29 / 30 / 34 | 3.1 / 3.1 / 3.35 | WO-7702: setup 34 +13.3%, run 3.35 +8.1%. WO-7811: setup 29 −3.3%, run 3.18 +2.6% | Within threshold |
| 40 Deburr and inspect | INSP | 4 — as above | MB-1880 Rev B routing | n/a | 10 / 10 / 10 (no spread available) | 2.0 / 2.0 / 2.0 (no spread available) | none | AS9102 FAI not included |
| — Laser mark | — | no source | — | — | not estimated | not estimated | — | Not in the MB-1880 routing |
| — Anodize | outside | outside process, no machine time | PO-30602 | — | — | — | — | Lead time goes to the date check |

- The low and high bounds are the minimum and maximum of the MB-1880 routing and the recorded actuals. Actual run min/pc = `actual_run_min_total` ÷ `qty_completed`.
- No actuals are `probable_standard`: none agree with the routing to within 1%.
- No toolpath check: the CAM path did not run.
- **What would firm these hours up:** a current MB-2040 Rev C routing, or a confirmed geometry estimate from a released Rev C drawing (Gate 3).
- **Pricing on the high bound instead of the expected value** would raise op 20 and op 30 by up to 0.5 and 0.25 min/pc. That is not priced; it is shown as the spread.

#### Work content per break (setup + run, on starts; routing basis, rung 4)

| Break | MILL-V setup / run h | INSP setup / run h | Total h |
|---|---|---|---|
| 250 | 1.583 / 45.9 | 0.167 / 8.5 | 56.15 |
| 500 | 1.583 / 91.8 | 0.167 / 17.0 | 110.55 |
| 1,000 | 1.583 / 183.42 | 0.167 / 33.97 | 219.14 |

These assume one setup per break. Monthly releases would repeat the 1.75 h setup (160.40) for each release.

#### Comparables

| Comparable | What made it comparable | How MB-2040 differs |
|---|---|---|
| MB-1880 Rev B routing (labelled "current routing (similar bracket)") | A bracket the input labels similar; same work centres | A different part. Its geometry, material and finish are not in the inputs. MB-2040 adds an H7 bore at Ra 1.6, anodize, marking and FAI |
| WO-7702, MB-1880 Rev B, 300 + 6 scrapped, closed 2026-07-18 | Actual hours for ops 20 and 30 | About 4 months old; no cost recorded; ops 10 and 40 not recorded |
| WO-7811, MB-1880 Rev B, 500 + 9 scrapped, closed 2026-09-26 | As above | About 7 weeks old; no cost recorded |

No MB-2040 history (0 routing rows, 0 closed-job rows). No prior Northwind orders or quotes: no such file was supplied and no ERP was reached. That is absent, not zero.

The 1,000-pc break is 2x the largest MB-1880 run (500): an extrapolation, from a different part.

#### Date check (Step 7)

**Not checked against shop load.** No planning export was supplied. Work content by work centre is in the table above (rung 4, similar-part routing).

Lead times seen in the PO history:
- Plate, PO-to-receipt: 7 days on both PO-30411 and PO-30588.
- Anodize, PO-to-receipt: 12 days on PO-30602.

These are past intervals, not quoted supplier lead times. The requested first-article date, 15 Jan 2027, is 62 days from 2026-11-14. It cannot be confirmed or refused without the shop load, and the earliest achievable date cannot be given. Confirm with scheduling before release.

#### Figures block

Every number above is computed by code:
- Hours, material and lots: `out/calc/compute_mb2040.py` → `out/calc/figures_MB-2040.json`.
- Priced lines: `out/calc/price_mb2040.py` → `out/calc/pricing_MB-2040.json`, which reads the rates from `plant-setup/plant-rates.md`.

Key rows:

| Figure | Value | Filter / arithmetic |
|---|---|---|
| MB-2040 routing rows / closed-job rows | 0 / 0 | `part == "MB-2040"` |
| MB-1880 closed WOs | 2 (WO-7702, WO-7811), 2026-07-18 to 2026-09-26 | distinct work_order |
| Pooled scrap | 0.0184 | 15 / (800+15) |
| Setup per run | 105 min = 1.75 h; 160.40 USD | sum setup_min; × WC rates |
| Run per piece | 12.8 min/pc | sum run_min_per_unit |
| Starts 250/500/1,000 | 255 / 510 / 1,019 | ceil(q / (1−0.0184)) |
| Plates, 27/plate (priced) | 10 / 19 / 38 | ceil(starts/27) |
| Anodize lots | 1 / 2 / 4 | ceil(starts/300) |
| Cost totals | 7,614.90 / 14,849.50 / 29,519.70 | material + OSP + conversion |
| Margin line | 1,406.72 / 2,751.85 / 5,464.34 | markups + conv ÷ 0.82 − conv |
| Unit price | 36.09 / 35.20 / 34.98 | (cost + margin line) ÷ q, to cents |
| Op 20 WO-7702 setup variance | +15.6% FLAG | (52−45)/45 |
| Days to 15 Jan 2027 | 62 | date difference |

#### Operation record

Saved at `out/operation-record_MB-2040.json`. A counter re-derives from it and never reopens CAD.

#### Gaps (names only)

- Scrap costing basis: not set.
- Downtime cost per hour: not set.
- Material and outside-processing markups: recorded outside the margin-rules JSON shape.
- Margin application: not stacked vs stacked, to be confirmed.
- Plant setup profile: none. No site, no capability profile, no machining data, no quote template, no standard terms.
- No planning export.
- No quote history.
- No drawing.

```
=== END ===
```

---

## Notes to the estimator (outside both documents)

**Rates saved.** The labor (combined, fully burdened) rate and the margin rules are now confirmed in the plant rates file at `C:/LMFG/runs/B05-positive/work/plant-setup/plant-rates.md`, given by Test Estimator (LEGION WO-LMFG-004 test operator) on 2026-11-14. The private Plant rates page was not published: no artifact tools in this run, so the file lasts only as long as this folder.

**Questions this run would ask** (recorded rather than asked):
1. **Gate 2.** Do you confirm the bid, and who should be recorded as approving it?
2. **Margin.** Should the markups and the default margin apply per category (priced), stacked, or as margin only?
3. **Scrap costing.** Should the memo's scrap-costing rule be recorded as the plant's scrap costing basis?
4. **Gate 1.** When were the open questions sent to Dana Whitfield, and by whom?
5. **Path A.** Release as a budgetary estimate, or wait for the Rev C drawing and build a firm quote?
6. **Site and standard terms.** Which plant builds this, and what are its standard terms (onboarding has not run)?
7. **Gate 4.** Who releases the quote?

**Not done:**
- No Open work page or Plant rates page was published (no artifact tools).
- No Sales command-center page was produced, because it is written at quote release.
- No data-consolidate dataset was built: the CSVs were read directly.
