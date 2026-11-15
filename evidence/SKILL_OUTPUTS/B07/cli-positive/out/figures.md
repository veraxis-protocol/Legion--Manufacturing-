# Figures block — SRC-2026-11-15-BSH-1210 (INTERNAL)

Produced by `out/scripts/compare_bids.py`, run 2026-11-15T13:12-05:00. Every number in the package notes and comparison is quoted from here.

| Figure | Value | Computed from | Filter or query |
|---|---|---|---|
| MRP rows for BSH-1210 | 3 | demand.csv | item == "BSH-1210" |
| Revisions on MRP rows | A | demand.csv | distinct rev |
| Total MRP requirement (pcs) | 3200 | demand.csv | sum qty_required |
| MRP horizon | 2026-12 to 2027-02 (3 months) | demand.csv | min/max month |
| Requirement 2026-12 (pcs) | 800 | demand.csv | month == "2026-12" |
| Requirement 2027-01 (pcs) | 1200 | demand.csv | month == "2027-01" |
| Requirement 2027-02 (pcs) | 1200 | demand.csv | month == "2027-02" |
| Largest single month (pcs) | 1200 | demand.csv | max qty_required |
| Average per month (pcs) | 1066.7 | demand.csv | total / months |
| Earliest possible need date (month start, date within month not in export) | 2026-12-01 | demand.csv | month == "2026-12" |
| Historical usage / PO / receipt rows | 0 — none supplied | inputs folder enumerated | no usage, PO or receipt file present in ./inputs |
| Forecast beyond MRP horizon | none supplied | inputs folder enumerated | no forecast/EAU file present |
| Mandated quantity breaks | 800, 1200, 3200 | demand.csv | first month (800), largest month (1200), full horizon (3200) |
| fields_missing, Alder Sintered Parts | 12 | bid_supplier_A.txt | mandated fields checked one by one |
| fields_missing, Birch Powder Metal | 12 | bid_supplier_B.txt | mandated fields checked one by one |
| Bids received / suppliers known | 2 of 2 | inputs/supplier | bid_*.txt files |
| Approved suppliers confirmed | 0 of 2 — no approved supplier table (no plant profile) | plant profile | profile_path does not exist |
| Birch Powder Metal extended @ 3200 | 1568.00 USD | bid_supplier_B.txt, line 3 | 0.49 x 3200 |
| Birch Powder Metal first-order total @ 3200 (incl. one-time tooling) | 3418.00 USD | bid_supplier_B.txt, line 3 | 1568.0 + 1850.0 |
| INDICATIVE Alder first release: MOQ 1,000 x 1,000-pc price | 620.00 USD | bid_supplier_A.txt | assumes 800 needed but MOQ forces 1,000; excl. freight (FOB origin) |
| INDICATIVE Alder 3,200 pcs at the 3,000-pc price | 1760.00 USD | bid_supplier_A.txt | ASSUMES the 3,000 break applies at 3,200 — not stated; excl. freight and tooling (price not stated) |
| INDICATIVE gap: Birch first-order total minus Alder indicative @3,200 | 1658.00 USD | both files | headroom for Alder freight before Birch is cheaper on the order |
| Piece-price difference @3,000/3,200 (Alder - Birch) | 0.06 USD/ea | both files | 0.55 - 0.49 |
| Break-even volume for Birch tooling vs Alder piece price | 30,833 pcs | both files | tooling / piece-price difference; vs 3,200 pcs in MRP horizon |
| Birch tooling as share of its 3,200 first order | 54.1 % | bid_supplier_B.txt | tooling / first-order total |
| Alder arrival if PO placed today (4 wk ARO, transit not stated) | 2026-12-13 | bid_supplier_A.txt | 2026-11-15 + 4 weeks |
| Birch arrival if PO placed today (6-7 wk, start event not stated) | 2026-12-27 to 2027-01-03 | bid_supplier_B.txt | 2026-11-15 + 6/7 weeks |
| Days Alder lands after earliest Dec need date | 12 | computed | arrival - 2026-12-01 |
| Days Birch lands after earliest Dec need date | 26 to 33 | computed | arrival - 2026-12-01 |
| Response tracker: suppliers with a send recorded by the buyer | 0 | conversation | no send reported; bids predate this package |
