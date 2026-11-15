# quote-build — Harbor Robotics Lab, reBot B601 DM part sets (NOREF-20261112) — DRAFT

Run 2026-11-14. Skill followed: `quote-build` (Chain 1 final step). SYNTHETIC test data, fictitious plant. Nothing was sent or written to any system.
Quote reference used here: `Q-HARBOR-ROBOTICS-LAB-NOREF-20261112-01` (the customer gave no RFQ reference).

## Notes to the estimator (outside both documents)

**Headline: this draft has no price.** Every hour is unknown (no routing, no closed-job actuals, no confirmed geometry estimate, no plant machining data), and no labour, burden or margin rate is on file in either route the skill accepts. Material is the only cost line with a sourced number, and only as a partial lower bound. Per the skill, no job total and no unit price is produced by any route.

**Plant setup.** `plant_setup.py find` (run from the work folder) returned `exists: false` and `rates_exists: false` for `work/plant-setup/plant-context.md` and `plant-rates.md`. Artifact tools were not used in this run (run rules), so the setup and rates pages were not looked up; no `CLAUDE.local.md` profile exists in the work folder. Result: no Plant context, no machining data, no demonstrated tolerance capability, no plant quote template, no standard commercial terms.

**Rates.** `MFG_LABOR_RATE`, `MFG_BURDEN_RATE`, `MFG_MARGIN_RULES`, `MFG_SCRAP_COSTING_BASIS`: none set (checked by name). The finance memo you supplied (`inputs/rates_memo.txt`, dated 1 Oct 2026) holds per-work-centre burdened shop rates, a material markup, a target margin figure, an outside-processing markup and a scrap-costing rule. **It is not a rate on file**: a rate handed to this run is not used and is not repeated here. To make it the plant's number, say *"update our labour rate"* (onboarding step 10, records each rate with a name and date on the plant's private rates page), or set `MFG_LABOR_RATE` / `MFG_BURDEN_RATE` / `MFG_MARGIN_RULES` in the environment. The quote completes as soon as they are set **and** hours exist. Note for onboarding: the memo states one burdened rate per work centre, while the profile holds labour and burden separately; onboarding should record which way the plant wants it.

**Gate state.** `bid_decision_state: draft`, `recommendation: bid` with `recommendation_provisional: true`, `gates_passed: []`. The request said "build the draft quote", so this run proceeded **on an unconfirmed recommendation**, recorded on both documents' internal side. Gate 1 (open questions) has not been sent; Gate 3 (design / tolerance reading / operation list) has not been passed, so no geometry-derived hour may be priced.

**Provenance of the BOM handoff.** The intake form (2026-11-14) recorded the STEP and BOM as named but **not received**. `02_bom_handoff.json` now gives a part list read from a STEP named `reBot_B601_DM_v1.1_20260625.step` (sha256 recorded in the handoff) plus the project readme, sourced from a public repository commit. It is not recorded as the file the customer sent. Its `bom_status` is `T`, its `engineering_verdict` is `Z` (not a verified pass) and it lists 7 engineering-missing items, including per-part tolerances, finish, inspection and functional requirements. The file name and revision (v1.1) match the intake line's `revision`, so there is no revision block, but the customer should confirm it is their file (question below).

### Questions recorded instead of asked

To the estimator (internal):
1. Gate 4: who should be recorded as approving release of this quote? (Name not given; not inferred.)
2. Do you want the finance memo's rates recorded through onboarding ("update our labour rate" and the burden / margin equivalents) so this and later quotes can price?
3. Gate 3: the handoff carries bounding boxes, volumes and face counts only. Who will produce the operation list per part (or a geometry estimate) and confirm it, so hours can be derived?
4. Six pieces per set are `CNC + Sheet Metal`. The equipment list has no forming asset. Quote forming through an outside partner (needs a sourced price), or offer those parts as excluded / no-bid?
5. `02_SLIDER_EXTENSION` (smallest dimension 17.8 mm) is thicker than any 5052 stock on our POs. Bar or thick plate needs a supplier quote.
6. The bid decision is still `draft`. Confirm bid / no-bid at Gate 2 before this goes further.

To the customer (add to the Gate 1 email, which has not been sent; questions 1, 2 and 8 of the intake draft still stand as written except where noted):
- Q1/Q2 update: we have a v1.1 STEP (`reBot_B601_DM_v1.1_20260625.step`) and the project readme parts list, giving {{PIDS}} CNC aluminium part numbers, {{PCS}} pieces per arm set. Please confirm this is your file and your set composition, and that 3D-printed parts and fasteners are not part of this request.
- Q3 update: the readme states "Key dimension tolerance: ±0.02 mm GB/T1840-M" (readme line 129). Which dimensions on each part are the key dimensions? Please confirm the standard designation as written, and what applies to every other dimension.
- Q4 update: the readme states 5052; temper is not stated. Is 5052-H32 acceptable?
- Q5 unchanged, plus: the manufacturer tolerance for the MGN9-170 rail is not stated.

{{CUSTOMER_BLOCK}}

{{INTERNAL_BLOCK}}

## Files written by this run
- `out/quote-build-reply.md` — this reply, both delimited documents in full
- `out/figures.json`, `out/material-basis.csv` — figures block and material table, produced by `out/scripts/compute_quote_figures.py`
- `out/operation-record.json` — the operation record kept with the quote
- `out/sales-command-center.html` — the Sales command-center page, offered

No Word or Excel copy this run: no Word or Excel writer available (python-docx and openpyxl are not installed, and installing is outside the run rules).
