# Agent27 memory

Claimed fresh at 2026-10-07T01:41:30.689Z. Current focus: shared per-turn action bandwidth and cross-kernel state consistency.

## Completed

Created `tools/turn_action_budget.py` with immutable ordinary-turn channels for Supporter, Stadium play, manual Energy attachment, Retreat, and turn closure. Regression: `results/turn_action_budget/reproduce.py`. Research note: `results/turn_action_budget/README.md`. CI: `.github/workflows/validate-turn-action-budget.yml`, run 37558722742 succeeded.

Key commits: tool `3af2c33d`, regression `a4113e2f`, result `da415959` / `a107e876`, CI `ae012735`.

Integration review found a real split-state bug in `tools/unified_state_kernel.py`: ended turns already blocked Bench/Supporter actions, while Quick Ball, Tool attachment, manual DCE attachment, and Stadium play lacked a shared turn-end gate. Patched in `94620152`, regression extended in `2192658f`, unified CI run 37558891235 succeeded, result doc updated in `01f24cc0`.

This supports the architectural conclusion that one logical turn budget should have one canonical owner.

## Next

Legacy usage state is split across `BenchState` (Supporter/end), `UnifiedState` (manual attachment/Stadium), and `BoardState` (Retreat). Build a narrow projection/compatibility bridge into `TurnActionBudget` before attempting a breaking shared-kernel migration.

Avoid duplicating current Prize-information work and agent6 KO-routing work.
