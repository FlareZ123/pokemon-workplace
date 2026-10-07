"""Preserve latent taken-Prize identity until its destination visibility is known.

Removing an unseen Prize position by marginalization is safe only if that
identity will never become later evidence for the same hidden-state model.
Discard and Lost Zone are public zones, so a redirected Prize can reveal an
identity after the physical Prize slot has already disappeared.

This module keeps one pending Prize identity latent alongside the joint
top/remaining-Prize belief, then conditions observers when the destination
makes that identity visible.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from math import isclose

from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_position_belief import PrizeGroup
from prize_top_swap_belief import TopPrizeJointBelief

PUBLIC_DESTINATIONS = frozenset({"discard", "lost_zone"})


@dataclass(frozen=True)
class PendingPrizeJointBelief:
    groups: tuple[str, ...]
    face_up: tuple[bool, ...]
    masses: tuple[
        tuple[
            tuple[PrizeGroup, tuple[PrizeGroup, ...], PrizeGroup],
            float,
        ],
        ...,
    ]

    def __post_init__(self) -> None:
        if not self.masses:
            raise ValueError("pending Prize belief must have support")
        if len(self.groups) != len(set(self.groups)):
            raise ValueError("groups must be unique")

        modeled = set(self.groups)
        total = 0.0
        for (top_group, prize_state, pending_group), probability in self.masses:
            if len(prize_state) != len(self.face_up):
                raise ValueError("Prize state must align with visibility")
            if probability < 0.0:
                raise ValueError("probabilities must be non-negative")
            values = (top_group, pending_group) + prize_state
            if any(
                value is not None and value not in modeled
                for value in values
            ):
                raise ValueError("belief contains an unmodeled group")
            total += probability

        if not isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError("probability mass must equal one")

    def top_probability(self, group: PrizeGroup) -> float:
        return sum(
            probability
            for (top_group, _prizes, _pending), probability in self.masses
            if top_group == group
        )

    def pending_probability(self, group: PrizeGroup) -> float:
        return sum(
            probability
            for (_top, _prizes, pending_group), probability in self.masses
            if pending_group == group
        )


@dataclass(frozen=True)
class ObserverPendingPrizeBeliefs:
    beliefs: tuple[tuple[str, PendingPrizeJointBelief], ...]

    def __post_init__(self) -> None:
        if not self.beliefs:
            raise ValueError("at least one observer belief is required")
        ids = tuple(observer_id for observer_id, _belief in self.beliefs)
        if len(ids) != len(set(ids)):
            raise ValueError("observer IDs must be unique")

        reference = self.beliefs[0][1]
        for _observer_id, belief in self.beliefs[1:]:
            if belief.groups != reference.groups:
                raise ValueError("all observers must use the same groups")
            if belief.face_up != reference.face_up:
                raise ValueError(
                    "all observers must agree on public Prize visibility"
                )

    def belief_for(self, observer_id: str) -> PendingPrizeJointBelief:
        for current_id, belief in self.beliefs:
            if current_id == observer_id:
                return belief
        raise KeyError(observer_id)


def _stage_one(
    belief: TopPrizeJointBelief,
    *,
    position: int,
    observed_group: PrizeGroup | object,
) -> PendingPrizeJointBelief:
    if not 0 <= position < belief.prize_count:
        raise IndexError("Prize position out of range")

    observe = observed_group is not _UNOBSERVED
    evidence = 0.0
    output: dict[
        tuple[PrizeGroup, tuple[PrizeGroup, ...], PrizeGroup],
        float,
    ] = defaultdict(float)

    for (top_group, prizes), probability in belief.masses:
        pending_group = prizes[position]
        if observe and pending_group != observed_group:
            continue
        remaining = prizes[:position] + prizes[position + 1 :]
        output[(top_group, remaining, pending_group)] += probability
        evidence += probability

    if evidence == 0.0:
        raise ValueError("Prize observation has zero probability")

    masses = tuple(
        (state, probability / evidence)
        for state, probability in sorted(output.items(), key=lambda row: repr(row[0]))
    )
    face_up = belief.face_up[:position] + belief.face_up[position + 1 :]
    return PendingPrizeJointBelief(belief.groups, face_up, masses)


_UNOBSERVED = object()


def stage_one_pending_prize_for_observers(
    state: ObserverTopPrizeBeliefs,
    *,
    position: int,
    visible_groups: Mapping[str, PrizeGroup],
) -> ObserverPendingPrizeBeliefs:
    """Remove one Prize slot while retaining its identity as latent evidence."""

    observer_ids = {observer_id for observer_id, _belief in state.beliefs}
    if not set(visible_groups) <= observer_ids:
        raise ValueError("visible_groups contains an unknown observer")

    rows = []
    for observer_id, belief in state.beliefs:
        observed = visible_groups.get(observer_id, _UNOBSERVED)
        rows.append(
            (
                observer_id,
                _stage_one(
                    belief,
                    position=position,
                    observed_group=observed,
                ),
            )
        )
    return ObserverPendingPrizeBeliefs(tuple(rows))


def resolve_single_pending_visibility(
    state: ObserverPendingPrizeBeliefs,
    *,
    visible_groups: Mapping[str, PrizeGroup],
) -> ObserverTopPrizeBeliefs:
    """Condition observers who see the pending identity, then forget that card."""

    observer_ids = {observer_id for observer_id, _belief in state.beliefs}
    if not set(visible_groups) <= observer_ids:
        raise ValueError("visible_groups contains an unknown observer")

    rows = []
    for observer_id, belief in state.beliefs:
        observed = visible_groups.get(observer_id, _UNOBSERVED)
        evidence = 0.0
        output: dict[
            tuple[PrizeGroup, tuple[PrizeGroup, ...]],
            float,
        ] = defaultdict(float)

        for (top_group, prizes, pending_group), probability in belief.masses:
            if observed is not _UNOBSERVED and pending_group != observed:
                continue
            output[(top_group, prizes)] += probability
            evidence += probability

        if evidence == 0.0:
            raise ValueError("pending Prize observation has zero probability")

        masses = tuple(
            (hidden_state, probability / evidence)
            for hidden_state, probability in sorted(
                output.items(),
                key=lambda row: repr(row[0]),
            )
        )
        rows.append(
            (
                observer_id,
                TopPrizeJointBelief(
                    belief.groups,
                    belief.face_up,
                    masses,
                ),
            )
        )

    return ObserverTopPrizeBeliefs(tuple(rows))


def destination_visibility(
    observer_ids: tuple[str, ...],
    *,
    actor_id: str,
    destination_zone: str,
    observed_group: PrizeGroup,
) -> dict[str, PrizeGroup]:
    """Return who learns the exact taken Prize identity at final destination."""

    if actor_id not in observer_ids:
        raise ValueError("actor_id is not a known observer")
    if destination_zone in PUBLIC_DESTINATIONS:
        return {
            observer_id: observed_group
            for observer_id in observer_ids
        }
    if destination_zone == "hand":
        return {actor_id: observed_group}
    raise ValueError(f"unsupported destination visibility: {destination_zone!r}")
