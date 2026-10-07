# Canonical per-turn action-budget ownership

## Question

Can the repository move from split per-turn booleans to one authoritative quota state without breaking existing UnifiedState callers?

Yes, for the migrated UnifiedState actions and the physical Retreat seam covered here. The ownership path is additive: legacy-only states still project their old flags into a budget, while a state with an explicit `turn_budget` treats that integer budget as authoritative.

Implementation:

- `tools/unified_state_kernel.py`
- `tools/legacy_turn_budget_bridge.py`
- `tools/canonical_turn_budget_owner.py`

Regression: `results/canonical_turn_budget_owner/reproduce.py`

## Ownership rule

`UnifiedState.turn_budget` is optional for backward compatibility. When absent, `effective_turn_budget(...)` derives the old Supporter, Stadium, manual-Energy, and turn-ended flags exactly as before. Once present, the explicit `TurnActionBudget` is the source of truth.

The migrated actions now query that owner:

- Gladion / Supporter play;
- manual Double Colorless Energy attachment;
- Thunder Mountain Prism Star play;
- Item / Tool / Bench-entry turn-boundary checks.

`consume_turn_action(...)` updates the integer budget and mirrors boolean compatibility fields. Those booleans remain lossy whenever a quota exceeds one, so migrated actions do not use them to decide quota availability.

## Dual Brains counterexample

Magnezone `bw8-46` / Dual Brains gives the concrete reason this matters. After one Supporter in a two-Supporter turn:

- `supporter_plays_used == 1`;
- `supporter_play_limit == 2`;
- another Supporter is still legal;
- the old `BenchState.supporter_used` boolean is already true.

The regression places Gladion in hand in exactly that state, deliberately leaves the legacy boolean true, and confirms `play_gladion(...)` consumes the second Supporter from the canonical budget. Suppressing Dual Brains then recomputes the live limit from 2 to 1 without erasing the one already-used Supporter; restoring the grant reopens the second use.

This is direct evidence that a boolean can remain a compatibility observation but cannot remain the authoritative rule state.

## Stale-flag adversarial checks

Two opposite stale-state witnesses are included:

1. the canonical budget is fresh while the legacy manual-attachment or Stadium boolean says the action was already used; the migrated physical action still succeeds and consumes the canonical quota;
2. the canonical budget says the turn has ended while the legacy BenchState bit is false; a Quick Ball transition is still rejected.

These are intentional adversarial states. They prove which owner actually controls execution.

## Physical Retreat bridge

Retreat still lives in `BoardState`, whose `retreat_used` field is a boolean. `CanonicalCompositeTurnState` joins the physical board transition to the canonical budget:

1. check `TurnAction.RETREAT` against the integer budget;
2. execute the exact physical Energy discard and Active/Bench swap through the existing board kernel;
3. consume one Retreat in the canonical budget;
4. mirror only whether any Retreat has been used back to `BoardState.retreat_used`.

A synthetic `retreat_limit=2` stress test performs two physical Retreats even though the board's compatibility bit is already true after the first. This is a representation test, not a claim that a currently identified Expanded card grants two ordinary Retreats. Under the ordinary base limit of one, the second Retreat remains illegal.

## What this closes

The previous bridge established a staged migration path but had no canonical owner inside UnifiedState and could not round-trip modified quotas through legacy booleans. This result executes the next step of that migration:

- canonical integer usage and limits can now live in UnifiedState;
- migrated UnifiedState actions consume that owner;
- physical Retreat can consume the same owner through a composite adapter;
- the old bridge returns the explicit canonical budget when one exists;
- canonical states can synchronize modified quotas without collapsing them into booleans.

## Remaining boundary

Specialized kernels that still inspect their own legacy action booleans directly remain migration debt. The safe rule is now explicit: composed policy search should read and consume the canonical `TurnActionBudget`; legacy bits are compatibility projections until each specialized transition is migrated.
