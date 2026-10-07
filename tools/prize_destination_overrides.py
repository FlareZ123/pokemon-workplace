"""Resolve destination overrides for Prize cards already staged as taken.

The mechanical layer separates applicability from ordering authority. Compatible
replacement effects can resolve directly. When applicable effects disagree, a
caller with rules-backed chooser authority can select one effect for the exact
pending Prize card; otherwise the choice remains pending without physical move.
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
    candidate_zones: tuple[str, ...]
    chosen_effect_id: str | None = None

    @property
    def resolved(self) -> bool:
        return self.destination_zone is not None

    @property
    def requires_choice(self) -> bool:
        return self.destination_zone is None and len(self.candidate_zones) > 1


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
    chosen_effect_id: str | None = None,
) -> PrizeDestinationDecision:
    """Resolve one destination when replacement effects agree or a choice exists."""

    if not ordinary_destination:
        raise ValueError("ordinary_destination must be non-empty")
    if ordinary_destination == "prize_pending":
        raise ValueError("ordinary destination cannot remain prize_pending")

    rows = tuple(sorted(overrides))
    if not rows:
        if chosen_effect_id is not None:
            raise ValueError("cannot choose a replacement when none applies")
        return PrizeDestinationDecision(
            (),
            ordinary_destination,
            (ordinary_destination,),
        )

    zones = tuple(sorted({row.destination_zone for row in rows}))
    if len(zones) == 1:
        if chosen_effect_id is not None:
            matching = tuple(
                row for row in rows if row.effect_id == chosen_effect_id
            )
            if not matching:
                raise ValueError("chosen replacement effect is not applicable")
        return PrizeDestinationDecision(
            rows,
            zones[0],
            zones,
            chosen_effect_id,
        )

    if chosen_effect_id is None:
        return PrizeDestinationDecision(rows, None, zones, None)

    matches = tuple(
        row for row in rows if row.effect_id == chosen_effect_id
    )
    if len(matches) != 1:
        raise ValueError(
            "chosen replacement effect must identify exactly one applicable effect"
        )
    return PrizeDestinationDecision(
        rows,
        matches[0].destination_zone,
        zones,
        chosen_effect_id,
    )


def resolve_pending_prize_with_overrides(
    state: PrizePendingTakeState,
    overrides: Iterable[PrizeDestinationOverride],
    *,
    ordinary_destination: str = "hand",
    chosen_effect_id: str | None = None,
) -> PrizeDestinationTransition:
    """Resolve the next pending Prize only after its destination is determined."""

    if not state.pending:
        raise ValueError("no pending Prize card remains")

    decision = decide_prize_destination(
        overrides,
        ordinary_destination=ordinary_destination,
        chosen_effect_id=chosen_effect_id,
    )
    if not decision.resolved:
        return PrizeDestinationTransition(decision, None)

    resolution = resolve_next_pending_prize(
        state,
        destination_zone=decision.destination_zone,
    )
    return PrizeDestinationTransition(decision, resolution)
