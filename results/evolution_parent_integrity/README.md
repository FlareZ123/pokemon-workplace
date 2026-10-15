# English source archive evolution-parent integrity audit

## Question and approach

Which English Stage 1 or Stage 2 Pokémon records are missing their printed evolution parent, or name a parent not found anywhere in the complete English source archive?

The archived set of 20,635 card records contains 6,901 Stage 1 or Stage 2 Pokémon. A reproducible scanner at `results/evolution_parent_integrity/reproduce.py` loads the complete archive and compares each evolution's `evolvesFrom` against every printed card name. Raw results:

| Category | Raw source records |
| --- | --- |
| Missing evolution parent | `me55-96` Zoroark |
| Unknown parent name | `rsv10pt5-50`, `rsv10pt5-131` Archen: `Antiuqe Plume Fossil` |
| Special-language parent | `xy12-109` Exeggutor: `タマタマ[Exeggcute]` |

## Confirmed errors

- The [official Zoroark #96](https://www.pokemon.com/us/pokemon-tcg/pokemon-cards/series/30th/96) page states the missing parent **Zorua**.
- The [official Antique Plume Fossil #79](https://www.pokemon.com/us/pokemon-tcg/pokemon-cards/series/rsv10pt5/79) explicitly says the Pokémon evolves into **Archen**. Both Archen records have the typo `Antiuqe`; the fossil's actual title is `Antique Plume Fossil`.

After applying the three exact-print corrections in `tools/verified_evolution_parent_repairs.py`, the scanner finds zero missing parents and one special-language unmatched parent.

The `xy12-109` Exeggutor record retains a Japanese-text parent. This is left untouched because a name-based heuristic cannot determine whether its official printing or present-day rulings require a different value.

## Reproduction

Run `python -m results.evolution_parent_integrity.reproduce` on the root of the repository. The test asserts archive population, raw anomalous identities, exact source strings and normalized outcomes. Windows CI is at `.github/workflows/validate-evolution-parent-integrity.yml`. The [three-print official source audit](../verified_evolution_parent_semantics/) includes focused exact-print guards and cross-language manifest parity.

This is a **data-integrity heuristic**. A parent name existing in the archive does not prove the right family linkage, and exceptions such as fossils and Japanese-language promo text require specific card text. No claim about Twinleaf implementation coverage or game win rates follows from the scan.
