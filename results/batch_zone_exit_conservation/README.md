# Atomic batch zone-exit conservation

## Question

How should the conserved board model remove several Pokémon from one player's
side in a single card effect?

The target-geometry catalog contains direct effects whose physical target is a
set rather than one Pokémon. Representative legal witnesses include:

- Virizion-GX `sm8-34`, which can put any number of your Pokémon in play and
  all attached cards into your hand;
- Togepi & Cleffa & Igglybuff-GX `sm12-143`, whose extra-Energy branch can
  shuffle all opposing Benched Pokémon and attached cards into the deck;
- Shiftry `sv5-5`, which chooses three opposing Benched Pokémon and shuffles
  the other opposing Benched Pokémon and their attached cards into the deck.

Implementation: `tools/batch_zone_exit_conservation.py`  
Regression: `results/batch_zone_exit_conservation/reproduce.py`

## Atomic transition

`leave_play_batch_before_promotion()` accepts a resolved set of Pokémon object
IDs and applies one shared destination pair to the set.

The transition:

1. validates every selected board object before mutation;
2. removes the whole selected set from the board simultaneously;
3. routes every physical Pokémon card in every selected evolution stack;
4. routes every attached physical card;
5. preserves every unselected board object;
6. returns a `PromotionPendingState` so a selected Active does not force an
   early replacement choice;
7. checks physical-card conservation.

The selected IDs are treated as a set for legality while output order follows
board order for deterministic reproduction.

## Why sequential single-object exits are unsafe

Suppose Virizion-GX returns the Active Pokémon plus several Benched Pokémon.

A loop that calls the stable single-object transition repeatedly must decide a
new Active as soon as it removes the old Active. A later selected Benched Pokémon
could then remove that newly promoted object even though the card effect chose
its target set before the batch resolved.

The batch primitive avoids that invented intermediate decision.

All selected Pokémon leave first. Promotion, when required, occurs only from the
surviving set after the entire batch has been applied.

## Variable-cardinality effects

The batch API accepts an empty tuple.

This is intentional. An attack effect using `any number` can legally resolve
with zero selected targets under the rulebook's `any number` terminology.

The physical layer therefore treats the empty batch as an identity transition.
Whether a Trainer card or Ability could be used when zero selection would leave
the game state unchanged remains an upstream playability rule.

## Regression

The main regression starts with:

- an evolved Tarountula -> Spidops Active;
- a physical Grass Energy attached to the Active;
- three Benched Basic Pokémon.

A Virizion-GX-style hand return selects the Active and two Benched Pokémon.

The regression proves that:

- both physical cards in the evolved Active stack reach hand;
- the attached Energy reaches hand;
- both selected Benched Pokémon reach hand;
- the one unselected Bench survivor remains bound in play;
- no Active is invented during the batch;
- only the actual survivor is a later promotion candidate;
- promotion reconstructs an ordinary stable board;
- total physical cards remain conserved.

A second regression removes two Benched Pokémon to deck while preserving the
existing Active.

The suite also covers:

- an empty batch;
- duplicate selection rejection;
- unknown board-object rejection.

## Relationship to target geometry

This transition supplies the physical execution layer for several geometry
families in `pokemon_zone_exit_target_geometry`.

The compiler still has to determine the resolved target set.

Examples:

- `own_any_number` can map directly to a selected subset;
- `opponent_bench_all` maps to the opponent's complete Bench set;
- `opponent_bench_all_except_one` requires the complement of an earlier
  survivor selection.

The batch layer deliberately receives those choices after target semantics have
already been resolved.

## Scope

All objects in one batch currently share one Pokémon destination and one
attachment destination.

Cross-player batches remain a separate composition layer because each player's
promotion state and choice order are independently visible.

Replacement/redirection effects can also require per-object destinations. Those
belong in a later routing layer rather than in this minimal atomic primitive.

## Validation

Run:

`python results/batch_zone_exit_conservation/reproduce.py`
