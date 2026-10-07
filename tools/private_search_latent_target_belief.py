"""Retain a private unrestricted-search target as latent observer evidence."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from math import isclose

from deck_search_shuffle_belief import condition_prize_composition
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from private_search_target_belief import PrivateTargetPolicy
from prize_position_belief import PrizeGroup
from prize_slot_visibility import PrizeSlotVisibilityBelief
from prize_top_swap_belief import TopPrizeJointBelief


PrizeComposition = tuple[int, ...]


def _composition(
    state: tuple[PrizeGroup, ...],
    groups: Sequence[str],
) -> PrizeComposition:
    return tuple(
        sum(value == group for value in state)
        for group in groups
    )


@dataclass(frozen=True)
class LatentPrivateTargetJointBelief:
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
            raise ValueError("belief must have support")
        total = 0.0
        modeled = set(self.groups)
        for (top_group, prizes, target_group), probability in self.masses:
            if len(prizes) != len(self.face_up):
                raise ValueError("Prize state must align with visibility")
            if probability < 0.0:
                raise ValueError("probabilities must be non-negative")
            values = (top_group, target_group) + prizes
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
            for (top_group, _prizes, _target), probability in self.masses
            if top_group == group
        )

    def target_probability(self, group: PrizeGroup) -> float:
        return sum(
            probability
            for (_top, _prizes, target_group), probability in self.masses
            if target_group == group
        )

    def prize_probability_at(self, position: int, group: PrizeGroup) -> float:
        if not 0 <= position < len(self.face_up):
            raise IndexError("Prize position out of range")
        return sum(
            probability
            for (_top, prizes, _target), probability in self.masses
            if prizes[position] == group
        )

    def project_hidden_target(self) -> TopPrizeJointBelief:
        output: dict[
            tuple[PrizeGroup, tuple[PrizeGroup, ...]],
            float,
        ] = defaultdict(float)
        for (top_group, prizes, _target), probability in self.masses:
            output[(top_group, prizes)] += probability
        return TopPrizeJointBelief(
            self.groups,
            self.face_up,
            tuple(sorted(output.items(), key=lambda row: repr(row[0]))),
        )

    def condition_target(
        self,
        observed_group: PrizeGroup,
    ) -> "LatentPrivateTargetJointBelief":
        evidence = self.target_probability(observed_group)
        if evidence == 0.0:
            raise ValueError("target observation has zero probability")
        return LatentPrivateTargetJointBelief(
            self.groups,
            self.face_up,
            tuple(
                (hidden_state, probability / evidence)
                for hidden_state, probability in self.masses
                if hidden_state[2] == observed_group
            ),
        )


@dataclass(frozen=True)
class ObserverLatentPrivateTargetBeliefs:
    beliefs: tuple[tuple[str, LatentPrivateTargetJointBelief], ...]

    def __post_init__(self) -> None:
        if not self.beliefs:
            raise ValueError("at least one observer is required")
        ids = tuple(observer_id for observer_id, _belief in self.beliefs)
        if len(ids) != len(set(ids)):
            raise ValueError("observer IDs must be unique")

    def belief_for(self, observer_id: str) -> LatentPrivateTargetJointBelief:
        for current_id, belief in self.beliefs:
            if current_id == observer_id:
                return belief
        raise KeyError(observer_id)

    def project_hidden_target(self) -> ObserverTopPrizeBeliefs:
        return ObserverTopPrizeBeliefs(
            tuple(
                (observer_id, belief.project_hidden_target())
                for observer_id, belief in self.beliefs
            )
        )


def post_private_search_with_latent_target(
    prizes: PrizeSlotVisibilityBelief,
    *,
    pre_search_group_pool_counts: Mapping[str, int],
    pre_search_pool_size: int,
    target_probability_by_composition: PrivateTargetPolicy,
) -> LatentPrivateTargetJointBelief:
    """Preserve the selected target group while sampling the shuffled top."""

    groups = prizes.positions.groups
    prize_count = prizes.positions.prize_count
    if set(pre_search_group_pool_counts) != set(groups):
        raise ValueError("pool counts must cover every modeled group")

    filler_pool = (
        pre_search_pool_size - sum(pre_search_group_pool_counts.values())
    )
    output: dict[
        tuple[PrizeGroup, tuple[PrizeGroup, ...], PrizeGroup],
        float,
    ] = defaultdict(float)

    for prize_state, prize_probability in prizes.positions.masses:
        composition = _composition(prize_state, groups)
        policy = target_probability_by_composition.get(composition)
        if policy is None:
            raise ValueError("target policy must cover every Prize composition")

        prized_counts = {
            group: sum(value == group for value in prize_state)
            for group in groups
        }
        filler_prized = sum(value is None for value in prize_state)
        deck_counts = {
            group: pre_search_group_pool_counts[group] - prized_counts[group]
            for group in groups
        }
        filler_deck = filler_pool - filler_prized
        deck_size = pre_search_pool_size - prize_count

        for target_group, target_probability in policy.items():
            if target_probability == 0.0:
                continue
            available = (
                filler_deck
                if target_group is None
                else deck_counts[target_group]
            )
            if available <= 0:
                raise ValueError("target policy selects an absent group")

            remaining_counts = dict(deck_counts)
            remaining_filler = filler_deck
            if target_group is None:
                remaining_filler -= 1
            else:
                remaining_counts[target_group] -= 1

            remaining_size = deck_size - 1
            for top_group, count in remaining_counts.items():
                if count:
                    output[(top_group, prize_state, target_group)] += (
                        prize_probability
                        * target_probability
                        * count
                        / remaining_size
                    )
            if remaining_filler:
                output[(None, prize_state, target_group)] += (
                    prize_probability
                    * target_probability
                    * remaining_filler
                    / remaining_size
                )

    return LatentPrivateTargetJointBelief(
        groups,
        prizes.face_up,
        tuple(sorted(output.items(), key=lambda row: repr(row[0]))),
    )


def resolve_private_search_with_latent_target_for_observers(
    prizes_by_observer: Sequence[tuple[str, PrizeSlotVisibilityBelief]],
    *,
    actor_id: str,
    actor_exact_prize_counts: Mapping[str, int],
    actor_selected_target_group: PrizeGroup,
    pre_search_group_pool_counts: Mapping[str, int],
    pre_search_pool_size: int,
    target_probability_by_composition: PrivateTargetPolicy,
) -> ObserverLatentPrivateTargetBeliefs:
    """Give the actor exact target knowledge while others retain target latency."""

    ids = tuple(observer_id for observer_id, _prizes in prizes_by_observer)
    if actor_id not in ids:
        raise ValueError("actor_id must identify an observer")

    groups = prizes_by_observer[0][1].positions.groups
    actor_key = tuple(actor_exact_prize_counts[group] for group in groups)

    rows = []
    for observer_id, prizes in prizes_by_observer:
        if observer_id == actor_id:
            exact = condition_prize_composition(
                prizes,
                actor_exact_prize_counts,
            )
            policy: PrivateTargetPolicy = {
                actor_key: {actor_selected_target_group: 1.0}
            }
            belief = post_private_search_with_latent_target(
                exact,
                pre_search_group_pool_counts=pre_search_group_pool_counts,
                pre_search_pool_size=pre_search_pool_size,
                target_probability_by_composition=policy,
            )
        else:
            belief = post_private_search_with_latent_target(
                prizes,
                pre_search_group_pool_counts=pre_search_group_pool_counts,
                pre_search_pool_size=pre_search_pool_size,
                target_probability_by_composition=target_probability_by_composition,
            )
        rows.append((observer_id, belief))

    return ObserverLatentPrivateTargetBeliefs(tuple(rows))


def reveal_private_target_to_observers(
    state: ObserverLatentPrivateTargetBeliefs,
    *,
    observed_group: PrizeGroup,
    observer_ids: tuple[str, ...],
) -> ObserverLatentPrivateTargetBeliefs:
    """Condition selected observers when the exact searched card is revealed."""

    selected = set(observer_ids)
    known = {observer_id for observer_id, _belief in state.beliefs}
    if not selected <= known:
        raise ValueError("unknown observer in reveal set")

    return ObserverLatentPrivateTargetBeliefs(
        tuple(
            (
                observer_id,
                belief.condition_target(observed_group)
                if observer_id in selected
                else belief,
            )
            for observer_id, belief in state.beliefs
        )
    )
