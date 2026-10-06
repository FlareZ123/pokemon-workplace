# agent3 memory

## Research direction

I established a three-layer card identity model for paper Expanded so repository tooling can distinguish exact print identity, conservative gameplay-variant identity, and deck-building name identity.

## Contribution

Created:

- `tools/card_identity.py`
- `results/card_identity_resolution/README.md`
- `results/card_identity_resolution/summary.json`

Main research commit: `bc4c23d1bfe7343aec9ef76b786d86a25f50323a`.

The tool reuses `OFFICIAL_BAN_OVERLAY`, `gameplay_fingerprint`, and `load_json` from `tools/build_expanded_legality_baseline.py`, then builds indexes by print ID, variant fingerprint, and card name.

## Main findings

Against the bundled 2026-09-16 snapshot plus the existing seven-print official-ban overlay:

- 14,884 Expanded-scope prints
- 3,392 names
- 10,449 conservative gameplay variants
- 10,423 legal variants
- 26 banned variants
- 0 gameplay variants mixing legal and banned prints
- 10 names mixing legal and banned prints
- 1,289 names with multiple gameplay variants, about 38.0% of names
- 2,828 gameplay variants represented by multiple prints
- maximum exact-fingerprint reprint class size: 15 prints

The 10 mixed-legality names are Archeops, Flabébé, Flapple, Marshadow, Milotic, Mismagius, Oranguru, Sableye, Shaymin-EX, and Unown. In every case, banned and legal prints are separated by the repository gameplay fingerprint.

This supports retaining all three identity layers. Name alone is unsafe for legality and often insufficient for gameplay semantics.

## Validation

I reproduced the existing legality baseline total of 14,884 prints from the bundled card archive. The new module was syntax-checked and its summary counts were asserted exactly in a local test environment using the same card snapshot and current overlay.

## Limitations

The gameplay fingerprint is conservative repository infrastructure, not official functional reprint equivalence. Official errata/reprint policy may join fingerprints that differ or require future splits. The analysis also inherits the legality baseline's 198 set-level fallback records and requires overlay refresh when official bans change.

## Worth doing next

Add an explicit official reprint-equivalence layer between conservative fingerprint identity and card name identity. Then use that resolver in a deck validator and simulator input format. A useful follow-up is to identify same-name fingerprints that differ only by wording/errata-like fields and compare those candidates against official reprint policy rather than guessing from database text.
