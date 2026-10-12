# Shared verified-card metadata normalization boundary

The complete Pokémon TCG research code needs a single reusable definition of verified card-source corrections. Prior to this integration, gameplay fingerprinting and the 60-card deck validator each applied independent lists of repairs. This made future divergence likely whenever a new exact-print source correction was discovered.

## Implementation

`tools/verified_card_metadata.py` composes four audited and separately tested print-local corrections in one explicit order:

- 2 missing Stage/Prize field entries, covering Pitch Black Mankey and Mega Chandelure ex.
- 1 missing Tera subtype and Bench immunity on Prismatic Evolutions Terapagos ex.
- 45 extra generic two-Prize rules on current Mega Evolution ex prints.
- 24 duplicate Tera Bench immunity statements on older Tera ex prints.

All **72** print IDs are mutually disjoint in this snapshot. Each repair preserves the immutable card archive, allows already-corrected input, and refuses unexpected source mutations. The shared interface preserves original object identity when the print ID is unrelated, avoiding unnecessary deep copies across the full card universe.

Both `tools/current_card_semantics.py` and `tools/deck_validator.py` now call the same function, reducing the chance of a card being represented differently during deck validation and card equivalence analysis.

## Evidence and reproducibility

Every repair has a documented card-source audit and a dedicated independent regression:

- [Stage semantics](../verified_stage_semantics/)
- [Terapagos Tera status](../verified_tera_semantics/)
- [Mega three-Prize Rule Box](../verified_mega_prize_rules/)
- [Duplicated Tera damage prevention](../verified_tera_duplicate_rules/)

Run `python -m results.verified_card_metadata_boundary.reproduce` to check exact ID family coverage, disjointness, idempotence, original-card immutability, synchronized downstream records, and unchanged unrelated cards.

Windows CI in `.github/workflows/validate-verified-card-metadata-boundary.yml` runs this compatibility suite and all source-specific corrections plus reprint and deck-validator regressions.

## Cross-language manifest for JavaScript research

The deterministic JSON artifact [`overrides.json`](overrides.json) enumerates all 72 source-print field corrections as exact `before` and `after` pairs, with immutable print IDs. This permits the Node-based Twinleaf research adapters to consume the same provenance-guarded corrections without porting the underlying Python normalizers.

The canonical generator is `tools/export_verified_card_metadata.py`. Run `python -m results.verified_card_metadata_boundary.reproduce_export` to assert that the checked-in artifact is byte-for-byte regenerable from the bundled archive and audited Python repair functions. The Node CommonJS consumer `simulation/twinleaf/verified-card-metadata.cjs` uses deep equality checks and copies only changed arrays. Its runnable SFT is `node simulation/twinleaf/test-verified-card-metadata.cjs`.

These interfaces only correct source card records. They do not add cards to Twinleaf's implemented card registry or patch any upstream game-engine behavior.

## Limits

The 72 audited identities are a **coverage set**, rather than a claim that the rest of the 20,000-plus-card archive has no anomalies. The shared boundary does not automatically modify unrelated print IDs and is deliberately separate from official tournament legality and competitive win-rate estimation.
