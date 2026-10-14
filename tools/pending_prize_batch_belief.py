"""Joint observer belief for an ordered batch of unresolved Prize identities.

The physical Prize queue can have several cards in flight, including additional
Prizes inserted at the front. Keeping each latent identity alongside deck-top
and remaining-Prize identities prevents premature loss of correlations.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from math import isclose

from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_position_belief import PrizeGroup
from prize_top_swap_belief import TopPrizeJointBelief

StateKey = tuple[PrizeGroup, tuple[PrizeGroup, ...], tuple[PrizeGroup, ...]]


@dataclass(frozen=True)
class PendingPrizeBatchBelief:
    groups: tuple[str, ...]
    face_up: tuple[bool, ...]
    pending_ids: tuple[str, ...]
    masses: tuple[tuple[StateKey, float], ...]

    def __post_init__(self) -> None:
        if not self.masses:
            raise ValueError("pending batch must have support")
        if len(self.groups) != len(set(self.groups)):
            raise ValueError("groups must be unique")
        if len(self.pending_ids) != len(set(self.pending_ids)):
            raise ValueError("pending instance IDs must be unique")
        if any(not identifier for identifier in self.pending_ids):
            raise ValueError("pending IDs must be nonempty")
        modeled = set(self.groups)
        total = 0.0
        for (top, prizes, pending), mass in self.masses:
            if len(prizes) != len(self.face_up):
                raise ValueError("remaining Prize/face-up geometry mismatch")
            if len(pending) != len(self.pending_ids):
                raise ValueError("pending identity/ID geometry mismatch")
            if mass < 0:
                raise ValueError("negative probability mass")
            if any(g is not None and g not in modeled for g in (top, *prizes, *pending)):
                raise ValueError("unmodeled card group")
            total += mass
        if not isclose(total, 1.0, rel_tol=0, abs_tol=1e-12):
            raise ValueError("probability mass must equal one")

    def top_probability(self, group: PrizeGroup) -> float:
        return sum(mass for (top, _, _), mass in self.masses if top == group)

    def pending_probability(self, instance_id: str, group: PrizeGroup) -> float:
        position = self.pending_ids.index(instance_id)
        return sum(
            mass for (_, _, pending), mass in self.masses
            if pending[position] == group
        )


@dataclass(frozen=True)
class ObserverPendingPrizeBatchBeliefs:
    beliefs: tuple[tuple[str, PendingPrizeBatchBelief], ...]

    def __post_init__(self) -> None:
        if not self.beliefs:
            raise ValueError("at least one observer is required")
        names = [name for name, _ in self.beliefs]
        if len(names) != len(set(names)):
            raise ValueError("observer IDs must be unique")
        baseline = self.beliefs[0][1]
        for _, belief in self.beliefs[1:]:
            if (belief.groups, belief.face_up, belief.pending_ids) != (
                baseline.groups, baseline.face_up, baseline.pending_ids
            ):
                raise ValueError("observers disagree on public batch topology")

    def belief_for(self, observer_id: str) -> PendingPrizeBatchBelief:
        for name, belief in self.beliefs:
            if name == observer_id:
                return belief
        raise KeyError(observer_id)


def _normalize(
    groups: tuple[str, ...],
    face_up: tuple[bool, ...],
    pending_ids: tuple[str, ...],
    rows: Mapping[StateKey, float],
) -> PendingPrizeBatchBelief:
    evidence = sum(rows.values())
    if evidence <= 0:
        raise ValueError("observation has zero probability")
    masses = tuple(
        (key, mass / evidence)
        for key, mass in sorted(rows.items(), key=lambda item: repr(item[0]))
        if mass > 0
    )
    return PendingPrizeBatchBelief(groups, face_up, pending_ids, masses)


def _check_observations(
    observer_ids: set[str],
    pending_ids: tuple[str, ...],
    visible_groups: Mapping[str, Mapping[str, PrizeGroup]],
) -> None:
    if not set(visible_groups).issubset(observer_ids):
        raise ValueError("unknown observer")
    pending_set = set(pending_ids)
    if any(not set(groups).issubset(pending_set) for groups in visible_groups.values()):
        raise ValueError("observation references an unknown pending instance")


def stage_pending_prize_batch(
    state: ObserverTopPrizeBeliefs,
    *,
    positions: tuple[int, ...],
    pending_ids: tuple[str, ...],
    visible_groups: Mapping[str, Mapping[str, PrizeGroup]],
) -> ObserverPendingPrizeBatchBeliefs:
    """Stage original Prize positions in supplied physical pending-queue order."""
    if not positions or len(positions) != len(set(positions)):
        raise ValueError("positions must be nonempty and distinct")
    if len(positions) != len(pending_ids):
        raise ValueError("positions and IDs must align")
    _check_observations({name for name, _ in state.beliefs}, pending_ids, visible_groups)
    output = []
    for observer_id, belief in state.beliefs:
        if any(position < 0 or position >= belief.prize_count for position in positions):
            raise IndexError("Prize position out of range")
        selected = set(positions)
        known = visible_groups.get(observer_id, {})
        rows: dict[StateKey, float] = defaultdict(float)
        for (top, prizes), mass in belief.masses:
            taken = tuple(prizes[position] for position in positions)
            if any(
                taken[index] != known[identifier]
                for index, identifier in enumerate(pending_ids)
                if identifier in known
            ):
                continue
            remaining = tuple(
                group for index, group in enumerate(prizes) if index not in selected
            )
            rows[(top, remaining, taken)] += mass
        face_up = tuple(
            visible for index, visible in enumerate(belief.face_up)
            if index not in selected
        )
        output.append((
            observer_id,
            _normalize(belief.groups, face_up, pending_ids, rows),
        ))
    return ObserverPendingPrizeBatchBeliefs(tuple(output))


def stage_additional_pending_prize_front_belief(
    state: ObserverPendingPrizeBatchBeliefs,
    *,
    position: int,
    instance_id: str,
    visible_groups: Mapping[str, PrizeGroup],
) -> ObserverPendingPrizeBatchBeliefs:
    """Insert an additional taken Prize at the front of an existing latent queue."""
    if not instance_id:
        raise ValueError("instance ID must be nonempty")
    if not set(visible_groups).issubset({name for name, _ in state.beliefs}):
        raise ValueError("unknown observer")
    output = []
    for observer_id, belief in state.beliefs:
        if instance_id in belief.pending_ids:
            raise ValueError("duplicate pending instance ID")
        if not 0 <= position < len(belief.face_up):
            raise IndexError("Prize position out of range")
        rows: dict[StateKey, float] = defaultdict(float)
        for (top, prizes, pending), mass in belief.masses:
            new_group = prizes[position]
            if observer_id in visible_groups and new_group != visible_groups[observer_id]:
                continue
            remaining = prizes[:position] + prizes[position + 1:]
            rows[(top, remaining, (new_group,) + pending)] += mass
        face_up = belief.face_up[:position] + belief.face_up[position + 1:]
        output.append((
            observer_id,
            _normalize(
                belief.groups, face_up, (instance_id,) + belief.pending_ids, rows,
            ),
        ))
    return ObserverPendingPrizeBatchBeliefs(tuple(output))


def resolve_next_pending_batch_visibility(
    state: ObserverPendingPrizeBatchBeliefs,
    *,
    instance_id: str,
    visible_groups: Mapping[str, PrizeGroup],
) -> ObserverPendingPrizeBatchBeliefs:
    """Condition on destination-visible identity before forgetting the queue head."""
    if not set(visible_groups).issubset({name for name, _ in state.beliefs}):
        raise ValueError("unknown observer")
    output = []
    for observer_id, belief in state.beliefs:
        if not belief.pending_ids or belief.pending_ids[0] != instance_id:
            raise ValueError("only the next pending instance can resolve")
        rows: dict[StateKey, float] = defaultdict(float)
        for (top, prizes, pending), mass in belief.masses:
            if observer_id in visible_groups and pending[0] != visible_groups[observer_id]:
                continue
            rows[(top, prizes, pending[1:])] += mass
        output.append((
            observer_id,
            _normalize(
                belief.groups, belief.face_up, belief.pending_ids[1:], rows,
            ),
        ))
    return ObserverPendingPrizeBatchBeliefs(tuple(output))


def finish_pending_prize_batch(
    state: ObserverPendingPrizeBatchBeliefs,
) -> ObserverTopPrizeBeliefs:
    """Project only once every latent pending identity has been resolved."""
    output = []
    for observer_id, belief in state.beliefs:
        if belief.pending_ids:
            raise ValueError("pending Prize queue is not empty")
        masses = tuple(
            ((top, prizes), mass)
            for (top, prizes, _), mass in belief.masses
        )
        output.append((
            observer_id,
            TopPrizeJointBelief(belief.groups, belief.face_up, masses),
        ))
    return ObserverTopPrizeBeliefs(tuple(output))
