=== INTERNAL COST SHEET — NOT FOR CUSTOMER ===

**ROM — rough order of magnitude. Path A: text specs, no drawing. Not a firm quote and can't be released as one.** The RFQ package is a specification sheet (MB-2040_spec_revC.md) with no drawing, so the bore, slot and hole positions aren't fully defined. A firm quote needs the released Rev C drawing, sent back through rfq-to-quote step 7 (path C2).

# MB-2040 Rev C motor bracket — Northwind Robotics — internal cost basis

**Status: DRAFT for estimator review. Not released (Gate 4 not passed).**
Prepared 2026-11-15. All figures computed by `out/calc/mb2040_calc.py` from `./inputs`; raw output in `out/calc/mb2040_calc_output.json`.

**Sheet-wide labels**
- **Rates: finance memo rate — not on the plant rates page.** No plant profile or rates page exists in this session and `MFG_LABOR_RATE`, `MFG_BURDEN_RATE`, `MFG_MARGIN_RULES` are all unset (checked by name). Every rate below comes from `inputs/rates_memo.txt` (finance memo, 1 Oct 2026), which you directed me to use. It has not been recorded through onboarding with a name and date. Use "update our labour rate" to record it so later quotes don't depend on this file.
- **Every machining hour is rung 4 (first principles, from a similar part).** There is no MB-2040 routing, no MB-2040 closed job and no geometry estimate.
- **No controlled quote template is on file**, so I used a neutral structure.

---

## 1. Rates used

| Rate | Value | Source | Lines it feeds |
|---|---|---|---|
| MILL-V fully burdened | 95.00 USD/h | rates_memo.txt line 2 | Ops 10, 20, 30 setup and run |
| INSP fully burdened | 60.00 USD/h | rates_memo.txt line 2 | Op 40 setup and run |
| Material markup | 12% | rates_memo.txt line 3 | Material |
| Outside processing markup | 10% | rates_memo.txt line 3 | Anodize |
| Target margin | 18% | rates_memo.txt line 3 | Margin line |
| Scrap costing rule | standard material + value-added labour at the scrapping work centre | rates_memo.txt line 4 | Scrap allowance (see §4) |
| Laser marking | **none on file** | — | **Laser marking line is blocked** |

The memo's "fully burdened shop rate" is one combined labor + burden rate per work centre, so I don't show labor and machine/burden as separate lines.

**I read "target margin 18%" as margin on sell price**: price = cost ÷ (1 − 0.18). The memo also lists the material and OSP markups separately, so I applied those first and then took margin on the whole subtotal. Please confirm this is what finance means. If margin is meant to apply only to conversion, the unit prices are 36.86 / 35.96 / 35.73 (sensitivity, §6).

---

## 2. Inputs and what was missing

| Item | Status | Source |
|---|---|---|
| Part, revision | MB-2040 Rev C. Spec sheet dated 2026-10-27 | MB-2040_spec_revC.md lines 2, 4 |
| Quantities | 250 / 500 / 1,000 | rfq_email.txt line 10 |
| Material | Al 6061-T6 plate, ASTM B209 | spec line 8 |
| Finish | Type II sulfuric anodize, black, MIL-A-8625 | spec line 15. The anodize request is repeated in rfq_email.txt line 11 |
| Material cert | Required with each lot | rfq_email.txt line 11 |
| FAI | AS9102 on first lot | spec line 19 |
| First article date | 15 Jan 2027, then monthly production deliveries | rfq_email.txt line 10 |
| Annual volume | about 4,000/yr, "not a commitment" | rfq_email.txt line 29. **Not priced** |
| **Flatness, mounting face** | **TBD by customer** | spec line 17, rfq_email.txt line 22 |
| **Marking location** | **"per customer", not given** | spec line 18 |
| Rev B drawings | Customer says to ignore them (M5 pattern moved 2 mm outboard in Rev C) | rfq_email.txt line 21 |
| Payment, freight, packaging, liability, currency | **Not stated in the RFQ.** No plant standard is on file either | — |
| Delivery split | "Monthly after" first articles. Batch sizes not stated | rfq_email.txt line 10 |
| Intake form | Not produced (customer-inquiry-intake did not run). I built a minimal intake from the RFQ files above, with every field cited | — |
| Planning export / shop load | **Not available** | — |
| Plant capability profile | **Not available** | — |

---

## 3. Capability flags (raised before pricing)

1. **Main bore Ø22.000 +0.021/−0.000 mm (H7), Ra 1.6 µm** (spec line 10). This is a 21 µm tolerance band. There is no plant capability profile on file, so the plant has **no demonstrated capability on record** for this tolerance. It is also unknown whether MB-1880 has a comparable bore. The quote assumes the bore is finished on MILL-V within the borrowed op 20/30 times. If it needs a separate finish-bore or ream op, run time goes up (not priced).
2. **Flatness of the mounting face is TBD** (spec line 17). Priced with no flatness callout beyond ISO 2768-m general tolerance. A tight flatness callout could add a skim pass or a stress-relief step, or rule out 0.5 in plate as stock (see §4: only 0.7 mm is available to face).
3. **4× M5×0.8 tapped through** (spec line 11). The MB-1880 op 20 description is "bore and holes", and it doesn't say whether those holes are tapped. If MB-1880 holes are not tapped, the borrowed times leave out tapping.

---

## 4. Material

| Item | Value | Source / arithmetic |
|---|---|---|
| Stock | 6061-T6 plate 0.5 in × 12 in × 48 in, item AL6061-PL-0.5 | purchase_orders.csv |
| Price used | **219.90 USD/plate, PO-30588, dated 2026-09-30, received 2026-10-07**, Metals Supply Co | purchase_orders.csv row 2 (most recent) |
| Prior price | 212.40 USD/plate, PO-30411, 2026-08-14 | purchase_orders.csv row 1. **+3.53% in 6 weeks**, so I added a validity caveat |
| Thickness | 0.5 in = 12.7 mm, against 12 mm finished. **Only 0.7 mm total to face** | spec line 9. Confirm this is enough for op 10 face and any flatness callout. If not, buy thicker stock (no PO history for that) |
| Blanks per plate | **27** (28 at 0 mm allowance, 27 at 5 mm and 10 mm) | Calculated: 80+a × 120+a mm blanks nested in 304.8 × 1,219.2 mm with a 3 mm kerf, best orientation. **Kerf and allowance are my assumptions. Please confirm** |
| Scrap allowance | **1.84%** (15 / 815 pieces) | closed_jobs.csv: WO-7702 6/306 = 1.96%, WO-7811 9/509 = 1.77% (MB-1880) |
| Starts = ⌈qty ÷ (1 − 0.0184)⌉ | 255 / 510 / 1,019 | — |
| Plates = ⌈starts ÷ 27⌉, charged as whole plates | 10 / 19 / 38 | Drop is charged to the job. Conservative |
| Material cost | 2,199.00 / 4,178.10 / 8,356.20 | plates × 219.90 |
| + 12% markup | 263.88 / 501.37 / 1,002.74 | memo |
| **Material to price** | **2,462.88 / 4,679.47 / 9,358.94** | — |

Scrap costing: the memo calls for standard material plus value-added labour at the work centre where the part was scrapped. **There is no standard cost (no ERP)**, so I used the PO price instead. The MB-1880 actuals don't record which op the scrap came from. I therefore charged all four ops on every start, which costs each scrapped piece as if it was scrapped after inspection. That is the conservative case. Anodize is charged on good pieces only.

Material certs: I assumed the mill cert ships with the plate at no extra charge. The PO doesn't say. **Please confirm.**

---

## 5. Hours basis — per operation (all rung 4)

**Why every op is rung 4.** Rung 1 needs an MB-2040 Rev C routing, and routings.csv has 0 rows for MB-2040. Rung 2 needs MB-2040 actuals, and closed_jobs.csv has 0 MB-2040 work orders. Rung 3 needs a confirmed geometry estimate, and none exists because the design step (rfq-to-quote step 7) did not run. What I used is the **routing and actuals of a similar part, MB-1880 Rev B** (4 routing rows; 2 closed work orders, WO-7702 and WO-7811, closed 2026-07-18 and 2026-09-26). The ladder treats a similar part's data as first principles.

**What would firm it up:** a confirmed geometry estimate for MB-2040 Rev C, or the MB-1880 drawing so I can compare features (bore tolerance, tapped holes, slot, envelope) line by line.

Per-piece run times from actuals = actual_run_min_total ÷ (qty_completed + qty_scrapped). I divided by **pieces started**, because the scrapped pieces were also machined. Dividing by good pieces only gives op 20: 6.70 / 6.48 and op 30: 3.35 / 3.18 min/pc.

| Op | WC | Description (MB-1880 routing) | Setup min low / **exp** / high | Run min/pc low / **exp** / high | Expected basis | Cross-check variance vs MB-1880 routing (setup, run) | Flag (threshold 15%, default, not set by the plant) |
|---|---|---|---|---|---|---|---|
| 10 | MILL-V | Saw and face blank | 20 / **20** / 20 | 1.5 / **1.5** / 1.5 | MB-1880 routing. No actuals, so no spread available | — | — |
| 20 | MILL-V | Mill profile, bore and holes, op 1 | 45 / **49.5** / 52 | 6.200 / **6.467** / 6.569 | Median of WO-7702, WO-7811 | WO-7702 **+15.6%**, +5.9%. WO-7811 +4.4%, +2.7% | **WO-7702 setup is above threshold** |
| 30 | MILL-V | Op 2 flip and finish | 29 / **31.5** / 34 | 3.100 / **3.204** / 3.284 | Median of WO-7702, WO-7811 | WO-7702 +13.3%, +5.9%. WO-7811 −3.3%, +0.8% | — |
| 40 | INSP | Deburr and inspect | 10 / **10** / 10 | 2.0 / **2.0** / 2.0 | MB-1880 routing. No actuals | — | — |

The low and high bounds are the min and max of (MB-1880 routing, MB-1880 actuals). They are not a percentage band.

- **probable_standard check:** no actual falls within 1% of its routing standard, so none are flagged. Closest is op 30 run on WO-7811 at +0.8%, but its setup differs by −3.3%. Both are recorded actuals.
- **Op 20 setup variance on WO-7702 (+15.6%), drivers:** the data can't tell. WO-7702 was the earlier of the two jobs (July against September), and the later job came in at +4.4%. That fits a first-run prove-out, but that is inference, not data.
- **Variance drivers for MB-2040 against MB-1880 (not quantifiable without a geometry estimate):** the H7 bore with Ra 1.6; the tapped M5×4; the 8 × 40 mm through slot; edge break 0.2–0.5 mm on all edges (could add deburr time to op 40); the envelope, since the MB-1880 envelope is unknown.
- **Not covered by any op:** laser marking (§7) and the AS9102 FAI report (§7).
- Toolpath check: not run (no CAM path).

Expected work content by work centre:

| | 250 | 500 | 1,000 |
|---|---|---|---|
| MILL-V setup h | 1.68 | 1.68 | 1.68 |
| MILL-V run h | 47.48 | 94.95 | 189.72 |
| INSP setup h | 0.17 | 0.17 | 0.17 |
| INSP run h | 8.50 | 17.00 | 33.97 |

**Extrapolation flag:** MB-1880 has only run at 300 and 500 pieces. The 1,000 break uses the same rates per piece, with no learning curve applied, so it is extrapolated from experience at 500 or fewer.

---

## 6. Cost buildup and quantity breaks (expected case, USD)

| Line | 250 | 500 | 1,000 | Source |
|---|---|---|---|---|
| Material incl. 1.84% scrap starts, whole plates | 2,199.00 | 4,178.10 | 8,356.20 | PO-30588 @ 219.90, §4 |
| Material markup 12% | 263.88 | 501.37 | 1,002.74 | memo |
| Anodize (lots of ≤300 pcs) | 385.00 (1 lot) | 770.00 (2 lots) | 1,540.00 (4 lots) | **PO-30602, 2026-10-03, Bright Anodize LLC, 385.00/lot (up to 300 pcs ≤150 mm)**. Part is 120 mm, so it fits |
| OSP markup 10% | 38.50 | 77.00 | 154.00 | memo |
| Setup (ops 10–40, once per run) | 169.92 | 169.92 | 169.92 | §5 × 95 / 60 USD/h |
| Run (ops 10–40 × starts) | 5,020.32 | 10,040.64 | 20,061.59 | §5 × 95 / 60 USD/h |
| **Cost subtotal** | **8,076.62** | **15,737.03** | **31,284.45** | — |
| **Margin (18% of price)** | **1,772.92** | **3,454.47** | **6,867.32** | memo. Price = subtotal ÷ 0.82 |
| **Price** | **9,849.53** | **19,191.50** | **38,151.77** | — |
| **Unit price** | **39.40** | **38.38** | **38.15** | — |
| Laser marking | BLOCKED | BLOCKED | BLOCKED | §7 |
| AS9102 FAI (one-time) | BLOCKED | — | — | §7 |

Per-unit build, to explain the price curve:

| per pc | 250 | 500 | 1,000 |
|---|---|---|---|
| Material incl. markup | 9.85 | 9.36 | 9.36 |
| Anodize incl. markup | 1.69 | 1.69 | 1.69 |
| **Setup contribution** | **0.68** | **0.34** | **0.17** |
| Run | 20.08 | 20.08 | 20.06 |
| Margin | 7.09 | 6.91 | 6.87 |
| **Unit price** | **39.40** | **38.38** | **38.15** |

**Why the price is nearly flat across breaks:** setup is only 101 MILL-V minutes plus 10 INSP minutes per run, so amortizing it moves the unit price by just 0.51 between 250 and 1,000. Run time (about 20/pc) dominates. Material per piece also drops a little at 500 because the plate drop is smaller. If the customer pushes on volume pricing, the room is in run time and margin, not setup.

**Range (low / high hours case, same rates):** 250: 38.61 – 39.79. 500: 37.63 – 38.76. 1,000: 37.41 – 38.52. The range only covers the spread inside MB-1880 data. It does **not** cover the MB-2040 feature differences in §5, which is the bigger uncertainty.

**Sensitivity:**
- **Margin applied to conversion only** (material and OSP at their markups only): unit price 36.86 / 35.96 / 35.73.
- **Setup assumption:** I assumed one setup per quantity, run as a single batch. If "monthly deliveries" means separate monthly runs, each extra run adds 169.92 setup cost before margin (207.22 at price). That is +0.83/pc at 250 per extra run. There may also be extra anodize lots, because a lot is charged at 385.00 regardless of how many parts are in it.
- **FA lot run separately**, held for approval before production: one extra setup as above.

---

## 7. Blocked lines

| Line | Why blocked | What unblocks it |
|---|---|---|
| Laser marking (part no. + lot code) | No laser work centre in the routings, no rate for it in the finance memo, no OSP PO for it, and the customer hasn't given a location (spec line 18) | Plant confirms how marking is done (in-house laser WC with a rate, or an outside vendor quote). Customer gives the location |
| AS9102 FAI report, first lot | No hours source anywhere in the inputs. The INSP rate exists (60 USD/h), but I won't invent an hours figure | Estimator enters the FAI hours (balloon count and CMM time), or provides a prior FAI job's hours |

**The totals in §6 leave both out.** This is an incomplete quote and must not be released until both lines are priced or explicitly excluded by agreement with the customer.

---

## 8. Comparables

| Comparable | Why comparable | How MB-2040 differs |
|---|---|---|
| MB-1880 Rev B, routing (4 ops) | Similar motor bracket, same 4-op MILL-V/INSP route, presumably the same 0.5 in 6061 plate ("saw and face blank") | Different part. Features and envelope unknown to me; MB-2040 has an H7 bore, tapped M5 ×4, a slot, edge break and laser marking. **Whether MB-1880 is anodized is not recorded** |
| WO-7702 (300 good, 6 scrap, closed 2026-07-18) | Same as above, actual times | ~4 months old. Smaller than 2 of the 3 breaks |
| WO-7811 (500 good, 9 scrap, closed 2026-09-26) | Same as above, actual times | ~7 weeks old. 1,000 is twice its size |

There is **no prior MB-2040 job, no prior Northwind quote, and no prior sell price** in the inputs. Without an ERP or document store I can't say whether Northwind is a new customer, so I haven't assumed it is.

---

## 9. Date check

- **Not checked against shop load.** There is no planning export.
- Lead-time elements from the data: plate 7 calendar days (PO-30411: ordered 08-14, received 08-21; PO-30588: ordered 09-30, received 10-07). Anodize 12 calendar days (PO-30602: ordered 10-03, received 10-15).
- Machining content for the 250 run: 49.2 MILL-V hours + 8.7 INSP hours, plus FAI time (unpriced). I can't convert hours to days without a shift pattern.
- Requested first articles: 15 Jan 2027, which is 61 days from today (2026-11-15). On work content alone (7 + 12 calendar days plus about 49 machine hours) it **looks reachable if the order is placed by early December, but that has not been checked against committed load.** I haven't put a committed date in the customer draft.

---

## 10. Figures block

| Figure | Value | Filter / arithmetic |
|---|---|---|
| MB-2040 routing rows | 0 | routings.csv part == MB-2040 |
| MB-1880 Rev B routing rows | 4 | routings.csv part == MB-1880 |
| MB-2040 closed WOs | 0 | closed_jobs.csv part == MB-2040 |
| MB-1880 closed WOs | 2 (WO-7702, WO-7811) | distinct work_order, part == MB-1880 |
| Actuals date range | 2026-07-18 – 2026-09-26 | min/max closed_date |
| Plate POs | 2 | item == AL6061-PL-0.5 |
| Plate price change | +3.53% | (219.90 − 212.40) / 212.40 |
| Scrap rate | 1.84% | 15 / (800 + 15) |
| Blanks per plate | 27 | nesting calc, §4 |
| Variance op 20 setup WO-7702 | +15.56% | (52 − 45) / 45 |
| Variance op 20 setup WO-7811 | +4.44% | (47 − 45) / 45 |
| Variance op 20 run WO-7702 / WO-7811 | +5.95% / +2.67% | (2010/306 − 6.2)/6.2; (3240/509 − 6.2)/6.2 |
| Variance op 30 setup WO-7702 / WO-7811 | +13.33% / −3.33% | (34−30)/30; (29−30)/30 |
| Variance op 30 run WO-7702 / WO-7811 | +5.95% / +0.77% | (1005/306 − 3.1)/3.1; (1590/509 − 3.1)/3.1 |
| Starts | 255 / 510 / 1,019 | ⌈q / (1 − 0.018405)⌉ |
| Plates | 10 / 19 / 38 | ⌈starts / 27⌉ |
| Anodize lots | 1 / 2 / 4 | ⌈q / 300⌉ |
| Unit price exp / low / high | see §6 | (subtotal / 0.82) / q |

---

## 11. Operation record (kept for counters and for actual-vs-estimate comparison)

Part MB-2040, priced to **Rev C (spec dated 2026-10-27)**, derived 2026-11-15, priced at quantity breaks 250 / 500 / 1,000. No geometry estimate (no `document_ref`, no approval state).

| op_seq | WC | Machine class | Rung | Path | Cutting data basis | Setup min L/E/H | Run min/pc L/E/H | Sources |
|---|---|---|---|---|---|---|---|---|
| 10 | MILL-V | not on file | 4 | similar-part routing | n/a | 20/20/20 | 1.5/1.5/1.5 | routings.csv MB-1880 op 10 |
| 20 | MILL-V | not on file | 4 | similar-part actuals | n/a | 45/49.5/52 | 6.200/6.467/6.569 | routings.csv MB-1880 op 20; closed_jobs.csv WO-7702, WO-7811 op 20 |
| 30 | MILL-V | not on file | 4 | similar-part actuals | n/a | 29/31.5/34 | 3.100/3.204/3.284 | routings.csv MB-1880 op 30; closed_jobs.csv WO-7702, WO-7811 op 30 |
| 40 | INSP | not on file | 4 | similar-part routing | n/a | 10/10/10 | 2.0/2.0/2.0 | routings.csv MB-1880 op 40 |
| — | OSP | — | — | PO price | — | — | — | PO-30602, 385.00/lot ≤300 pcs |
| — | marking | — | — | BLOCKED | — | — | — | — |
| — | FAI | — | — | BLOCKED | — | — | — | — |

## 12. Assumptions (internal)

1. Rates are taken from the finance memo dated 2026-10-01 and are not recorded on a plant rates page.
2. Margin is read as margin on sell price, applied after the material and OSP markups.
3. One setup per quantity break. The FA comes from the first pieces of the same run.
4. Run time is charged on starts (1.84% scrap), i.e. scrap costed at full value-added. PO price stands in for standard material cost.
5. Whole plates are charged. 27 blanks/plate (3 mm kerf, 5 mm blank allowance).
6. The mill cert is included in the plate price.
7. Anodize is charged at ⌈q/300⌉ lots of 385.00, with no quantity discount assumed.
8. Currency is USD. The RFQ states no currency, and all cost data is in USD.
9. The MB-1880 hours stand in for MB-2040 with no feature adjustment. This is the largest uncertainty.
10. Validity should be short (suggest 30 days) because plate rose 3.5% between Aug and Sep. No plant standard validity is on file.

=== END ===
