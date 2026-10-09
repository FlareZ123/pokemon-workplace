# Legacy Mega Evolution ends the turn unless Spirit Link is effective

## Question

Can the shared per-turn action budget distinguish XY-era Mega Evolution Pokémon-EX turn-end rules, a matching Spirit Link exemption, and newer Mega Evolution ex Pokémon whose rule boxes serve different purposes?

## Source-backed answer

Yes, using exact print metadata and the actual Tool attachment on the evolved Pokémon.

XY-era Mega Evolution Pokémon-EX prints (for example, M Charizard-EX `xy2-13`) include a rule that the turn ends when one of your Pokémon becomes a Mega Evolution Pokémon. Primal Kyogre-EX `xy5-55` has a similar Primal Reversion rule.

A matching Spirit Link Tool has precise text exempting evolution into a named Pokémon from ending the turn. For example, Charizard Spirit Link `xy12-75` permits M Charizard-EX to evolve and the turn to continue. A Spirit Link for another Pokémon is insufficient. A Tool whose effect has been suppressed is also insufficient.

By contrast, newer Mega Venusaur ex `me1-3` has the rule that the opponent takes three Prizes when that Mega Evolution Pokémon ex is Knocked Out. Its printed rule does not end the turn when it evolves.

All checked prints are in the bundled Expanded legal snapshot. This distinction shows why the word *Mega* and the subtype *MEGA* are insufficient to determine whether a turn-ending rule applies.

## State transition

`tools/legacy_mega_evolution_turn_end.py` bridges the physical `BoardState` evolution transition to canonical `TurnActionBudget`.

It requires:
- the exact target print and its printed `evolvesFrom` identity;
- an already-completed ordinary physical evolution retaining Tool, Energy and damage;
- unchanged Active/Bench positions;
- a live, unended turn.

It then determines whether the new print's `rules` contain the XY Mega rule or exact Primal Reversion wording. For a legacy rule, the turn closes by consuming `END_TURN`, unless the evolved Pokémon still holds a matching Expanded-legal Spirit Link by **exact Tool print ID**, with an active Tool effect. The result records the source print, exemption and turn boundary.

Because the Tool persists through evolution, its own effect can prevent the turn ending if it was attached before evolution and remains effective at the relevant boundary. The current board already exposes `pokemon_state.tool_effect_enabled`, so a Jamming Tower-like suppressed Tool fails to prevent the end.

## Validated witnesses

`results/legacy_mega_evolution_turn_end/reproduce.py` checks:

| Evolution | Tool state | Turn ends? |
| --- | --- | --- |
| Charizard-EX to M Charizard-EX | None | Yes |
| Charizard-EX to M Charizard-EX | Charizard Spirit Link effective | No |
| Charizard-EX to M Charizard-EX | Manectric Spirit Link (wrong target) | Yes |
| Charizard-EX to M Charizard-EX | Charizard Spirit Link with effect suppressed | Yes |
| Charizard-EX to M Charizard-EX | Link name without verified print ID | Yes, under this conservative model |
| Kyogre-EX to Primal Kyogre-EX | None | Yes |
| Kyogre-EX to Primal Kyogre-EX | Kyogre Spirit Link effective | No |
| Ivysaur to newer Mega Venusaur ex | None | No |

The regression also rejects a transition with incorrect printed evolution ancestry and proves a closed turn cannot subsequently attack.

## Full bundled Expanded legacy-Tool coverage

The companion audit `tools/legacy_mega_spirit_link_catalog.py` scans all set-in-scope effectively legal print records and matches exact printed legacy Mega Evolution/Primal Reversion turn-end rules against Spirit Link text naming the evolved Pokémon. The bundled corpus contains **92 effectively legal legacy Mega/Primal print records spanning 41 Pokémon names** and **35 matching Spirit Link Tool prints covering 34 named evolutions**. Seven legacy Mega Evolution names have **no matching Spirit Link print in this corpus**:

- M Absol-EX
- M Blaziken-EX
- M Diancie-EX
- M Heracross-EX
- M Kangaskhan-EX
- M Metagross-EX
- M Swampert-EX

The newest included print, **M Gardevoir-EX `me55c-106m`**, retains the old Mega Evolution turn-ending rule *without the historical `Mega Evolution rule:` prefix*. The compiler and catalog therefore recognize the exact effect wording as well as prefixed XY text. This reprint is covered by Gardevoir Spirit Link and increases the legal print count by one, without changing the 41 distinct names or seven uncovered names. A prefix-only audit would incorrectly omit this 2026 print.

That is an exact print-coverage observation. It does not by itself prove that no other card effect can manipulate a turn-ending consequence. Modern Mega Evolution ex prints are excluded because their different Rule Box text does not describe an evolution turn-end action. The independent reproducible `catalog.py` confirms the counts and seven-name coverage gap.

## Scope and limitations

This is an exact-print *turn-end bridge*, not a complete evolution rule executor. Upstream still must validate the game turn, restrictions on evolution, hand card provenance, and any conditions specific to how the Pokémon was evolved. The physical board kernel is responsible for keeping the Tool and Energy identities attached; this bridge verifies the before/after conservation boundary relevant to the turn-end decision.

Continuous Tool-effect resolution is an upstream input. In particular, the simulated `tool_effect_enabled=False` scenario demonstrates the consequence of Tool suppression, without claiming to have modeled all possible sources and orderings that suppress Tools. Reprinted cards or errata beyond the bundle must be audited separately.

Related research: [../canonical_turn_budget_owner/](../canonical_turn_budget_owner/), [../board_action_quota_derivation/](../board_action_quota_derivation/), [../condition_turn_sequence/](../condition_turn_sequence/).
