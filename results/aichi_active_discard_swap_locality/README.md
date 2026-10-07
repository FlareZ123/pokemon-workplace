# Aichi Active-swap locality for Guzma & Hala discard families

## Result

Changing the non-Jirachi starting Active from the existing policy's Basic `A` to Bunnelby changes the modeled Guzma & Hala discard family only through the two swapped names.

Across 100,000 accepted-opening trials, every payment edge added by Bunnelby-first contains `A`, the displaced default Active, and every payment edge removed by Bunnelby-first contains Bunnelby. There were zero violations across all seven endpoints.

| Endpoint | Comparable | Added edges | Removed edges | Net/state |
| --- | ---: | ---: | ---: | ---: |
| core | 10,343 | 48,235 | 40,627 | +0.735570 |
| Pidgeot | 9,586 | 43,399 | 34,564 | +0.921657 |
| Stoutland | 7,947 | 35,895 | 28,401 | +0.942997 |
| dual Stage 2 | 6,936 | 26,500 | 25,145 | +0.195358 |
| Item lock | 9,578 | 43,429 | 14,009 | +3.071622 |
| Item lock + Pidgeot | 5,384 | 8,233 | 11,979 | -0.695765 |
| Item lock + Stoutland | 4,484 | 7,045 | 10,015 | -0.662355 |

## Why this is exact in the current model

Let `H` be the opening hand plus first-turn draw and let the existing Active be `A`. The existing policy passes `H - A` to the discard evaluator, while Bunnelby-first passes `H - Bunnelby`.

For a discard pair containing neither swapped name, the Basic endpoint checker adds the chosen Active back into direct Basic inventory. The resulting multisets are identical:

- existing policy: `(H - A - pair) + A`
- Bunnelby-first: `(H - Bunnelby - pair) + Bunnelby`

The remaining deck and search state are the same. Such a pair therefore has the same feasibility under both policies. Any newly added pair must use the displaced Active name, and any removed pair must use Bunnelby.

## Interpretation

Starting-Active choice is a localized one-copy protection/exposure operation on the G&H payment hypergraph. The new Active leaves the hand payment surface while the displaced Active enters it.

This explains the endpoint-dependent pair-count changes and suggests an efficient optimizer representation: reevaluate edges incident to the two swapped Basic names instead of rebuilding the whole discard graph.

## Scope

This proof is specific to the current first-turn `route_flex` model. A fuller game model can break locality through retreat costs, Abilities, damage, matchup effects, lock geometry, or continuation value.

## Reproduction

- `tools/aichi_active_discard_swap_locality.py`
- `results/aichi_active_discard_swap_locality/reproduce.py`
- 100,000 trials, seed 20261007
