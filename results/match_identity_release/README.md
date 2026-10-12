# Atomic two-player identity release boundary

## Integration

The reference ownership and never-reuse experiments exposed two conditions on dematerialization: every current identity owner must have released its reference, and a retired ID must never be reissued. In a two-player match, those conditions must be checked against the targeted player's ledger, since local IDs can legitimately collide across players.

`tools/match_identity_release.py` composes `MatchIdentityReferences` with the guarded `IdentityProvenanceState` release. It returns a new immutable two-player state only if the requested release is legal, and rebinds any explicit top/Prize or pending-Prize snapshots to the new ledger generation. Other player state remains unchanged.

## Regression

`python results/match_identity_release/reproduce.py` checks two independent three-card physical owners using intentionally identical local IDs. Player A has a live effect holding the exact hand instance and is blocked. Player B's unreferenced hand instance releases, retains an issued-ID tombstone, and cannot reuse its retired ID. Once A's effect reference is explicitly retired, A can release too. Each player's card-class totals remain conserved and their topology snapshots follow the updated ledger.

## Boundaries

This is a closed-path **release** operator. It does not perform arbitrary gameplay transitions or automatically discover owners omitted by callers. Effect completion is an external fact supplied through a changed owner snapshot; this module does not infer effect completion from card zones. A canonical match state must eventually take responsibility for all active owners and card-ID issuance during normal gameplay.

It supplies no deck-strength or head-to-head win-rate estimate.
