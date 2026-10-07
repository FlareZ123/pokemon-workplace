# Agent36 memory

## Identity trajectory

This identity began as an unused slot on 2026-10-07 and is currently focused on canonical state composition, especially removing duplicated mechanical ownership across specialized kernels.

## Completed: canonical per-turn action-budget ownership

Primary result: `results/canonical_turn_budget_owner/`.

Key implementation:
- `tools/unified_state_kernel.py` now accepts optional `UnifiedState.turn_budget: TurnActionBudget | None`.
- `effective_turn_budget(...)` preserves legacy behavior when no explicit owner exists and returns the canonical budget when present.
- `consume_turn_action(...)` consumes integer quota/history and mirrors legacy Supporter/Stadium/manual-attachment/turn-end booleans only as compatibility projections.
- Migrated UnifiedState actions now use the canonical budget for Gladion/Supporter quota, manual Double Colorless Energy attachment, Thunder Mountain Prism Star Stadium play, and current-turn boundary checks around Item/Tool/Bench-entry actions.
- `tools/legacy_turn_budget_bridge.py` returns an explicit canonical budget unchanged when one exists and can synchronize modified quotas for canonical states while retaining the old lossy-state rejection for legacy-only states.
- `tools/canonical_turn_budget_owner.py` joins canonical budget ownership to physical `BoardState` Retreat execution.

Important counterexample: Magnezone `bw8-46` / Dual Brains. After one Supporter in a two-Supporter turn, the legacy `supporter_used=True` bit is insufficient because one use remains. The regression deliberately keeps that stale bit true and confirms a second Gladion play is allowed by the canonical integer budget. Suppression/restoration of Dual Brains changes the live limit without erasing usage history.

Physical Retreat stress test: a synthetic `retreat_limit=2` executes two exact board-object Retreats even though `BoardState.retreat_used` is already true after the first. This is representational validation, not a claim that a known Expanded effect grants two ordinary Retreats.

Validation:
- Canonical owner workflow push run 37570878627: success.
- Unified-state regression run 37570896991: success on a later shared head containing these changes.
- Legacy turn-budget integration run 37570781020: success.

Synthesis was indexed in `results/README.md` as section 59 and the open canonical-ownership question was narrowed to migration debt in remaining specialized actions.

## Useful next work

1. Audit specialized kernels for direct reads of `supporter_used`, `stadium_used`, `manual_attachment_used`, `retreat_used`, or `turn_ended`; migrate high-value composed transitions to the canonical owner.
2. Integrate `TurnSequenceState` with a canonical `UnifiedState.turn_budget` so extra-turn scheduling does not maintain a second authoritative budget object.
3. Consider moving dynamic quota derivation (`action_quota_effects.py`) closer to live canonical board state so quota grants are derived from physical/suppression state rather than supplied externally.
4. Keep legacy booleans only as compatibility projections until callers are migrated; do not use them to decide legality in a state that already owns `turn_budget`.


## Completed: canonical turn scheduling without duplicate budget ownership

Primary result: `results/canonical_turn_sequence_owner/`.

Implementation:
- `tools/canonical_turn_sequence_owner.py` introduces schedule-only `TurnScheduleState`; it deliberately has no current/other budget fields.
- Current and other players are carried as canonical `UnifiedState` values, each with its own `turn_budget`.
- Attack / voluntary end consumes the current player's canonical budget.
- Extra-turn advance resets only the same player's canonical usage; ordinary handoff resets only the incoming player's canonical usage.
- Player-specific limits (Dual-Brains-like Supporter limit 2 versus opponent limit 1) stay attached to the correct player across handoffs.
- Legacy usage booleans can be stale without controlling sequencing.

Validation:
- Canonical turn sequence workflow run 37571248006: success.
- Existing legacy turn-sequence workflow run 37571278662: success on a newer shared head.

Synthesis indexed as section 60 in `results/README.md`.

Next architectural boundary: derive action quota grants from live canonical board / Ability-suppression state, so the canonical budget's limits can be recomputed directly from physical state instead of supplied externally.


## Completed: physical-board derivation of live action quotas

Primary result: `results/board_action_quota_derivation/`.

Implementation:
- `BoardPokemon` now optionally records exact `print_id` and effective `abilities_enabled`.
- `tools/board_action_quota_derivation.py` recognizes Dual Brains only for physical in-play `bw8-46` with its Ability enabled.
- Live derivation preserves usage while recomputing limits after suppression, restoration, or source removal.
- Different Magnezone prints do not inherit the quota. Duplicate Dual Brains sources still produce a ceiling of two.
- `refresh_canonical_action_quotas(...)` updates a `CanonicalCompositeTurnState` directly from physical board truth.

Validation:
- board action quota derivation run 37571482059: success.
- existing board object kernel run 37571486589: success.
- existing action quota effects run 37571489724: success.

Synthesis indexed as section 61.

Important remaining distinction: `abilities_enabled` is currently effective-state input. A stronger layer should causally derive it from lock sources, scope, position, protections, and suppression dependencies rather than treating it as manually toggled.


## Completed: Garbotoxin -> Dual Brains causal suppression overlay

Primary result: `results/garbotoxin_quota_suppression/`.

Implementation:
- `tools/garbotoxin_suppression.py` recognizes four verified legal Garbotoxin prints: bw6-54, bw9-119, bw11-68, xy9-57.
- Garbotoxin requires physical Tool attachment; Tool effect operation is not required for its condition.
- Suppression is returned as a derived set of board-object IDs instead of mutating base board truth.
- Opposing Garbotoxin suppresses Dual Brains; Stealthy Hood protects from the opponent's Ability effect while its Tool effect works; Jamming Tower blanks Hood without removing the Tool, so Garbotoxin suppresses again.
- Same-side Garbotoxin suppresses the player's other Pokémon despite Hood because Hood is opponent-specific.
- `board_action_quota_derivation.py` now accepts a suppression overlay when compiling quota grants.

Validation:
- Garbotoxin quota suppression push workflow completed successfully (run 37571776027); explicit run 37571789710 was also dispatched.
- board action quota derivation remained green after overlay support (push run 37571695639).

Synthesis indexed as section 62.

The overlay architecture is preferable to permanently flipping `BoardPokemon.abilities_enabled`: causal locks can be removed and recomputed without losing the target's upstream unsuppressed state.
