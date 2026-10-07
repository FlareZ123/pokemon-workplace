# Causal Ability locks feed the canonical turn-budget owner

## Question

How should effective lock history affect action quotas without creating another
budget owner?

Through a one-way adapter from resolved causal suppression into the existing
canonical quota derivation.

## Adapter

`tools/ability_lock_canonical_budget.py` accepts:

- a `CanonicalCompositeTurnState`, whose `UnifiedState.turn_budget` remains
  the authoritative action budget;
- a resolved `AbilityLockCausalState`;
- which side's board the canonical composite represents.

It selects that side's effective suppression overlay and calls the existing
`refresh_canonical_action_quotas` function.

The adapter owns no physical board copy and no quota copy.

If the causal lock state is unresolved, the adapter returns `None` instead of
publishing a guessed downstream budget.

## Regression

The physical player board contains Active Empoleon V and Bench Magnezone
`bw8-46` with Dual Brains. The opponent has Active Wobbuffet.

A fresh canonical budget begins with Supporter-play limit 1.

When setup precedence belongs to the Empoleon side, the causal lock state keeps
Magnezone unsuppressed. Refreshing through the adapter writes Supporter limit 2
into the same canonical `UnifiedState.turn_budget`.

When setup precedence belongs to the Wobbuffet side, Bide Barricade suppresses
Magnezone and the canonical budget remains at Supporter limit 1.

An explicitly unresolved causal lock state produces no canonical refresh.

## Ownership chain

The resulting ownership flow is:

`physical BoardState`

`-> AbilityLockCausalState`

`-> effective suppressed object IDs`

`-> board-derived quota grants`

`-> UnifiedState.turn_budget`

Only the final object owns action usage and limits. Earlier layers supply
mechanical evidence for deriving those limits.

Regression: `results/ability_lock_canonical_budget/reproduce.py`.
