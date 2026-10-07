# Attack-applied source-scoped restriction materialization

## Question

Attack profiles describe when a restriction could be applied. This result resolves the attack's actual gate outcome into either one concrete restriction or no pending effect.

Implementation: `tools/attack_source_scoped_restrictions.py`

Regression: `results/attack_source_scoped_restrictions/reproduce.py`

## Gate resolution

The materializer supports all 77 attack-applied profiles in the audited family.

Seventy-one unconditional profiles produce their compiled restriction directly.

Three heads-only profiles require an explicit coin result. Heads creates the restriction and tails creates no restriction.

Chi-Yu `me1-31` / Scorching Earth requires an explicit prerequisite outcome. Its restriction exists only when the Stadium-discard dependency succeeded.

Crobat `sv4-112` / Echoing Madness requires the selected lock dimension and resolves to exactly that printed branch.

Vileplume `swsh11-3` / Allergy Storm requires a coin result. The compiler preserves printed branch order so heads resolves to Supporter lock and tails resolves to Item lock.

## Strict outcome ownership

A gated attack cannot be materialized without the outcome it requires.

The materializer also rejects outcome arguments that do not belong to the profile's gate. This keeps coin state, player choice, and prerequisite completion from leaking across unrelated attack semantics.

Continuous Ability profiles are rejected by this module and remain owned by the continuous evaluator.

## Finding

Attack resolution should create a concrete temporal restriction only after every lock-relevant gate has resolved.

This gives the downstream turn-window layer a simple contract. It receives either one fully concrete restriction, with exclusive branches already resolved, or no restriction at all.

The temporal layer therefore does not need to interpret attack text, flip coins, or decide whether an earlier prerequisite succeeded.

## Limits

The materializer assumes the attack itself has already executed far enough for the relevant gate to be resolved. It does not check Energy cost, attack legality, attack immunity, or whether an attack was prevented.

The next layer still needs to assign the concrete restriction a turn-relative lifetime and expire it at the correct event boundary.
