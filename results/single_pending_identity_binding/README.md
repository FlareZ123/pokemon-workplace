# A single pending-Prize belief must retain its physical instance ID

## Problem

The pre-existing one-Prize `ObserverPendingPrizeBeliefs` stores probabilistic
group identities but no physical `instance_id`. The physical Prize queue can
resolve the card into hand before the observer's latent identity is resolved.
At that point, looking only at the physical queue would incorrectly allow
the exact hand instance to collapse.

## Model and test

`tools/single_pending_identity_binding.py` provides a conservative
`BoundSinglePendingPrizeIdentity`, created only for exactly one physical
pending Prize whose remaining visibility geometry agrees with the observer
belief. This wrapper outlives physical resolution and publishes an ordinary
`IdentityReference` until the caller resolves the single pending belief.

`collect_composite_identity_references` accepts both this one-card binding and
the existing batch pending-Prize belief representation. The collector rejects
stale physical ledger snapshots and absent materialized IDs.

Run `python results/single_pending_identity_binding/reproduce.py`.
The fixture checks physical queue -> hand -> observer reveal -> release,
preservation of per-card-class totals and hand size, and rejection of mismatched
Prize geometry.

The owner wrapper is explicitly scoped to one pending Prize. It does not
implicitly prove correctness of a caller that omits any active effect owner,
nor does it justify a particular deck choice or predict matches.
