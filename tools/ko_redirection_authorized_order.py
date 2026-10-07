"""Authorize a KO effect order from selected rules sources, then resolve routes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping, Sequence

from ko_trigger_order_authority import (
    AuthorityClaim,
    OrderingAuthority,
    OrderingContext,
    assess_ordering_authority,
)
from knockout_redirection_ordering import (
    ResolvedDestination,
    resolve_ordered_programs,
)


class AuthorizedOrderStatus(str, Enum):
    RESOLVED = "resolved"
    NO_AUTHORITY_CLAIMS = "no_authority_claims"
    MISSING_PLAYER_CONTEXT = "missing_player_context"
    AUTHORITY_CONFLICT = "authority_conflict"
    UNAUTHORIZED_CHOOSER = "unauthorized_chooser"
    INVALID_EFFECT_ORDER = "invalid_effect_order"


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
class AuthorizedOrderResult:
    status: AuthorizedOrderStatus
    chooser: str | None
    claims: tuple[AuthorityClaim, ...]
    concrete_claims: tuple[ConcreteAuthorityClaim, ...] = ()
    resolutions: tuple[ResolvedDestination, ...] | None = None


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


def authorize_and_resolve_order(
    programs: Mapping[str, Mapping[str, str]],
    ordered_effect_ids: Sequence[str],
    *,
    context: OrderingContext,
    source_ids: Iterable[str],
    players: OrderingPlayers,
    submitted_by: str,
) -> AuthorizedOrderResult:
    """Authorize a caller-supplied effect order before physical route resolution.

    Source-level authority claims are instantiated to concrete player IDs. If
    different abstract authority rules name the same concrete player in the
    current state, execution is safe despite the source-level disagreement.
    """

    assessment = assess_ordering_authority(context, source_ids)
    if not assessment.claims:
        return AuthorizedOrderResult(
            AuthorizedOrderStatus.NO_AUTHORITY_CLAIMS,
            None,
            assessment.claims,
        )

    concrete_claims: list[ConcreteAuthorityClaim] = []
    for claim in assessment.claims:
        player_id = _player_for_authority(claim.authority, players)
        if player_id is None:
            return AuthorizedOrderResult(
                AuthorizedOrderStatus.MISSING_PLAYER_CONTEXT,
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
        return AuthorizedOrderResult(
            AuthorizedOrderStatus.AUTHORITY_CONFLICT,
            None,
            assessment.claims,
            tuple(concrete_claims),
        )

    chooser = next(iter(chooser_ids))
    if submitted_by != chooser:
        return AuthorizedOrderResult(
            AuthorizedOrderStatus.UNAUTHORIZED_CHOOSER,
            chooser,
            assessment.claims,
            tuple(concrete_claims),
        )

    resolutions = resolve_ordered_programs(programs, ordered_effect_ids)
    if resolutions is None:
        return AuthorizedOrderResult(
            AuthorizedOrderStatus.INVALID_EFFECT_ORDER,
            chooser,
            assessment.claims,
            tuple(concrete_claims),
        )

    return AuthorizedOrderResult(
        AuthorizedOrderStatus.RESOLVED,
        chooser,
        assessment.claims,
        tuple(concrete_claims),
        resolutions,
    )
