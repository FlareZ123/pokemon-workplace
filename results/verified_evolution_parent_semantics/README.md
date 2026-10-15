# Missing evolution parent: Zoroark, 30th Celebration 96

## Confirmed physical print

English **30th Celebration #96**, `me55-96`, Zoroark (120 HP, Stage 1, Nighttime Byway), explicitly states **Evolves From: Zorua**.

Primary evidence: [The Pokémon Company's official card page](https://www.pokemon.com/us/pokemon-tcg/pokemon-cards/series/30th/96).

The bundled `resources/cards/en/me55.json` record has the correct Stage 1 subtype, HP, Ability and attack but omits the `evolvesFrom` field entirely. This is a **source-data error** and can obstruct evolution-line matching in consumers using the printed parent, or give the wrong gameplay fingerprint. The source archive is kept immutable.

## Reproduction and scope

- Exact source ID: `me55-96`
- Source `evolvesFrom`: absent
- Printed `evolvesFrom`: `Zorua`
- Audited patch: `tools/verified_evolution_parent_repairs.py`
- Cross-language patch manifest: `results/verified_card_metadata_boundary/overrides.json`
- Regression: `python -m results.verified_evolution_parent_semantics.reproduce`

The function guards print ID, name, supertype, Stage 1, HP, regulation mark and Nighttime Byway Ability. It is idempotent, preserves source immutability, rejects an unexpected parent or identity change and returns unrelated objects untouched. The shared Python normalizer and Node CommonJS manifest consumer can use the same correction.

## Limits

This validates the printed evolution parent and source normalization. It does **not** establish that Twinleaf implements Nighttime Byway or that a deck using Zoroark is competitively strong. The archive scan that led to this finding exposed one Stage 1/Stage 2 record with no parent as of the 6 October source snapshot, but this criterion alone cannot prove every other evolution line is correct.
