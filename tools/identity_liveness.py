"""Conservative liveness gate for collapsing exact card instances.

IdentityLedger can dematerialize an off-board card mechanically. This module adds
an explicit semantic precondition: exact physical identity may collapse only
when the card is in a caller-approved exchangeable zone and no live external
reference still names that instance.
"""

from __future__ import annotations

from collections.abc import Iterable, Set
from dataclasses import dataclass

from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    dematerialize,
)


DEFAULT_EXCHANGEABLE_ZONES = frozenset({
    "hand",
    "deck",
    "discard",
    "lost_zone",
})


@dataclass(frozen=True)
class IdentityReference:
    """One live higher-layer reference to an exact physical card instance."""

    reference_id: str
    instance_id: str
    reason: str

    def __post_init__(self) -> None:
        if not self.reference_id:
            raise ValueError("reference_id must be non-empty")
        if not self.instance_id:
            raise ValueError("instance_id must be non-empty")
        if not self.reason:
            raise ValueError("reason must be non-empty")


@dataclass(frozen=True)
class DematerializationAssessment:
    instance_id: str
    safe: bool
    blockers: tuple[str, ...]


def assess_dematerialization(
    ledger: IdentityLedger,
    instance_id: str,
    *,
    references: Iterable[IdentityReference] = (),
    exchangeable_zones: Set[str] = DEFAULT_EXCHANGEABLE_ZONES,
) -> DematerializationAssessment:
    """Return a conservative sufficient test for identity-collapse safety.

    The default exchangeable-zone set excludes relation-bearing or
    topology-sensitive zones such as in_play, attached, deck_top, and prize.
    A caller may supply a broader set only when it owns the proof that those
    additional zones are exchangeable in its representation.
    """

    current = ledger.instance(instance_id)
    blockers: list[str] = []

    if current.zone not in exchangeable_zones:
        blockers.append(f"zone:{current.zone}")

    if current.attached_to is not None:
        blockers.append(f"attached_to:{current.attached_to}")
    if current.board_object_id is not None:
        blockers.append(f"board_object:{current.board_object_id}")

    for reference in references:
        if reference.instance_id == instance_id:
            blockers.append(f"reference:{reference.reference_id}")

    blockers = sorted(set(blockers))
    return DematerializationAssessment(
        instance_id=instance_id,
        safe=not blockers,
        blockers=tuple(blockers),
    )


def dematerialize_if_safe(
    ledger: IdentityLedger,
    instance_id: str,
    *,
    references: Iterable[IdentityReference] = (),
    exchangeable_zones: Set[str] = DEFAULT_EXCHANGEABLE_ZONES,
) -> IdentityLedger:
    """Collapse one exact instance only after the liveness gate clears."""

    assessment = assess_dematerialization(
        ledger,
        instance_id,
        references=references,
        exchangeable_zones=exchangeable_zones,
    )
    if not assessment.safe:
        joined = ", ".join(assessment.blockers)
        raise ValueError(
            f"instance {instance_id!r} still requires exact identity: {joined}"
        )

    next_ledger = dematerialize(ledger, instance_id)
    assert_conserved(ledger, next_ledger)
    return next_ledger
