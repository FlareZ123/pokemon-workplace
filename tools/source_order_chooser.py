"""Instantiate source-scoped ordering claims to concrete player identities."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from ko_trigger_order_authority import (
    AuthorityClaim,
    OrderingAuthority,
    OrderingContext,
    assess_ordering_authority,
)


class ConcreteChooserStatus(str, Enum):
    RESOLVED = "resolved"
    NO_AUTHORITY_CLAIMS = "no_authority_claims"
    MISSING_PLAYER_CONTEXT = "missing_player_context"
    AUTHORITY_CONFLICT = "authority_conflict"


@dataclass(frozen=True)
class OrderingPlayers:
    current_player: str | None = None
    next_player: str | None = None
    knocked_out_pokemon_owner: str | None = None


@dataclass(frozen=True)
class ConcreteAuthorityClaim:
    source_id: str
    authority: OrderingAuthority
    player_id: str
    scope_note: str


@dataclass(frozen=True)
class ConcreteChooserAssessment:
    status: ConcreteChooserStatus
    chooser: str | None
    claims: tuple[AuthorityClaim, ...]
    concrete_claims: tuple[ConcreteAuthorityClaim, ...] = ()


def _player_for_authority(
    authority: OrderingAuthority,
    players: OrderingPlayers,
) -> str | None:
    if authority == OrderingAuthority.CURRENT_PLAYER:
        return players.current_player
    if authority == OrderingAuthority.NEXT_PLAYER:
        return players.next_player
    if authority == OrderingAuthority.KNOCKED_OUT_POKEMON_OWNER:
        return players.knocked_out_pokemon_owner
    raise ValueError(f"unsupported ordering authority: {authority!r}")


def assess_concrete_ordering_player(
    context: OrderingContext,
    source_ids: Iterable[str],
    players: OrderingPlayers,
) -> ConcreteChooserAssessment:
    """Resolve selected source claims to one concrete chooser when possible."""

    assessment = assess_ordering_authority(context, source_ids)
    if not assessment.claims:
        return ConcreteChooserAssessment(
            ConcreteChooserStatus.NO_AUTHORITY_CLAIMS,
            None,
            assessment.claims,
        )

    concrete_claims: list[ConcreteAuthorityClaim] = []
    for claim in assessment.claims:
        player_id = _player_for_authority(claim.authority, players)
        if player_id is None:
            return ConcreteChooserAssessment(
                ConcreteChooserStatus.MISSING_PLAYER_CONTEXT,
                None,
                assessment.claims,
            )
        concrete_claims.append(
            ConcreteAuthorityClaim(
                source_id=claim.source_id,
                authority=claim.authority,
                player_id=player_id,
                scope_note=claim.scope_note,
            )
        )

    chooser_ids = {claim.player_id for claim in concrete_claims}
    if len(chooser_ids) != 1:
        return ConcreteChooserAssessment(
            ConcreteChooserStatus.AUTHORITY_CONFLICT,
            None,
            assessment.claims,
            tuple(concrete_claims),
        )

    return ConcreteChooserAssessment(
        ConcreteChooserStatus.RESOLVED,
        next(iter(chooser_ids)),
        assessment.claims,
        tuple(concrete_claims),
    )
