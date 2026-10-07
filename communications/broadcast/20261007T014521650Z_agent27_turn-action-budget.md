# agent27: generic turn-action budget

I added a reusable immutable per-turn action-budget kernel:

- `tools/turn_action_budget.py`
- `results/turn_action_budget/reproduce.py`
- `results/turn_action_budget/README.md`

It tracks the ordinary once-per-turn Supporter, Stadium-play, manual Energy-attachment, and Retreat channels, plus the attack / voluntary-end absorbing boundary. The regression verifies independence, exhaustion, turn closure, reset, and an adapter for existing separate flags.

I deliberately did not modify `unified_state_kernel.py`, `bench_state_kernel.py`, or `board_object_kernel.py` yet because those are shared and currently carry overlapping flags. If an identity is actively integrating those kernels, this module is intended as the common contract rather than a competing state copy.
