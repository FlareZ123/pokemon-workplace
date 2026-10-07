# Turn scheduling with canonical UnifiedState budgets

## Question

Once `UnifiedState.turn_budget` is the authoritative per-turn resource, can extra-turn scheduling stop owning a second copy of each player's action budget?

Yes. This result separates turn-order metadata from action-budget state.

Implementation: `tools/canonical_turn_sequence_owner.py`  
Regression: `results/canonical_turn_sequence_owner/reproduce.py`

## Representation

`TurnScheduleState` stores only:

- current player;
- other player;
- whether an extra turn is queued;
- whether Pokémon Checkup is skipped before that queued turn.

It contains no `budget` or `other_budget` fields.

The current and non-current players are each represented by a `UnifiedState` whose explicit `turn_budget` is authoritative. Closing a turn consumes `ATTACK` or `END_TURN` through that canonical state. Advancing the schedule resets only the budget of the player whose new turn begins.

## Extra-turn witness

Player A starts with a two-Supporter limit representing a Dual-Brains-like quota and spends:

- one Supporter;
- one Stadium play;
- one manual Energy attachment;
- one Retreat.

Player B separately has an ordinary one-Supporter limit and a spent Supporter.

A then closes the turn with an extra-turn attack whose wording skips Pokémon Checkup. On advancement:

- A remains the current player;
- A's ordinary action usage resets;
- A's two-Supporter limit is preserved;
- B's previously spent budget remains untouched because B has not started a new turn;
- Pokémon Checkup is skipped.

After A closes the extra turn normally, B becomes current. B's own limit remains one and B's usage resets for the new turn. When play later returns to A, A's two-Supporter limit returns with fresh usage.

This proves the turn scheduler does not need to duplicate action-budget state to preserve player-specific quota effects.

## Adversarial compatibility check

Before A closes the first turn, the regression deliberately makes A's legacy Supporter, Stadium, and manual-attachment booleans stale. The canonical budget still determines the close/reset behavior. This keeps the ownership contract consistent with `results/canonical_turn_budget_owner/`.

## Architectural implication

Turn order and action bandwidth are distinct state axes.

A composed planner can now use:

`TurnScheduleState + current UnifiedState + other UnifiedState`

without a second authoritative `TurnActionBudget` inside the scheduling layer. Extra turns reset the same player's canonical budget; ordinary handoffs reset the incoming player's own canonical budget.

The older `TurnSequenceState` remains available as a standalone compatibility kernel. This result supplies the migration path for composed planners.

## Remaining boundary

This adapter does not yet derive quota grants from live board objects. If a two-Supporter effect appears or disappears through Ability suppression or board movement, the canonical budget still needs an upstream quota-derivation step before the next legality decision.
