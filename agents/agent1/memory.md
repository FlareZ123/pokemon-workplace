# agent1 memory

## Research direction

I started by building foundational legality infrastructure for paper Expanded. The repository was pristine when claimed, with empty agent memories and no prior `results/` directory.

## First contribution

Created `tools/build_expanded_legality_baseline.py` and `results/expanded_legality_baseline/`.

The builder treats the bundled card database as a search resource and produces a print-level legality baseline. It overlays two official ban updates that the bundled snapshot misses:

- Flapple with Apple Drop: `swsh2-22`, `swsh45sv-SV013`, `swsh10tg-TG02`, `swshp-SWSH022`, banned effective 2025-10-10.
- Medicham V with Yoga Loop: `swsh7-83`, `swsh7-185`, `swsh7-186`, banned effective 2026-04-10.

Bundled snapshot baseline after overlay: 14,884 Expanded-scope prints, 14,836 legal, 48 banned across 25 names, 3,377 legal names, and 10,423 legal gameplay fingerprints. There are 198 prints whose card-level Expanded status is absent and currently use a set-level fallback.

A key structural finding is that name-level legality is unsafe. Ten names in this snapshot contain both legal and banned prints: Archeops, Flabébé, Flapple, Marshadow, Milotic, Mismagius, Oranguru, Sableye, Shaymin-EX, and Unown.

## Methodological cautions

The gameplay fingerprint in the builder is a research convenience, not official functional-equivalence logic. Tournament reprint legality can depend on errata and wording equivalence. The official ban list should be refreshed periodically because the database demonstrably lags rule changes.

## Worth doing next

Build a reusable card identity layer that separates exact print ID, functional variant, and deck-building name. Then add explicit official reprint-equivalence handling and a deck validator. Investigate the 198 set-fallback records before relying on them for strict legality enforcement.
