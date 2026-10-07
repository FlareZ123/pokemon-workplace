# Typed Special Conditions inside board-object state

## Question

Can the richer Special Condition payload model be composed with the existing
per-Pokémon board object without breaking movement, retreat, and evolution
semantics?

Implementation: `tools/conditioned_board_state.py`  
Regression: `results/conditioned_board_state/reproduce.py`

## Representation

The existing board kernel remains the mechanical authority for position,
attachments, damage, retreat payment, and movement. A `ConditionedBoardState`
adds one `SpecialConditionState` per board object.

The adapter deliberately keeps the existing
`BoardPokemon.special_conditions: frozenset[str]` field as a compatibility
projection. Validation requires that projection to equal the names represented
by the typed state. A stale dual representation is rejected immediately.

This is an incremental migration path. Existing code that only asks whether the
Active is Asleep or Paralyzed can continue reading the name projection, while
new Checkup and irregular-condition logic can read the typed payload.

## Finding 1: synchronization is enforceable

The regression starts with a Severe Poison payload that places 4 counters and a
legacy projection of `{"Poisoned"}`.

A deliberately stale state pairs that same board object with an empty typed
condition state. Validation rejects it. This prevents the compatibility layer
from becoming two drifting authorities.

## Finding 2: movement can clear the rich payload atomically

The wrapper delegates the physical position change to the existing board kernel
and clears the outgoing Active's typed condition state in the same transition.

For effect-based switching, the regression confirms that both:

- the legacy `{"Poisoned"}` projection; and
- the richer 4-counter Severe Poison payload

are gone after the outgoing Active moves to the Bench.

The retreat wrapper preserves the existing physical Energy-card payment and
performs the same synchronized condition clearing.

## Finding 3: evolution can preserve board topology while dropping condition state

The evolution wrapper delegates card-identity and attachment preservation to the
existing board transition, then clears the typed Special Condition state for the
same Pokémon object.

This keeps the board object's identity stable while removing condition-local
payload that should no longer survive the represented evolution transition.

## Finding 4: name-only history cannot be losslessly upgraded

`lift_legacy_board_as_regular()` is intentionally named as an assumption.

If an old state stores only `{"Poisoned"}`, there is no information left that
distinguishes ordinary Poisoned from a 4-counter Severe Poison instance. The
adapter therefore reconstructs the ordinary 1-counter version and documents the
operation as lossy.

A simulator should materialize typed condition state when the condition is
applied rather than attempting to infer its payload later.

## Architectural consequence

A gradual migration does not require a destructive rewrite of
`board_object_kernel.py`.

The safe path is:

1. treat typed condition state as the lossless authority for condition payload;
2. maintain the old name set as a validated compatibility projection;
3. route condition-mutating transitions through synchronized wrappers;
4. migrate consumers from the name projection to typed queries where payload or
   Checkup timing matters;
5. remove the redundant projection only after downstream code no longer needs
   it.

This preserves compatibility while preventing irregular-condition information
from disappearing during board transitions.

## Validation

The regression checks:

- a Severe Poison payload survives initial board materialization;
- stale typed/legacy disagreement is rejected;
- effect-based switching clears both representations;
- normal retreat clears both representations while returning the selected
  physical Energy payment;
- evolution clears both representations;
- a legacy name-only lift reconstructs ordinary Poison and demonstrates the
  irreversible information loss.

## Limits

The adapter mirrors the current board kernel's represented movement and
evolution behavior. It does not independently settle every Special Condition
basic-rule question.

The compatibility projection is intentionally redundant. Every mutation must go
through a synchronized adapter while both representations exist.

Knock Out and Pokémon Checkup resolution remain separate kernels. The next
integration target is the Checkup effect-order authority and trigger-deferral
layer.
