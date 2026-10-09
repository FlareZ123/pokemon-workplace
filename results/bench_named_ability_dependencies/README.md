# Named Ability co-presence constraints and hard Bench-capacity gates

## Question

Can a card-text extraction produce **provable capacity lower bounds** for synergistic Pokémon abilities without simulating their whole effects?

Yes, for an explicitly recognized class of named-Pokémon guards. A guard requiring named species simultaneously `in play` entails a minimum number of distinct in-play Pokémon. Only one Pokémon can occupy the Active Spot, so a necessary Bench capacity follows.

The reproducible scanner is `tools/bench_named_ability_dependencies.py`. Its regression is `.github/workflows/validate-bench-named-ability-dependencies.yml` ([passing run 37919161458](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37919161458)).

## Scope and evidence

The catalog uses the bundled `resources/sets/en.json` plus `resources/cards/en/` and the repository's effective paper Expanded legality classification `build_expanded_legality_baseline.classify_effective_legality`. That classification includes the explicit ban overlay, the print's database legality, and legal-set fallback for otherwise unmarked prints.

It conservatively recognizes clauses of the form:

- `if you have [named species] in play`
- `as long as you have [named species] in play`
- the corresponding `on your Bench` variants.

The parser splits explicit comma-and conjunctions, then requires every extracted name to exactly equal a known Pokémon name in the legal candidate pool. Generic categories, card types, and quantifier phrases are intentionally omitted and reported.

For the bundled snapshot, the extraction produces:

| Measure | Result |
| --- | ---: |
| Matching print-level Ability guard occurrences | 38 |
| Distinct source/Ability/condition/text variants | 25 |
| Source Pokémon names | 21 |
| Reciprocal single-name pairs | 3 |
| Variants requiring five or more Bench slots | 1 |

Coverage is intentionally partial. Counts do not mean there are only 25 conditional Pokémon abilities in Expanded.

A particularly important legality detail is `me55-4` Illumise's requirement for Volbeat. The card print lacks a `legalities.expanded` value in the provided database, but its containing release is classified as Expanded legal and the repository's established fallback includes it. A print-only filter would silently omit this dependency, along with several new Moltres/Articuno/Zapdos guards.

## Derivation

Let a source Pokémon with name `s` have an Ability requiring names `R={r1,...,rm}` in play. The source itself is already in play for its Ability to operate.

Define `N = |{s} union R|`, the number of **distinct simultaneously required Pokémon names**, including the Ability source.

Provided a single Pokémon cannot satisfy two distinct required names at the same time, its necessary Bench lower bound is:

`bench_min = N - 1`.

This assumes the required Pokémon can occupy the Active Spot when that minimizes Bench use. If the wording instead demands prerequisites `on your Bench`, the necessary bound is:

`bench_min = max(|R|, N - 1)`.

These are lower bounds, not sufficiency proofs. Specific effects may force a Pokémon to remain Active, increase the required number of copies, or prevent an Ability from working despite adequate space. The model currently uses distinct-name identity under ordinary conditions and should recheck any future multi-name transformation effects.

## Expanded-legal witness: Regigigas

**Regigigas, Astral Radiance `swsh10-130`**, Ancient Wisdom:

> Once during your turn, if you have Regirock, Regice, Registeel, Regieleki, and Regidrago in play, you may attach up to 3 Energy cards from your discard pile to 1 of your Pokémon.

All five named prerequisites differ from the source, Regigigas. Therefore the simultaneous configuration contains at least **six Pokémon**.

- Default game: five Bench slots plus one Active makes the named condition structurally possible.
- Collapsed Stadium (`swsh9-137`), four-slot Bench: at most five in play, making the condition impossible while the restriction applies.
- Parallel City (`xy8-145`), affected three-slot side: at most four in play, also making the condition impossible.
- Sky Field (`xy6-89`), eight-slot Bench: capacity no longer provides this obstruction.

This is a hard capacity feasibility claim from card text and ordinary board geometry; it does not establish that any of the listed Pokémon are accessible, protected from Ability lock, or able to attack effectively.

## Additional named interactions

The scanner identifies single-requisite reciprocal relationships:

- **Lunatone ⇄ Solrock:** Lunar Cycle, Sol Shade, New Moon, Heal Block, Resistance Shade across various prints.
- **Karrablast ⇄ Shelmet:** Stimulated Evolution Abilities in the provided 2026 print pool.
- **Lunala ⇄ Solgaleo:** Blessing of the Moone and Armor of the Sunne.

It also identifies higher-order predicates, including the Uxie/Mesprit/Azelf trio, the Simisage/Simisear/Simipour trio, and the Moltres/Articuno/Zapdos trio. A guard listing a source's own Pokémon name is handled without counting that same card twice.

These are **textual dependency edges**. Some are reciprocal opportunities, while others provide unrelated or situational effects. Their real strategic value requires the game state, Energy availability, position, Ability lock, and the exact effect of the named cards.

## Validation

Run:

`python tools/bench_named_ability_dependencies.py --self-test`

Five tests assert the snapshot totals; the Regigigas five-Bench bound; representative reciprocal pairs; legal-set fallback for Illumise; and the different geometry of `in play` versus `on your Bench`.

Run without flags to emit an auditable JSON list of every matched source print, requirement, original Ability text, capacity lower bound, and unparsed requirement phrase.

## Strategic connection

This supplements [bench_synergy_contraction/](../bench_synergy_contraction/): dependencies can have two simultaneous roles.

1. **Conditional utility:** keeping the partner preserves an Ability or engine, so survivor choice should maximize a joint continuation-value function rather than individual occupant scores.
2. **Hard feasibility:** a multi-name prerequisite cannot activate at all beneath a certain physical board capacity, regardless of its nominal card access or value.

In a future optimizer, a verified named prerequisite should compile into a capacity-aware hyperedge. The model should first establish whether the edge is physically reachable under the current Active/Bench geometry, then evaluate its contextual payoff and other requirements.

## Limitations and next steps

This first scanner misses `if X is in play`, numeric conditions like `at least 1 other Bouffalant`, requirements embedded in attacks or Trainer text, negations, self-name transformations, and abilities whose condition is outside the exact template. It should be expanded cautiously using positive fixtures, with unparsed clauses retained for manual review.

The number of printed cards or normalized guards does not measure the competitive importance of any archetype. The strongest next test is to bind selected named Ability prerequisites to the physical board-state kernel and show capacity-restriction-induced deletion/restoration of the corresponding usable action.
