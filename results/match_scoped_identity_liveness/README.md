# Player-scoped exact identity liveness in two-player matches

## Risk

Two independent players can legitimately use the same local physical instance
ID and the same local reference ID, such as `top` and `deck_top`. A naive
match-global flattening would either report a false ownership collision or
apply Player A's effect reference to Player B's card.

## Source and method

`tools/match_scoped_identity_liveness.py` composes the existing
`collect_composite_identity_references` once per player using the player's
current IdentityLedger, topology, pending beliefs and effect owners. It retains
`(player_id, IdentityReference)` pairs in an immutable match-level snapshot.

The `for_player(player_id)` projection must be used before calling the
player-local dematerialization gate. Duplicate player IDs, references to
unknown players and mismatched physical ledger snapshots are rejected.

The regression `results/match_scoped_identity_liveness/reproduce.py`
constructs two disjoint physical three-card ledgers that intentionally reuse
all three local instance ID strings. Both have `deck_top`/Prize-position
references. Only Alice has an effect retaining exact hand identity. Bob's
otherwise identical hand instance safely dematerializes while Alice's remains
blocked. Physical totals are conserved on both sides.

This is a deterministic representation-integrity result. It does not provide
match win rates, playable decklists or a canonical full match state.

## Next

A shared match object should enforce this scoped owner snapshot as part of
every release boundary, alongside global per-match issuance of never-recycled
physical card IDs or explicitly owner-scoped ID provenance.
