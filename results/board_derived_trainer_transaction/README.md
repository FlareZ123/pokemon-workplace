# Board-derived live-source Trainer transaction gating

## Question

The live-source Trainer adapter previously required callers to construct
`ContinuousRestrictionSource` objects. After board-derived continuous restriction
state exists, can a real Trainer transaction consume canonical boards, causal
Ability-lock state, and temporal attack windows directly?

Implementation: `tools/board_derived_trainer_transaction.py`

Regression: `results/board_derived_trainer_transaction/reproduce.py`

## Composition

The adapter derives continuous sources from the two canonical `BoardState`
objects and a resolved `AbilityLockCausalState`, then delegates to the existing
live-source Trainer transaction wrapper. Temporal attack windows remain a
separate input because they are persistent effects created by earlier attacks
rather than properties of the current source Pokémon.

The established transaction engine still owns discard payment, search output,
zone movement, Supporter budget use, and other Trainer execution mechanics.

## Regression witness

A live Vileplume Irritating Pollen source blocks Secret Box from hand while
leaving Arven legal. An opposing Tool-attached Garbodor suppresses Vileplume,
which reopens Secret Box. Stealthy Hood on Vileplume protects it from the
opposing Garbotoxin and closes Secret Box again. Jamming Tower disables Hood's
protection while leaving the Tool attached, so the recomputed Garbotoxin overlay
suppresses Vileplume and Secret Box becomes executable.

A live Psyduck Headache temporal window still blocks Arven even when Garbotoxin
has removed Vileplume's continuous restriction. This verifies composition
between board-derived continuous state and attack-applied temporal state.

## Finding

A real Trainer action can now travel through the full restriction lifecycle
without caller-authored lock booleans:

`board + causal Ability suppression -> continuous source contexts -> active
restriction aggregation + temporal windows -> source-scoped permission gate ->
Trainer transaction`

The remaining state boundary is intentional. Attack-applied restrictions live
in temporal windows because their source Pokémon may leave play after the effect
was created.
