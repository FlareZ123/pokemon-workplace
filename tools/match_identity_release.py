"""Atomic player-scoped release preserving card-ID provenance and live owners."""

from __future__ import annotations

from dataclasses import dataclass, replace

from identity_instance_provenance import (
    IdentityProvenanceState,
    dematerialize_preserving_provenance,
)
from match_scoped_identity_liveness import (
    PlayerIdentityOwners,
    collect_match_identity_references,
)


@dataclass(frozen=True)
class MatchIdentityReleaseState:
    """Two player-local ledgers with their current reference owner snapshots."""

    players: tuple[
        tuple[PlayerIdentityOwners, IdentityProvenanceState],
        tuple[PlayerIdentityOwners, IdentityProvenanceState],
    ]

    def __post_init__(self) -> None:
        if len(self.players) != 2:
            raise ValueError("match requires exactly two identity owner states")
        ids = tuple(owner.player_id for owner, _provenance in self.players)
        if len(set(ids)) != 2:
            raise ValueError("player IDs must be distinct")
        for owner, provenance in self.players:
            if owner.ledger != provenance.ledger:
                raise ValueError(
                    f"provenance ledger mismatch for player {owner.player_id!r}"
                )

    def owner_for(self, player_id: str) -> PlayerIdentityOwners:
        for owner, _provenance in self.players:
            if owner.player_id == player_id:
                return owner
        raise KeyError(player_id)

    def provenance_for(self, player_id: str) -> IdentityProvenanceState:
        for owner, provenance in self.players:
            if owner.player_id == player_id:
                return provenance
        raise KeyError(player_id)


def _rebind_owner(
    owner: PlayerIdentityOwners,
    provenance: IdentityProvenanceState,
) -> PlayerIdentityOwners:
    """Keep explicit Prize snapshots at the same new ledger generation."""

    ledger = provenance.ledger
    top_prize = (
        replace(owner.top_prize, ledger=ledger)
        if owner.top_prize is not None
        else None
    )
    pending_prize = (
        replace(
            owner.pending_prize,
            physical=replace(owner.pending_prize.physical, ledger=ledger),
        )
        if owner.pending_prize is not None
        else None
    )
    return replace(
        owner,
        ledger=ledger,
        top_prize=top_prize,
        pending_prize=pending_prize,
    )


def release_match_identity(
    state: MatchIdentityReleaseState,
    *,
    player_id: str,
    instance_id: str,
) -> MatchIdentityReleaseState:
    """Release only after current owners agree and preserve retired-ID history."""

    match_refs = collect_match_identity_references(
        tuple(owner for owner, _provenance in state.players)
    )
    references = match_refs.for_player(player_id)
    provenance = state.provenance_for(player_id)
    next_provenance = dematerialize_preserving_provenance(
        provenance,
        instance_id,
        references=references,
    )
    players = tuple(
        (
            _rebind_owner(owner, next_provenance),
            next_provenance,
        )
        if owner.player_id == player_id else (owner, other_provenance)
        for owner, other_provenance in state.players
    )
    return MatchIdentityReleaseState(players)
