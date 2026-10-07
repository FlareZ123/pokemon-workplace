# agent36: turn scheduling now uses UnifiedState-owned budgets

New result: `results/canonical_turn_sequence_owner/`  
New adapter: `tools/canonical_turn_sequence_owner.py`

`TurnScheduleState` now carries only turn-order metadata. Current and other players retain their own canonical `UnifiedState.turn_budget` values, so the scheduler no longer needs a second authoritative budget pair.

The regression spends A's ordinary channels under a two-Supporter limit, gives B a separate one-Supporter history, then resolves an extra turn. A's usage resets while its limit stays 2; B's history remains untouched until B starts a turn. Ordinary handoff later resets only B, and returning to A restores A's own limit.

Stale legacy usage booleans do not affect scheduling.

Green CI:
- canonical sequence: 37571248006
- legacy sequence compatibility: 37571278662

Indexed in `results/README.md`.
