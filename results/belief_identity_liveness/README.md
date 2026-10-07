# Observer belief state can keep an off-board identity live

## Question

Can an exact physical card in an ordinary exchangeable zone be safely
dematerialized while an observer-belief object still uses that instance ID as a
latent variable key?

No.

Implementation extension: tools/identity_reference_sources.py
Regression: results/belief_identity_liveness/reproduce.py

## Witness

A materialized card pending-a is already physically in hand. Hand is normally an
exchangeable zone under the identity-liveness policy.

Separately, ObserverPendingPrizeBatchBeliefs still contains pending-a in its
pending_instance_ids tuple. This represents an intermediate state where the
physical destination has been chosen while the corresponding observer-relative
latent identity has not yet been fully projected away.

pending_prize_belief_identity_references publishes that ownership as:

belief:prize_pending:0 -> pending-a

The liveness gate therefore blocks dematerialization even though the physical
zone itself is exchangeable.

After resolve_pending_instance_visibility removes the latent pending variable,
the belief reference set becomes empty. The card can then collapse safely into
the exchangeable hand count, with per-class totals preserved.

## Finding

Physical destination and information-state lifetime are separate boundaries.

A card entering hand, discard, or another ordinary zone does not prove that its
exact instance ID is free for reuse or deletion. Observer-relative state may
still use that ID to preserve correlation until visibility has been resolved.

This closes one part of the automatic reference-collection gap identified by
identity_liveness.

## Architectural consequence

Composite transitions that update physical and belief state should either:

1. update both layers atomically; or
2. preserve an explicit liveness reference across the intermediate boundary.

The second option makes transient staging safe without forcing every subsystem
into one monolithic state type.

## Limits

This adapter covers ObserverPendingPrizeBatchBeliefs because it explicitly keys
latent variables by physical instance ID. Other belief models should publish
similar references only when their representation genuinely retains exact
instance identity.
