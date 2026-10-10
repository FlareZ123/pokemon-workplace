# Grand Tree: one effect, two evolutions, three card zones

## Integrated finding

Grand Tree (`sv7-136`) demonstrates three separate correctness constraints for
a Pokémon TCG Expanded deck or action-search optimizer:

1. **Source activation:** The Stadium's already-in-play voluntary effect has
   its own per-in-play-instance use history. This must be separated from
   the ordinary quota for playing a Stadium card from hand.
2. **Ordered conditional resolution:** A legal Basic -> Stage 1 evolution
   may continue to Stage 2 in the same Grand Tree effect. The continuation
   is a distinct evolution transition inside one source activation, and
   is expressly permitted despite the Stage 1 having just evolved.
3. **Physical availability:** Both evolution cards are searched from the
   deck. A Stage 2 in the Prize cards prevents that copy from being selected,
   but the Stage 1-only branch remains legal if Stage 1 is in the deck.
   A Stage 1 absent from deck prevents that particular chain from starting.

A model that collapses all three into one nominal `evolve` edge can be
both overoptimistic (assuming Prized cards are accessible) and
overrestrictive (charging two Stadium uses, or applying the freshly
evolved Stage 1's normal waiting rule to the permitted continuation).

## Implementation and validation trail

| Research layer | Executable evidence | Validated CI |
| --- | --- | --- |
| Generic C-12 source and Stadium instance quota correction | [Source gate](../effect_evolution_source_gate/README.md) | [38056866914](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38056866914) |
| One Grand Tree effect containing Stage 1 + optional Stage 2 | [Two-stage effect](../grand_tree_chain_execution/README.md) | [38057106068](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38057106068) |
| Physical deck-to-board instance binding and Prized Stage 2 fallback | [Materialized chain](../grand_tree_materialized_chain/README.md) | [38057279350](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38057279350) |
| Exact initial hand/Prize/deck partition probability | [Zone probability](../grand_tree_initial_zone_probability/README.md) | [38057596286](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38057596286) |

These findings build on earlier
[effect-evolution timing](../effect_evolution_timing/README.md) and
[effect-evolution physical execution](../effect_evolution_execution/README.md),
and reuse [Stadium instance usage](../stadium_effect_instance_usage/README.md).

## Exact baseline numbers and what they mean

Condition on **one specified target Basic** being in the opening seven-card
hand, with one copy of each required evolution stage among the other 59
cards. The remaining 59 are divided randomly into six other hand slots,
six Prize slots, and 47 deck positions. Before any further card movement:

- **63.1794%:** both Stage 1 and Stage 2 remain searchable in deck;
- **16.4816%:** Stage 1 is searchable, Stage 2 is outside the deck;
- **20.3390%:** Stage 1 is unavailable from deck.

For two copies of each stage, the first figure becomes **92.3940%**.
The formulas and exhaustive hypergeometric category enumeration are
published in the probability result.

This baseline is *not* an observed tournament statistic, a realistic
first-turn Grand Tree activation probability, or a complete setup estimate.
Grand Tree cannot evolve a Basic during its player's first turn, and card
draws/searches between setup and later activation alter these zones.

## Proposed next integration

A general planner should store:

- a single canonical turn action budget;
- separate Stadium card-in-play identity and voluntary effect-use history;
- source-specific permission gates and card-specific target timing;
- the evolving Pokémon's persistent physical object and evolution stack;
- selected Stage 1 and optional Stage 2 deck instances;
- public/private zone beliefs, with K0 -> K1 information update after
  first complete deck search;
- ordered resolution and one final commit only when candidate actions are
  legal.

The code already provides the deterministic core for this one card.
It does not yet integrate actual prize observations or a policy that
adaptively selects between the Stage 1-only and Stage 2 continuation after
observing searchable cards.

## Confidence and constraints

The four CI jobs pass the published deterministic regressions. The
source/action and identity claims follow rulebook B-04, C-12, Grand Tree's
literal card text, and the repository's identity-conservation kernels.
The zone probabilities are exact for their conditioned finite population.
Full-game strategic superiority and metagame implications remain open.
