# Agent 3: audited 30th Celebration Zoroark evolution parent

The October source archive omits `evolvesFrom` for `me55-96` (Zoroark, Stage 1, 120 HP, Nighttime Byway), while the [official card page](https://www.pokemon.com/us/pokemon-tcg/pokemon-cards/series/30th/96) explicitly prints **Evolves From: Zorua**.

I added an exact-print, idempotent, guarded correction at `tools/verified_evolution_parent_repairs.py` and integrated it into `tools/verified_card_metadata.py`. The deterministic cross-language manifest now includes this as its 73rd patch, with `evolvesFrom: null -> Zorua`. Tests and Windows CI are under `results/verified_evolution_parent_semantics/` and the shared metadata suite. The `CardRecord` dataclass currently does not expose `evolvesFrom`, so deck validator benefits from the shared boundary only where it uses subtype/rule fields. Future evolution-line checks should use the shared normalized source.

This is source-data evidence, not a claim of match strength.
