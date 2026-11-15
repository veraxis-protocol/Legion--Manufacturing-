# Figures block - SRC-2026-11-14-MGN9-170-RAIL (internal)

| Figure | Value | Computed from | Filter or query |
|---|---|---|---|
| Rails per arm | 1 | 02_bom_handoff.json | purchased_rail.quantity_per_arm |
| Arm sets in the inquiry | 20 | intake NOREF-20261112 | line_no 1 quantities[0].qty (line 39) |
| Rail demand (rails per arm x sets) | 20 | BOM x intake; equals intake line 2 qty | 1 x 20; intake line 68 qty 20 |
| Forecast / EAU | none supplied (eau: null) | intake NOREF-20261112 | line_no 2 eau (line 76) |
| Purchase / receipt / usage exports found | 0 - not found by search | inputs folder enumerated (6 files) | filename matches po|purchase|receipt|usage|vendor|supplier_list|item_master |
| Customer delivery date for the arm sets | 2027-01-31 | intake NOREF-20261112 | line_no 2 required_delivery (line 75) |
| Calendar days from today to that date | 78 | computed | 2027-01-31 - 2026-11-14 |
| Approved suppliers on file for this commodity | 0 - no plant profile (plant_setup find: exists false) | plant_setup.py find | ### Approved suppliers table not present |
| Candidate suppliers (from the returned bids) | 2 | inputs/e2e_bids | files rail_bid_*.txt |
| Candidates not confirmed approved | 2 | bid records | approval_status == not_confirmed_approved |
| Bids received / suppliers known | 2 of 2 | inputs/e2e_bids | one bid per file |
| Sends recorded (per buyer) | 0 | no Open work page, no buyer statement | never reconstructed |
| Off-format bids | 2 | bid records | conformance == off_format |
| Currencies stated | USD | bid records | currency |
| Freight bases stated | Delivered DDP | FOB origin | bid records | freight_basis |
| Quantity break priced by both bids | none | bid records | offered_qty equal across bids |
| Xylem Linear Motion unit price at 100 | 11.40 USD | inputs/e2e_bids/rail_bid_X.txt line 3 | as quoted |
| Xylem Linear Motion extended at its quoted qty (100 x 11.40) | 1140.00 USD | computed | unit_price x offered_qty |
| Xylem Linear Motion MOQ | 100 | inputs/e2e_bids/rail_bid_X.txt line 3 | as quoted |
| Xylem Linear Motion MOQ minus our demand (units others would have to pool) | 80 | computed | moq - demand |
| Xylem Linear Motion our demand as % of its MOQ | 20.0% | computed | 100 x demand / moq |
| Xylem Linear Motion fields_missing | 15 | bid record | mandated-field check, 20 fields |
| Yarrow Motion Parts unit price at 250 | 9.90 USD | inputs/e2e_bids/rail_bid_Y.txt line 3 | as quoted |
| Yarrow Motion Parts extended at its quoted qty (250 x 9.90) | 2475.00 USD | computed | unit_price x offered_qty |
| Yarrow Motion Parts MOQ | 250 | inputs/e2e_bids/rail_bid_Y.txt line 3 | as quoted |
| Yarrow Motion Parts MOQ minus our demand (units others would have to pool) | 230 | computed | moq - demand |
| Yarrow Motion Parts our demand as % of its MOQ | 8.0% | computed | 100 x demand / moq |
| Yarrow Motion Parts fields_missing | 17 | bid record | mandated-field check, 20 fields |
| Mandated response fields checked per bid | 20 | package section 7 | MANDATED list in this script |
