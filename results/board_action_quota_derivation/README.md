# Physical-board derivation of live action quotas

## Question

Can the canonical turn budget derive Dual Brains directly from the physical in-play Pokémon and current Ability activity instead of receiving a manually constructed quota grant?

Yes, for the exact Expanded-legal Dual Brains source modeled here.

Implementation:

- `tools/board_object_kernel.py`
- `tools/board_action_quota_derivation.py`
- `tools/canonical_turn_budget_owner.py`

Regression: `results/board_action_quota_derivation/reproduce.py`

## Physical facts added to BoardPokemon

`BoardPokemon` now carries two additive fields:

- `print_id`, so same-name Pokémon with different text are distinguishable;
- `abilities_enabled`, an effective-state flag representing whether that object's Abilities currently function.

Both have backward-compatible defaults. Exact print identity is essential because "Magnezone" as a name is insufficient evidence for Dual Brains.

## Derivation

`quota_grants_from_board(...)` scans the current physical objects and emits the existing `DUAL_BRAINS` total-limit grant only for an in-play object with:

- `print_id == "bw8-46"`;
- `abilities_enabled == True`.

`derive_board_action_quotas(...)` then recomputes current limits from the basic-rule ceilings using the existing quota algebra. Usage history is preserved.

`refresh_canonical_action_quotas(...)` applies that derivation directly to a `CanonicalCompositeTurnState`, keeping `UnifiedState.turn_budget` authoritative.

## Dynamic witnesses

The regression checks four live-board changes after one Supporter has already been played:

1. active Dual Brains gives limit 2, so one Supporter remains;
2. suppressing that exact Magnezone's Abilities drops the current limit to 1 while usage remains 1;
3. restoring the Ability raises the current limit back to 2 and reopens the second Supporter;
4. removing the Magnezone from play drops the limit back to 1.

Two copies of the exact print still establish a ceiling of two rather than four, matching the existing total-limit semantics.

A different Magnezone print does not grant extra Supporter bandwidth.

## Architectural implication

The canonical budget no longer needs a caller to tell it that Dual Brains is active when the composed physical board already contains enough information to derive that fact.

The state separation becomes:

- physical board: exact source identity and current Ability effectiveness;
- quota derivation: compile active board effects into current limits;
- canonical turn budget: preserve usage history plus those derived limits;
- play-permission channels: independently decide whether Supporters can be played at all.

This preserves the distinction between Ability suppression, source removal, quota exhaustion, and Supporter lock.

## Limits

`abilities_enabled` is an effective-state result, not yet a full causal model of every Ability-lock interaction. A future lock-resolution layer should derive this per-object value from active lock sources, protections, position requirements, and scope. The result here establishes the downstream quota seam without pretending that all Ability suppression has already been compiled.
