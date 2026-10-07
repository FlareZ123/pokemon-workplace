# agent36: canonical turn-budget ownership is green

New result: `results/canonical_turn_budget_owner/`  
New adapter: `tools/canonical_turn_budget_owner.py`

I advanced the staged turn-budget migration into `UnifiedState` itself. An explicit `UnifiedState.turn_budget` is now authoritative; legacy flags are projected only when no canonical budget exists.

The decisive regression is Dual Brains:
- one Supporter already used;
- canonical limit is 2;
- legacy `BenchState.supporter_used` is true;
- Gladion still legally consumes the second Supporter because the integer budget owns quota state.

Live quota suppression/restoration preserves usage history while changing the current limit. Manual Energy, Stadium, and current-turn boundary checks were migrated to the same owner.

A composite Retreat adapter also routes exact board-object Retreat execution through the canonical budget. A synthetic two-Retreat quota succeeds twice despite the legacy board boolean being true after the first; ordinary base quota still stops after one.

Green validation:
- canonical owner: 37570878627
- unified state: 37570896991
- legacy turn-budget bridge: 37570781020

Synthesis is indexed in `results/README.md`. Remaining migration debt is specialized kernels that still make legality decisions from their own booleans.
