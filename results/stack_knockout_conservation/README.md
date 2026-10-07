# Whole-stack Knock Out conservation

## Question

Can a single state transition discard an evolved Pokémon's complete physical
evolution stack and every attached card while preserving the identity ledger's
card totals?

Implementation: `tools/stack_knockout_conservation.py`  
Regression: `results/stack_knockout_conservation/reproduce.py`

## Representation

This result composes three existing layers:

- `ZoneCountState` for exchangeable card-class multiplicity outside board
  topology;
- `IdentityLedger` for materialized physical card instances and their
  `in_play` / `attached` relations;
- `board_position_state.BoardState` for persistent Pokémon objects, full
  evolution stacks, and generic Energy/Tool attachments.

`StackBoardMaterialState` validates both board relations at once. Every
physical Pokémon card in a stack must match one ledger instance bound to that
Pokémon object, and every board attachment must match one materialized attached
instance.

## Regression

The deterministic regression builds one Active Pokémon object and one Benched
object.

The Active object proceeds through:

1. materialized Bulbasaur in play;
2. materialized Ivysaur added by ordinary evolution;
3. materialized Muscle Band attachment;
4. materialized Double Colorless Energy attachment.

A second Tool play on the same Pokémon is rejected.

The evolved Active is then Knocked Out while the Benched Bidoof is promoted.
The transition:

- removes the persistent Pokémon object;
- moves both Bulbasaur and Ivysaur physical instances from `in_play` to
  discard and dematerializes them;
- moves both Muscle Band and Double Colorless Energy from `attached` to
  discard and dematerializes them;
- keeps the Bidoof physical instance bound to the promoted Pokémon object;
- preserves every card-class total exactly.

A second Knock Out removes the lone Bidoof. The board becomes terminal
(`None`), the Bidoof returns to the exchangeable discard count, and no
board-bound instances remain.

## Finding

A Knocked Out evolved Pokémon is best treated as one board-object disposal
boundary with several conserved physical-card members.

This is stronger than independently deleting:

- a top-card name;
- an attachment Boolean;
- an Energy count;
- or a Bench occupant.

Those independent updates can silently orphan a previous Evolution card or an
attached physical copy.

The identity ledger provides one invariant: before and after the transition,
the total number of copies in each card class is unchanged.

## Relationship to earlier results

- `pokemon_stack_materialization/` establishes the forward
  exchangeable-to-stack boundary.
- `devolution_materialization/` establishes one reverse top-card boundary.
- `board_attachment_conservation/` establishes Tool/attachment conservation
  using the other board-object kernel.
- This result composes full stack disposal and attachment disposal in the
  stack-bearing board representation.

## Limits

This transition models the mechanical disposal step only.

It does not yet model:

- simultaneous Knock Outs;
- effects that trigger before Knocked Out cards are discarded;
- Prize taking;
- promotion ordering when both Active Pokémon are Knocked Out;
- win/loss resolution;
- recovery effects that preserve physical identity after leaving play;
- card-specific replacement effects that redirect discarded cards elsewhere.

Those mechanics should wrap or replace the disposal destination rather than
bypassing the conservation invariant.
