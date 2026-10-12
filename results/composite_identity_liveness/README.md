# Composite identity liveness across physical and belief transitions

## Failure mode

Taking a Prize can move an exact physical card from the pending queue into
hand while an observer-relative belief object still records that exact
`instance_id` as a latent pending identity. The hand is normally an
exchangeable zone, so a release based only on physical-zone state would
silently destroy an identity that the belief layer still owns.

## Contribution

`tools/composite_identity_liveness.py` collects references from exact
deck-top/Prize topology, physical pending-Prize queues, observer pending
beliefs and explicitly supplied effect owners.

Its contract is conservative:

- all included physical snapshots must use the *same current* IdentityLedger;
- beliefs are permitted to lag the physical queue, because that lag is the
  central semantic liveness case;
- repeated identical references can be merged (topology present in both
  a top and a pending state);
- conflicting ownership under the same reference ID is rejected;
- a reference to an absent materialized instance is rejected;
- unpassed effect/history subsystems are outside the guarantee.

The collector returns ordinary `IdentityReference` objects compatible with
`assess_dematerialization`, `dematerialize_if_safe`, and the existing atomic
`release_zone_exit_identity_group` gate.

## Reproduction

Run `python results/composite_identity_liveness/reproduce.py`.

The source-controlled regression first stages Prize B with two observers,
checks three independent owners (pending physical position, observer belief
position, effect reference), then resolves physical B into hand while leaving
the observer's latent pending B unresolved. That hand card remains blocked
by its belief reference alone.

After the observer pending identity is resolved, the same card can safely
dematerialize to the ordinary hand count. The regression also rejects stale
physical snapshots, conflicting reference IDs, orphan references and checks
per-class physical card conservation.

This is a deterministic **representation-correctness** result with a synthetic
card-class fixture. It supplies no competitive deck-strength or win-rate
evidence.

## Next

Give actual pending effect/history objects owned reference adapters and
require match-level release callers to pass the complete current owner set.
An explicitly missing owner cannot be detected by this collector, so no
global guarantee of safe dematerialization follows from this result alone.
