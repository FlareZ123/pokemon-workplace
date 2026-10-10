# Exact resource coalitions for Shadow Rider after Trifrost

## Scope

This is an exhaustive finite subset study over seven binary action-resource switches in the deterministic Shadow Rider post-Trifrost recovery planner. It counts minimal sufficient resource combinations, with no probability interpretation.

The board scenario begins immediately after Regidrago VSTAR used Apex Dragon to copy Kyurem Trifrost on its Timeless-GX bonus turn, knocking out an unprotected Benched Mimikyu. Regidrago's last attack remains Apex Dragon, while the Shadow Rider player's Dialga-GX is in discard. The only Mimikyu starts in discard; Shadow Rider has a damaged Active VMAX, an unspent Supporter and manual attachment, an open Bench slot, an empty Active Tool slot, and access to an opponent's Bench target. All other required resources are fixed as described in the parent [response-turn model](../shadow_rider_post_trifrost_recovery/README.md).

Seven resource switches are varied: Tulip, Night Stretcher, Float Stone, Guzma, Acerola, Underworld Door and Dimension Valley. Every one of the **128 subsets** is checked by breadth-first action search and all non-minimal successful supersets are removed.

## Result A: two Psychic Energy in discard, none in hand

When Mimikyu and two Basic Psychic Energy start in discard, the only two minimal resource coalitions are:

- **Tulip + Float Stone + Underworld Door**. Tulip retrieves Mimikyu and two Energy. Underworld Door plus the manual attachment pays Copycat; Float Stone permits promotion without another Supporter.
- **Tulip + Float Stone + Dimension Valley**. The reduced Copycat cost requires only one manual Psychic Energy attachment.

Thus the exact success predicate *within this fixed state and action vocabulary* is

`Tulip AND FloatStone AND (UnderworldDoor OR DimensionValley)`.

Tulip is necessary because Night Stretcher can return only one card. Float Stone is necessary because spending the Supporter on Tulip prevents using Guzma or Acerola during the same turn. Another attachment channel or Dimension Valley is necessary for the original two-Energy Copycat cost.

## Result B: two Psychic Energy already in hand

If Mimikyu remains discarded but the two Psychic Energy are already in hand, **eight** minimal coalitions survive. These are the combinations of:

1. Night Stretcher + Float Stone, Night Stretcher + Guzma, Night Stretcher + Acerola, or Tulip + Float Stone to recover and promote Mimikyu;
2. Either Underworld Door or Dimension Valley to pay Copycat in conjunction with the manual attachment.

Board constraints sharply change the frontier:

| Condition | Minimal coalitions |
| --- | ---: |
| Full baseline, opponent has Bench, incumbent damaged and Tool-free | 8 |
| No opposing Benched Pokémon | 6; Guzma routes disappear |
| Incumbent Active undamaged | 6; Acerola routes disappear |
| Incumbent already has a Tool | 4; Float Stone routes disappear |

Guzma's first switching clause needs an opposing Bench target. Acerola needs a damaged Pokémon. Float Stone cannot be newly attached when the incumbent has a Tool, assuming no Tool-removal actions.

## Reproduction and interpretation

Run `python results/shadow_rider_recovery_coalitions/reproduce.py`. The program checks all 128 subsets per scenario, verifies each minimal witness with the parent recovery planner and confirms the observed removal of whole route families under the listed board constraints.

This is a concrete form of state-dependent resource substitutability. Night Stretcher can preserve the Supporter slot when Psychic Energy is already in hand. When that Energy is in discard with Mimikyu, Tulip becomes mandatory in the bounded model and makes Float Stone the critical promotion connector.

The experiment assumes named cards are accessible and their effects can be used. It ignores hidden draws, extra search cards, all alternative movement effects and complete damage/Prize resolution. The result is a reproducible classification of conditional strategic lines, **not** a match-win or in-game execution probability.
