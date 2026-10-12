# Preventing released physical card IDs from being reused

## Failure witness

`IdentityLedger` rejects simultaneous duplicate materialized IDs, but it
does not remember an ID after its instance dematerializes. Reusing an old ID
for a different card is currently allowed by the bare API.

A stale effect or observer reference naming that old ID can then appear to
refer to the *new* card. The composite liveness collector correctly rejects
an absent instance, but it cannot distinguish two successive physical copies
that were incorrectly assigned the same string identifier.

## Narrow closed-path mitigation

`tools/identity_instance_provenance.py` adds an immutable wrapper around
existing ledger operations. Its `ever_issued` set survives safe dematerialization
and prevents any identifier being minted twice in the tracked path.
`begin_identity_provenance` can adopt an existing ledger only if its caller
also supplies all previously issued IDs that are no longer live.

`results/identity_instance_provenance/reproduce.py` verifies both the
original aliasing witness and a protected replacement sequence with fresh IDs,
plus card-class totals conservation.

This is a model-integrity test, not a competitive deck or gameplay win-rate
evaluation.

## Limitation

The wrapper guarantees uniqueness only if every materialization in that game
uses `materialize_unique` and the immutable provenance state is carried
through every transition. Legacy bare-`IdentityLedger` users are unchanged.
A future canonical match state should own this provenance once per game and
disallow untracked allocation, rather than relying on callers to opt in.
