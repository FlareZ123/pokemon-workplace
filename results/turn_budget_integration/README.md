# Legacy split-state turn-budget bridge

## Question

Can the repository's existing per-turn usage flags be projected into the new shared `TurnActionBudget` without first rewriting the hot shared kernels?

Yes. This result adds a narrow compatibility bridge between the current unified/Bench state, the board-object state, and the generic turn budget.

Implementation: `tools/legacy_turn_budget_bridge.py`  
Regression: `results/turn_budget_integration/reproduce.py`

## Existing split

The current kernels place one logical turn resource across several owners:

- `BenchState.supporter_used` stores ordinary Supporter usage;
- `BenchState.turn_ended` stores the unified scaffold's turn-closed boundary;
- `UnifiedState.stadium_used` stores Stadium-play usage;
- `UnifiedState.manual_attachment_used` stores the normal Energy attachment;
- `BoardState.retreat_used` stores ordinary Retreat usage.

That split reflects the historical growth of specialized kernels. It is risky when a planner composes them, because a transition can consult one state owner and forget another.

The turn-end bug recorded in [../turn_action_budget/](../turn_action_budget/) is one concrete example.

## Bridge

`project_composite_turn_budget(unified, board)` reads all five legacy fields and returns one immutable `TurnActionBudget`.

The reverse helpers synchronize a chosen budget back into legacy state:

- `apply_budget_to_unified(...)` writes Supporter, turn-end, Stadium, and manual-attachment usage;
- `apply_budget_to_board(...)` writes Retreat usage.

These reverse helpers are migration support. The intended long-term direction is for one composite state to own the budget directly.

## Regression

The reproducer verifies:

1. fresh unified + board state projects to a fresh budget;
2. individually spent Supporter, Stadium, manual attachment, and Retreat flags all appear in the shared projection;
3. those four channels are exhausted independently while attacking remains available;
4. a legacy ended-turn flag makes the projected budget reject every ordinary action;
5. applying a target budget to both legacy kernels and projecting it back is an exact round trip;
6. a fresh next-turn budget clears every legacy usage flag through the same synchronization path.

## Architectural implication

The bridge makes the duplication measurable. Five booleans spread across three state layers can be represented by one value with one transition contract.

A safe migration sequence is:

1. project legacy state into `TurnActionBudget`;
2. make composed planners consume/query that budget;
3. move ownership of the budget into the canonical composite state;
4. remove redundant legacy booleans only after their callers have migrated.

This approach keeps current regressions stable while reducing the chance that one specialized subsystem silently grants an already-spent action.
