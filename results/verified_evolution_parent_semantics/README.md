# Verified evolution parents: Zoroark and Archen

## Official-print evidence

Three physical print IDs in the supplied card archive have an omitted or misspelled evolution parent.

| English print | Source value | Verified parent | Independent evidence |
| --- | --- | --- | --- |
| **Zoroark**, 30th Celebration #96 (`me55-96`) | `evolvesFrom` absent | **Zorua** | [Official Zoroark #96](https://www.pokemon.com/us/pokemon-tcg/pokemon-cards/series/30th/96) explicitly prints “Evolves From: Zorua” |
| **Archen**, White Flare #50 (`rsv10pt5-50`) | `Antiuqe Plume Fossil` | **Antique Plume Fossil** | [Official White Flare Antique Plume Fossil #79](https://www.pokemon.com/us/pokemon-tcg/pokemon-cards/series/rsv10pt5/79) explicitly says it evolves into Archen |
| **Archen**, White Flare #131 (`rsv10pt5-131`) | `Antiuqe Plume Fossil` | **Antique Plume Fossil** | Same official printed Fossil; both Archen prints have identical Pokémon combat semantics |

The Zoroark record correctly encodes Stage 1, 120 HP and its Nighttime Byway Ability but lacks the printed parent. Both Archen records correctly encode Stage 1, 80 HP and Acrobatics but misspell `Antique` as `Antiuqe`, which cannot match the Fossil card's name. The matching official Fossil item says “Evolves into Archen,” giving an independent source for the lineage. The 2026-10-06 card archive remains immutable.

## Scope, implementation and tests

The exact-print repairs are in `tools/verified_evolution_parent_repairs.py`, composed into `tools/verified_card_metadata.py` before card fingerprints or deck record extraction. The audited family contains 3 print IDs, raising the shared print correction manifest from 72 to **75**. The deterministic manifest at `results/verified_card_metadata_boundary/overrides.json` exposes each `evolvesFrom` change to JavaScript consumers of `simulation/twinleaf/verified-card-metadata.cjs`.

The regression `python -m results.verified_evolution_parent_semantics.reproduce` checks exact physical source values, guarded updates, idempotence, unchanged unrelated records, source immutability and consistency with current semantic fingerprints. `node simulation/twinleaf/test-verified-card-metadata.cjs` independently checks all 75 JSON manifest corrections, including these three. Windows CI is available in `.github/workflows/validate-verified-evolution-parent.yml` and `validate-verified-card-metadata-boundary.yml`.

This tests source-data meaning and normalization. It does not establish that Twinleaf implements the affected Pokémon's Abilities or the Fossil evolutionary rule correctly. Gameplay engine support and head-to-head match strength require separate evidence.

## Discovery method and limitations

An archive-wide scan isolated Zoroark as the only Stage 1/Stage 2 Pokémon missing `evolvesFrom` outright. A separate scan of Stage 1 parents absent from all Basic Pokémon names surfaced the two White Flare Archen typos, alongside numerous legitimate fossil evolution paths and older special-stage cases. Missing-parent and unknown-Basic-parent tests are discovery heuristics, not general legality proofs. Physical card text remains the audit authority.
