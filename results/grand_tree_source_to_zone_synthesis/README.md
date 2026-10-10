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

## Further cross-layer evidence

**Stadium use resets across actual turn boundaries.** The existing
per-in-play-instance model formerly kept its use history indefinitely.
`begin_stadium_turn` now explicitly refreshes that history only when the
turn scheduler advances to a new actor turn. The same Grand Tree can
therefore be used once by player A, then once by player B on the
subsequent turn, and again by A on a later turn, without replacement.
Evidence: [turn-scope regression](../stadium_effect_turn_scope/README.md),
[passing CI](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38057916123).

**Effect placement followed by Stadium activation is reachable in a
controlled line.** Gothitelle `xy3-41` can use Teleport Room to put
Grand Tree from the discard pile into play, even after the player has
spent the ordinary Stadium-play allowance. The just-entered Grand Tree
can then activate to evolve an otherwise eligible Basic. The adapter
projects one authoritative physical Stadium-entry state into an
ephemeral effect-source view, preserving exact Stadium identity and
both usage counters. Evidence:
[Teleport Room bridge](../teleport_grand_tree_bridge/README.md),
[passing CI](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38058117566).

**Balanced stage allocations optimize one static joint-search objective.**
For a fixed total `a+b` of Stage 1 and Stage 2 copies, the chance
that both stages are searchable from deck at initial setup is
maximized by a split as close to equal as feasible. This follows from
discrete convexity of `q(k)=C(12,k)/C(59,k)` and is verified by exact
finite-population calculations. At four stage-copy slots, 2/2 gives
92.3940% joint access versus 79.0930% for 1/3. This is an
optimization of one declared static objective, not a proof that
balanced lines always make the best competitive deck.
Evidence: [slot allocation theorem](../grand_tree_slot_allocation/README.md),
[passing CI](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38058254348).

## A stronger conditioning model

The initial setup odds above condition on one *particular* target Basic
already occupying an opening-hand slot. With several target Basics in
the deck, the more natural condition `at least one of r target Basics
in the opening hand` induces a different distribution over the other
cards. The [target-Basic conditioning result](../grand_tree_target_basic_conditioning/README.md)
gives an exact formula and independently enumerates all four-category
hand/Prize/deck allocations; its [CI](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38058424608)
passes. With one Stage 1 and one Stage 2 copy, the initial full-chain
probability is 63.1794% for r=1 and 62.8298% for r=4.

The balanced evolution-copy allocation theorem remains valid under
this more realistic condition. The reason is that the probability
`q_r(k)` of all k copies being outside the deck is a mixture over
conditional target-Basic placements of discrete-convex missing-deck
probability sequences. The mixture remains convex. Thus at a fixed
evolution-slot total the most balanced feasible Stage 1/Stage 2 split
still maximizes joint deck searchability. Independent exact-rational
validation and [CI](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38058551679)
appear in [conditional slot allocation](../grand_tree_slot_allocation_conditioned/README.md).

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
