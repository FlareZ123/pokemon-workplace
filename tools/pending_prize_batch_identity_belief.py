"""Observer-relative latent identities for a simultaneous pending Prize batch."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from math import isclose

from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_position_belief import PrizeGroup
from prize_top_swap_belief import TopPrizeJointBelief

_UNOBSERVED = object()


@dataclass(frozen=True)
class PendingPrizeBatchJointBelief:
    groups: tuple[str, ...]
    face_up: tuple[bool, ...]
    pending_count: int
    masses: tuple[
        tuple[
            tuple[
                PrizeGroup,
                tuple[PrizeGroup, ...],
                tuple[PrizeGroup, ...],
            ],
            float,
        ],
        ...,
    ]

    def __post_init__(self) -> None:
        if self.pending_count < 0:
            raise ValueError("pending_count must be non-negative")
        if not self.masses:
            raise ValueError("belief must have support")
        if len(self.groups) != len(set(self.groups)):
            raise ValueError("groups must be unique")

        modeled = set(self.groups)
        total = 0.0
        for (top_group, prizes, pending), probability in self.masses:
            if len(prizes) != len(self.face_up):
                raise ValueError("Prize state must align with visibility")
            if len(pending) != self.pending_count:
                raise ValueError("pending state length mismatch")
            if probability < 0.0:
                raise ValueError("probabilities must be non-negative")
            values = (top_group,) + prizes + pending
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

    def pending_probability(self, index: int, group: PrizeGroup) -> float:
        if not 0 <= index < self.pending_count:
            raise IndexError("pending index out of range")
        return sum(
            probability
            for (_top, _prizes, pending), probability in self.masses
            if pending[index] == group
        )


@dataclass(frozen=True)
class ObserverPendingPrizeBatchBeliefs:
    pending_instance_ids: tuple[str, ...]
    beliefs: tuple[tuple[str, PendingPrizeBatchJointBelief], ...]

    def __post_init__(self) -> None:
        if len(self.pending_instance_ids) != len(set(self.pending_instance_ids)):
            raise ValueError("pending instance IDs must be unique")
        if not self.beliefs:
            raise ValueError("at least one observer belief is required")

        observer_ids = tuple(observer_id for observer_id, _belief in self.beliefs)
        if len(observer_ids) != len(set(observer_ids)):
            raise ValueError("observer IDs must be unique")

        reference = self.beliefs[0][1]
        if reference.pending_count != len(self.pending_instance_ids):
            raise ValueError("pending instance IDs must align with belief batch")

        for _observer_id, belief in self.beliefs[1:]:
            if belief.groups != reference.groups:
                raise ValueError("all observers must use the same groups")
            if belief.face_up != reference.face_up:
                raise ValueError("all observers must agree on Prize visibility")
            if belief.pending_count != reference.pending_count:
                raise ValueError("all observers must use the same pending geometry")

    def belief_for(self, observer_id: str) -> PendingPrizeBatchJointBelief:
        for current_id, belief in self.beliefs:
            if current_id == observer_id:
                return belief
        raise KeyError(observer_id)

    def pending_index(self, instance_id: str) -> int:
        try:
            return self.pending_instance_ids.index(instance_id)
        except ValueError as exc:
            raise KeyError(instance_id) from exc


def _stage_batch_for_one(
    belief: TopPrizeJointBelief,
    *,
    positions: tuple[int, ...],
    observed_groups: tuple[PrizeGroup, ...] | object,
) -> PendingPrizeBatchJointBelief:
    if not positions:
        raise ValueError("at least one Prize position must be staged")
    if len(positions) != len(set(positions)):
        raise ValueError("Prize positions must be unique")
    if any(position < 0 or position >= belief.prize_count for position in positions):
        raise IndexError("Prize position out of range")

    observe = observed_groups is not _UNOBSERVED
    if observe and len(observed_groups) != len(positions):
        raise ValueError("observed groups must align with staged positions")

    selected = set(positions)
    output: dict[
        tuple[
            PrizeGroup,
            tuple[PrizeGroup, ...],
            tuple[PrizeGroup, ...],
        ],
        float,
    ] = defaultdict(float)
    evidence = 0.0

    for (top_group, prizes), probability in belief.masses:
        pending = tuple(prizes[position] for position in positions)
        if observe and pending != observed_groups:
            continue
        remaining = tuple(
            group
            for index, group in enumerate(prizes)
            if index not in selected
        )
        output[(top_group, remaining, pending)] += probability
        evidence += probability

    if evidence == 0.0:
        raise ValueError("Prize batch observation has zero probability")

    remaining_face_up = tuple(
        visible
        for index, visible in enumerate(belief.face_up)
        if index not in selected
    )
    masses = tuple(
        (hidden_state, probability / evidence)
        for hidden_state, probability in sorted(
            output.items(),
            key=lambda row: repr(row[0]),
        )
    )
    return PendingPrizeBatchJointBelief(
        belief.groups,
        remaining_face_up,
        len(positions),
        masses,
    )


def stage_pending_prize_batch_for_observers(
    state: ObserverTopPrizeBeliefs,
    *,
    positions: tuple[int, ...],
    pending_instance_ids: tuple[str, ...],
    visible_groups: Mapping[str, tuple[PrizeGroup, ...]],
) -> ObserverPendingPrizeBatchBeliefs:
    """Remove selected Prize slots while keeping selected identities latent."""

    if len(pending_instance_ids) != len(positions):
        raise ValueError("pending instance IDs must align with positions")
    if len(pending_instance_ids) != len(set(pending_instance_ids)):
        raise ValueError("pending instance IDs must be unique")

    observer_ids = {observer_id for observer_id, _belief in state.beliefs}
    if not set(visible_groups) <= observer_ids:
        raise ValueError("visible_groups contains an unknown observer")

    rows = []
    for observer_id, belief in state.beliefs:
        observed = visible_groups.get(observer_id, _UNOBSERVED)
        rows.append(
            (
                observer_id,
                _stage_batch_for_one(
                    belief,
                    positions=positions,
                    observed_groups=observed,
                ),
            )
        )

    return ObserverPendingPrizeBatchBeliefs(
        pending_instance_ids,
        tuple(rows),
    )


def resolve_pending_instance_visibility(
    state: ObserverPendingPrizeBatchBeliefs,
    *,
    instance_id: str,
    visible_groups: Mapping[str, PrizeGroup],
) -> ObserverPendingPrizeBatchBeliefs:
    """Condition observers on one pending identity and remove that pending card."""

    index = state.pending_index(instance_id)
    observer_ids = {observer_id for observer_id, _belief in state.beliefs}
    if not set(visible_groups) <= observer_ids:
        raise ValueError("visible_groups contains an unknown observer")

    rows = []
    for observer_id, belief in state.beliefs:
        observed = visible_groups.get(observer_id, _UNOBSERVED)
        output: dict[
            tuple[
                PrizeGroup,
                tuple[PrizeGroup, ...],
                tuple[PrizeGroup, ...],
            ],
            float,
        ] = defaultdict(float)
        evidence = 0.0

        for (top_group, prizes, pending), probability in belief.masses:
            if observed is not _UNOBSERVED and pending[index] != observed:
                continue
            next_pending = pending[:index] + pending[index + 1 :]
            output[(top_group, prizes, next_pending)] += probability
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
                PendingPrizeBatchJointBelief(
                    belief.groups,
                    belief.face_up,
                    belief.pending_count - 1,
                    masses,
                ),
            )
        )

    remaining_ids = (
        state.pending_instance_ids[:index]
        + state.pending_instance_ids[index + 1 :]
    )
    return ObserverPendingPrizeBatchBeliefs(
        remaining_ids,
        tuple(rows),
    )


def project_completed_batch(
    state: ObserverPendingPrizeBatchBeliefs,
) -> ObserverTopPrizeBeliefs:
    """Project a fully resolved batch back to ordinary top/Prize beliefs."""

    if state.pending_instance_ids:
        raise ValueError("pending Prize batch is not fully resolved")

    rows = []
    for observer_id, belief in state.beliefs:
        if belief.pending_count != 0:
            raise AssertionError("pending geometry is inconsistent")
        masses = tuple(
            ((top_group, prizes), probability)
            for (top_group, prizes, pending), probability in belief.masses
            if not pending
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
