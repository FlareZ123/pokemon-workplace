# Turn-aware Energy attack readiness

Source: `tools/energy_turn_windows.py`. SFT: `results/tests/energy_turn_windows/reproduce.py`.

This finite, known-zone planner wraps the existing Iron Thorns ex and Bagon/Crispin Energy searches with ordinary first-turn restrictions, canonical per-turn quotas, and an own-turn deadline. A permitted attack must both satisfy the typed Energy payment and occur in an attack-allowed turn window.

Official rules: the starting player cannot attack or play a Supporter on their first turn. See [Pokémon rulebook](https://assets.pokemon.com/assets/cms2-en-uk/pdf/trading-card-game/rulebook/par_rulebook_en.pdf) and the [Sword & Shield rule change](https://www.pokemon.com/uk/news/pokemon-tcg-retrospective-the-sword-shield-era). The bundled Advanced Player's Rulebook distinguishes effect Energy attachment from the ordinary hand attachment.

| Fixed represented line | Going second earliest own turn | Going first earliest own turn |
| --- | --- | --- |
| Iron Thorns ex: Tag Call -> Guzma & Hala -> DCE + Thunder Mountain -> Volt Cyclone | 1, four setup actions | 2, five actions including ending own turn 1 |
| Bagon: Crispin for Fire and Water Energy -> Dragon Claw | 1, two setup actions | 2, three actions including ending own turn 1 |

The same baseline Energy relationships do not imply the same turn-one opportunity. The search prioritizes earliest own-turn attack over shorter paths on a later turn. It conserves attached units, zones, and active Stadium state across turn transitions and resets ordinary action usage. It rejects inconsistent legacy-flag versus canonical-budget inputs, carries source-scoped locks forward, and exposes hypothetical explicit opening-turn rule exceptions independently.

**Boundaries:** this is deterministic mechanical feasibility under exact known initial zones. The opponent is assumed inert, future card draws and Prize uncertainty are omitted, and unsupported card effects are not inferred. It is not a full match simulation or win-rate estimate. Source-specific special effects can change turn restrictions and require separate validation.

Next: integrate opponent turns, turn draws and physical Prize beliefs before estimating playable deck-list consistency.


## Printed opening-attack exceptions (source-attested)

The complementary exact-print classifier `tools/opening_attack_permissions.py` inventories `legalities.expanded == "Legal"` English attacks with literal first-turn wording in the current bundled card snapshot. The standalone SFT is `opening_attack_regressions.py`.

| Printed-text family | Expanded-labeled prints | Representative attack |
| --- | ---: | --- |
| Going-first attack permission | 21 | Pheromosa-GX `sm5-140` Fast Raid |
| Only usable going second on own turn 1 | 12 | Scream Tail ex `sv6-94` Scream |
| Unusable going second on own turn 1 | 8 | Terapagos ex `sv7-128` Unified Beatdown |
| Going-second first-turn enhanced effect | 10 | Cresselia `swsh6-64` Crescent Glow |

The 51 prints partition completely into four recognized families, with no unclassified first-turn attack wording among cards labeled Expanded legal. They include multiple printings of the same functional attack. For example, the Scream Tail ex first-turn lock is unavailable after its player's first turn, while the Fast Raid exception applies to its explicitly printed attack and never to a separate attack on the same Pokémon. The bonus category changes the attack's effect during that window; it does not override the starting player's ordinary attack prohibition.

This is source-text and current-bundled-database coverage, subject to all external release-date, printing-equivalence, and ban-list checks required for tournament legality. It also excludes first-turn restrictions from other card-text locations, Abilities, and effects that modify turns. A future planner can pass the classified attack's exact print-and-attack identity into `attack_ready` rather than enabling a generic board-wide exception.
