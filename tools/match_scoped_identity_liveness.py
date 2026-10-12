"""Scope exact-identity liveness by player in two-player match state.

Two players may independently use the same local instance IDs and owner
reference IDs. Those names must be interpreted within each player's ledger,
rather than flattened into a match-wide unqualified string namespace.
"""

from __future__ import annotations

from dataclasses import dataclass

from composite_identity_liveness import collect_composite_identity_references
from identity_liveness import IdentityReference
from identity_materialization import IdentityLedger
from pending_prize_batch_identity_belief import ObserverPendingPrizeBatchBeliefs
from prize_pending_take import PrizePendingTakeState
from single_pending_identity_binding import BoundSinglePendingPrizeIdentity
from top_prize_physical_bridge import TopPrizePhysicalState


@dataclass(frozen=True)
class PlayerIdentityOwners:
    player_id: str
    ledger: IdentityLedger
    top_prize: TopPrizePhysicalState | None = None
    pending_prize: PrizePendingTakeState | None = None
    pending_beliefs: ObserverPendingPrizeBatchBeliefs | None = None
    single_pending_beliefs: BoundSinglePendingPrizeIdentity | None = None
    effect_references: tuple[IdentityReference, ...] = ()

    def __post_init__(self) -> None:
        if not self.player_id:
            raise ValueError("player_id must be non-empty")


@dataclass(frozen=True)
class ScopedIdentityReference:
    player_id: str
    reference: IdentityReference


@dataclass(frozen=True)
class MatchIdentityReferences:
    player_ids: tuple[str, str]
    references: tuple[ScopedIdentityReference, ...]

    def __post_init__(self) -> None:
        if len(self.player_ids) != 2 or len(set(self.player_ids)) != 2:
            raise ValueError("match identity owners require two distinct players")
        if any(not player_id for player_id in self.player_ids):
            raise ValueError("player IDs must be non-empty")
        if any(row.player_id not in self.player_ids for row in self.references):
            raise ValueError("reference names an unknown player")

    def for_player(self, player_id: str) -> tuple[IdentityReference, ...]:
        """Supply the original unqualified references to that player's gate."""

        if player_id not in self.player_ids:
            raise KeyError(player_id)
        return tuple(
            row.reference
            for row in self.references
            if row.player_id == player_id
        )


def collect_match_identity_references(
    players: tuple[PlayerIdentityOwners, PlayerIdentityOwners],
) -> MatchIdentityReferences:
    """Build a two-player union while preserving independent ID namespaces."""

    if len(players) != 2:
        raise ValueError("match identity owners require exactly two players")
    ids = (players[0].player_id, players[1].player_id)
    if len(set(ids)) != 2:
        raise ValueError("player IDs must be distinct")

    gathered: list[ScopedIdentityReference] = []
    for player in players:
        references = collect_composite_identity_references(
            player.ledger,
            top_prize=player.top_prize,
            pending_prize=player.pending_prize,
            pending_beliefs=player.pending_beliefs,
            single_pending_beliefs=player.single_pending_beliefs,
            effect_references=player.effect_references,
        )
        gathered.extend(
            ScopedIdentityReference(player.player_id, ref)
            for ref in references
        )

    return MatchIdentityReferences(ids, tuple(gathered))
