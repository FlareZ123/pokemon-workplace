"""Resolve overlapping evidence-backed effect-order authority claims safely."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from effect_order_authority import (
    OrderAuthorityCase,
    OrderAuthorityContext,
    ordering_player,
)


class AuthorityResolutionStatus(str, Enum):
    RESOLVED = "resolved"
    MISSING_CONTEXT = "missing_context"
    CONFLICT = "conflict"


@dataclass(frozen=True)
class AuthorityClaim:
    case: OrderAuthorityCase
    chooser: str | None


@dataclass(frozen=True)
class AuthorityResolution:
    status: AuthorityResolutionStatus
    claims: tuple[AuthorityClaim, ...]
    chooser: str | None

    def __post_init__(self) -> None:
        if not self.claims:
            raise ValueError("at least one authority claim is required")

        concrete = {
            claim.chooser
            for claim in self.claims
            if claim.chooser is not None
        }

        if self.status == AuthorityResolutionStatus.RESOLVED:
            if self.chooser is None or concrete != {self.chooser}:
                raise ValueError("resolved authority requires one concrete chooser")
            if any(claim.chooser is None for claim in self.claims):
                raise ValueError("resolved authority cannot contain missing claims")
            return

        if self.chooser is not None:
            raise ValueError("unresolved authority cannot expose a chooser")

        if self.status == AuthorityResolutionStatus.MISSING_CONTEXT:
            if not any(claim.chooser is None for claim in self.claims):
                raise ValueError("missing-context status requires a missing claim")
            return

        if self.status == AuthorityResolutionStatus.CONFLICT:
            if any(claim.chooser is None for claim in self.claims):
                raise ValueError("conflict status requires complete claims")
            if len(concrete) < 2:
                raise ValueError("conflict status requires different concrete choosers")
            return

        raise ValueError(f"unsupported authority status: {self.status!r}")


def resolve_overlapping_authority(
    cases: Iterable[OrderAuthorityCase],
    context: OrderAuthorityContext,
) -> AuthorityResolution:
    """Combine applicable authority rules without inventing precedence.

    The semantic caller decides which evidence-backed cases apply to the
    current event. This function asks each existing authority case for its
    concrete chooser in the supplied state.

    If every applicable case resolves to the same player, the concrete chooser
    is safe even if the relative precedence of the rules is not known. If the
    cases resolve to different players, the authority remains unresolved until
    a more specific rule or ruling establishes precedence.
    """

    requested = tuple(cases)
    if not requested:
        raise ValueError("at least one authority case is required")
    if len(requested) != len(set(requested)):
        raise ValueError("authority cases must be unique")

    claims = tuple(
        AuthorityClaim(case, ordering_player(case, context))
        for case in requested
    )

    if any(claim.chooser is None for claim in claims):
        return AuthorityResolution(
            AuthorityResolutionStatus.MISSING_CONTEXT,
            claims,
            None,
        )

    choosers = {claim.chooser for claim in claims}
    if len(choosers) == 1:
        chooser = next(iter(choosers))
        assert chooser is not None
        return AuthorityResolution(
            AuthorityResolutionStatus.RESOLVED,
            claims,
            chooser,
        )

    return AuthorityResolution(
        AuthorityResolutionStatus.CONFLICT,
        claims,
        None,
    )


def player_may_choose_order(
    resolution: AuthorityResolution,
    player_id: str,
) -> bool:
    """Return whether a concrete player is authorized by a resolved claim set."""

    if not player_id:
        raise ValueError("player_id must be non-empty")
    return (
        resolution.status == AuthorityResolutionStatus.RESOLVED
        and resolution.chooser == player_id
    )
