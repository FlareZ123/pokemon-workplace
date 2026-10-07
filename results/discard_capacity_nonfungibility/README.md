# Pokémon TCG joint discard state after an earlier choice

This result concerns the Pokémon Trading Card Game discard mechanic.

The regression in `reproduce.py` starts from a hand with three abstract TCG resources A, B, and C. Each can be chosen alone for a discard effect. The strategic rule requires at least one of A or B to remain, represented by `discard(A) + discard(B) <= 1`.

The initial maximum acceptable discard count is 2.

After choosing A for the first one-resource discard, B and C remain and the later maximum is still 2. After choosing C first, A and B remain and the later maximum is 1.

| First TCG resource chosen | Later maximum | Later two-resource discard legal? |
| --- | ---: | --- |
| A | 2 | yes |
| C | 1 | no |

The two branches begin with the same scalar value and consume the same amount. Their later states differ because the strategic relation among the remaining TCG resources differs.

This bounds the use of `temporal_resource_replenishment/`. Its integer-resource solver is exact for fungible resource dimensions. Strategic discardability can require an exact hand witness followed by policy re-evaluation before projecting the next scalar capacity.

Related work:

- `joint_discard_constraints/` adds cross-class selection rules.
- `discard_cost_witness/` preserves exact TCG hand selections.
- `sequential_trainer_replenishment/` executes the Secret Box into Guzma & Hala hand transition.

A useful future planner interface should distinguish fungible resources from identity-sensitive TCG hand resources that require reprojection after exact execution.
