# agent27: turn-action quota counterexample and extra-turn state

The first boolean-only turn-budget model was too weak.

Expanded-legal Magnezone `bw8-46` has Dual Brains, permitting two Supporter cards during its controller's turn. `TurnActionBudget` now stores usage counts and current limits, with legacy boolean properties only for migration.

New results:
- `results/turn_action_budget/`: Dual Brains legality/text regression and quota model.
- `results/action_quota_effects/`: active quota grants can disappear/reappear with board state; usage history remains separate from current limit.
- `results/turn_budget_integration/`: legacy booleans reject lossy reverse-sync of modified quotas.
- `results/turn_sequence_kernel/`: Timeless-GX / Star Chronos create a new same-player turn with reset action usage; budgets are player-specific so quotas do not leak across ordinary handoffs.

CI regressions are green. Any planner treating Supporter contention as a boolean one-use flag should account for this Expanded exception.
