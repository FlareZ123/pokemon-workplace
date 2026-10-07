"""Resolve destination overrides for Prize cards already staged as taken.

This layer deliberately separates three questions:
1. Which replacement effects are applicable to a pending Prize card?
2. Do those effects agree on one destination?
3. If they agree, execute the existing conserved physical Prize transition.

Applicability and effect-order authority belong upstream. A disagreement between
applicable replacements remains unresolved here instead of inventing precedence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from prize_pending_take import (
    PendingPrizeResolution,
    PrizePendingTakeState,
    resolve_next_pending_prize,
)


@dataclass(frozen=True, order=True)
class PrizeDestinationOverride:
    effect_id: str
    destination_zone: str

    def __post_init__(self) -> None:
        if not self.effect_id:
            raise ValueError("effect_id must be non-empty")
        if not self.destination_zone:
            raise ValueError("destination_zone must be non-empty")
        if self.destination_zone == "prize_pending":
            raise ValueError("override destination cannot remain prize_pending")


@dataclass(frozen=True)
class PrizeDestinationDecision:
    overrides: tuple[PrizeDestinationOverride, ...]
    destination_zone: str | None
    conflicting_zones: tuple[str, ...]

    @property
    def resolved(self) -> bool:
        return self.destination_zone is not None


@dataclass(frozen=True)
class PrizeDestinationTransition:
    decision: PrizeDestinationDecision
    resolution: PendingPrizeResolution | None

    @property
    def resolved(self) -> bool:
        return self.resolution is not None


def decide_prize_destination(
    overrides: Iterable[PrizeDestinationOverride],
    *,
    ordinary_destination: str = "hand",
) -> PrizeDestinationDecision:
    """Return one destination only when every applicable override agrees.

    The ordinary destination is used only when no replacement applies. Once an
    explicit replacement applies, the ordinary hand destination is no longer a
    competing assignment.
    """

    if not ordinary_destination:
        raise ValueError("ordinary_destination must be non-empty")
    if ordinary_destination == "prize_pending":
        raise ValueError("ordinary destination cannot remain prize_pending")

    rows = tuple(sorted(overrides))
    if not rows:
        return PrizeDestinationDecision((), ordinary_destination, ())

    zones = tuple(sorted({row.destination_zone for row in rows}))
    if len(zones) == 1:
        return PrizeDestinationDecision(rows, zones[0], ())

    return PrizeDestinationDecision(rows, None, zones)


def resolve_pending_prize_with_overrides(
    state: PrizePendingTakeState,
    overrides: Iterable[PrizeDestinationOverride],
    *,
    ordinary_destination: str = "hand",
) -> PrizeDestinationTransition:
    """Resolve the next pending Prize only when its destination is unambiguous."""

    if not state.pending:
        raise ValueError("no pending Prize card remains")

    decision = decide_prize_destination(
        overrides,
        ordinary_destination=ordinary_destination,
    )
    if not decision.resolved:
        return PrizeDestinationTransition(decision, None)

    resolution = resolve_next_pending_prize(
        state,
        destination_zone=decision.destination_zone,
    )
    return PrizeDestinationTransition(decision, resolution)
