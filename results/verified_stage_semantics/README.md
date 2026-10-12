# Verified stage metadata in current-semantic fingerprints

## Finding

Two print-specific errors in the bundled Pitch Black English card snapshot affect both deck validation and gameplay fingerprinting:

- `me5-42` Mankey omits the `Basic` stage label.
- `me5-115` Mega Chandelure ex omits `Stage 2` and its three-Prize Mega Evolution ex rule.

The corrections are independently verified in [the original card-data audit](../pitch_black_stage_metadata/). Agent1 integrated the guarded repair at the exact-print deck-validator boundary. The same correction is now applied before `current_semantic_fingerprint` by `tools/current_card_semantics.py`, so search/identity/reprint tools see a consistent representation without altering the raw card archive.

## State-conserving repair

The underlying `normalize_verified_stage_metadata` is restricted to two exact IDs and verifies name, Pokémon supertype, HP, and evolutionary identity. For the Mega Chandelure printing it accepts each independent source correction:

| Stage metadata | Three-Prize rule | Result |
| --- | --- | --- |
| Missing | Missing | Both repaired |
| Corrected | Missing | Rule repaired |
| Missing | Corrected | Stage repaired |
| Corrected | Corrected | Unchanged |

Unexpected states raise an error rather than being silently transformed. All four source combinations become identical to the same-set `me5-38` and `me5-99` in the current gameplay fingerprint. Mankey becomes a Basic Pokémon, consistent with its official catalogue entry.

This is a **verified source-data repair**. It provides no new historical reprint permissions, deck-legality exceptions, or match-win estimates.

## Reproduce

Run `python -m results.verified_stage_semantics.reproduce` from the repository root. The tests cover physical source records, corrected outcomes, idempotence, all four partial-data states, untouched original dictionaries, same-set print fingerprints, and unrelated-print preservation.

The Windows CI workflow `.github/workflows/validate-verified-stage-semantics.yml` additionally runs the existing stage-metadata, reprint-resolver, and deck-validator suites.

## Sources and limits

- [Official Pitch Black Mankey #42](https://www.pokemon.com/uk/pokemon-tcg/pokemon-cards/series/me05/42/).
- [Mega Chandelure ex special-illustration card record](https://limitlesstcg.com/cards/PBL/115).
- `resources/cards/en/me5.json` and the two printed same-set Chandelure variants.
- [Earlier data audit](../pitch_black_stage_metadata/) documents the checked field-level evidence.

Only the two audited IDs are changed. The complete archive has not been globally audited for missing stages or other metadata defects.
