# Controlled execution for directly declared copy attacks

## Question

Can the typed outer controls be executed while preserving the existing nested
copy kernel and its current safety boundary?

Yes, for a directly declared copy attack.

Implementation: `tools/attack_copy_controlled_execution.py`  
Regression: `results/attack_copy_controlled_execution/reproduce.py`

## Guarded compilation

The print-specific compiler now keeps two separate executable surfaces.

An ordinary copy attack still exposes `definition`. A controlled copy attack
continues to expose `definition=None`, preserving the old refusal behavior for
callers that do not understand its condition. It additionally exposes:

- `guarded_definition`, containing the selector and ordinary attack metadata;
- `outer_control`, containing the typed declaration or body gate.

This makes condition bypass an explicit opt-in through the controlled executor.

## Direct declaration behavior

`resolve_declared_compiled_copy_attack()` evaluates the typed control before
entering the existing copy kernel.

**Nightcap:** with exactly two opponent Prize cards remaining, execution
proceeds normally. With another Prize count, the result is
`declaration_illegal`; no attack resolution occurs and attack history is not
changed.

**Skill Thief:** with an empty hand, execution reaches the selected copied
body. With a nonempty hand, the attack still resolves while its conditional
copy branch is suppressed. The outer Skill Thief attack becomes the player's
last declared attack.

**Assist:** heads reaches the selected copied body. Tails resolves the outer
attack without a copied body. If no coin outcome is supplied, the executor
returns `random_outcome_required` rather than choosing an outcome internally.

## Why this representation helps

Declaration legality and attack-body control now have different state
transitions:

- failed declaration leaves the match before attack resolution;
- a failed body gate still consumes the declared attack and updates attack
  history;
- stochastic body gates expose a branch point to the caller.

That distinction matters for turn-ending behavior, opponent-last-attack copy
effects, and any future policy model that assigns value to the two coin
branches.

## Limits

The adapter intentionally owns only the attack that was directly declared. It
does not yet decide whether a declaration-stage condition from a selected
attack should be reapplied when that attack is reached only as a copied body.
That boundary needs separate rules validation.

The adapter also receives hand size, Prize count, and coin outcome as explicit
inputs. Those facts are not yet promoted into the minimal copy-kernel state.
