"""Authorize a KO effect order from selected rules sources, then resolve routes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping, Sequence

from ko_trigger_order_authority import AuthorityClaim, OrderingContext
from knockout_redirection_ordering import (
    ResolvedDestination,
    resolve_ordered_programs,
)
from source_order_chooser import (
    ConcreteAuthorityClaim,
    ConcreteChooserStatus,
    OrderingPlayers,
    assess_concrete_ordering_player,
)


class AuthorizedOrderStatus(str, Enum):
    RESOLVED = "resolved"
    NO_AUTHORITY_CLAIMS = "no_authority_claims"
    MISSING_PLAYER_CONTEXT = "missing_player_context"
    AUTHORITY_CONFLICT = "authority_conflict"
    UNAUTHORIZED_CHOOSER = "unauthorized_chooser"
    INVALID_EFFECT_ORDER = "invalid_effect_order"


@dataclass(frozen=True)
class AuthorizedOrderResult:
    status: AuthorizedOrderStatus
    chooser: str | None
    claims: tuple[AuthorityClaim, ...]
    concrete_claims: tuple[ConcreteAuthorityClaim, ...] = ()
    resolutions: tuple[ResolvedDestination, ...] | None = None


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

    assessment = assess_concrete_ordering_player(
        context,
        source_ids,
        players,
    )
    status_map = {
        ConcreteChooserStatus.NO_AUTHORITY_CLAIMS:
            AuthorizedOrderStatus.NO_AUTHORITY_CLAIMS,
        ConcreteChooserStatus.MISSING_PLAYER_CONTEXT:
            AuthorizedOrderStatus.MISSING_PLAYER_CONTEXT,
        ConcreteChooserStatus.AUTHORITY_CONFLICT:
            AuthorizedOrderStatus.AUTHORITY_CONFLICT,
    }
    if assessment.status != ConcreteChooserStatus.RESOLVED:
        return AuthorizedOrderResult(
            status_map[assessment.status],
            None,
            assessment.claims,
            assessment.concrete_claims,
        )

    assert assessment.chooser is not None
    chooser = assessment.chooser
    if submitted_by != chooser:
        return AuthorizedOrderResult(
            AuthorizedOrderStatus.UNAUTHORIZED_CHOOSER,
            chooser,
            assessment.claims,
            assessment.concrete_claims,
        )

    resolutions = resolve_ordered_programs(programs, ordered_effect_ids)
    if resolutions is None:
        return AuthorizedOrderResult(
            AuthorizedOrderStatus.INVALID_EFFECT_ORDER,
            chooser,
            assessment.claims,
            assessment.concrete_claims,
        )

    return AuthorizedOrderResult(
        AuthorizedOrderStatus.RESOLVED,
        chooser,
        assessment.claims,
        assessment.concrete_claims,
        resolutions,
    )
