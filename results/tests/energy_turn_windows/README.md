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
