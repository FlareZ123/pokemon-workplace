"""Bayesian signaling from a publicly revealed deck-search target."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isclose

from deck_search_shuffle_belief import (
    condition_prize_composition,
    post_shuffle_top_prize_belief,
)
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_position_belief import PrizeGroup, PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief


PrizeComposition = tuple[int, ...]
TargetSelectionPolicy = Mapping[
    PrizeComposition,
    Mapping[str, float],
]


def prize_composition_key(
    state: tuple[PrizeGroup, ...],
    groups: Sequence[str],
) -> PrizeComposition:
    """Project one positional Prize state to ordered modeled-group counts."""

    return tuple(
        sum(value == group for value in state)
        for group in groups
    )


def _validate_policy(
    prizes: PrizeSlotVisibilityBelief,
    target_probability_by_composition: TargetSelectionPolicy,
) -> None:
    groups = prizes.positions.groups
    supported = {
        prize_composition_key(state, groups)
        for state, probability in prizes.positions.masses
        if probability > 0.0
    }
    if not supported <= set(target_probability_by_composition):
        raise ValueError(
            "target-selection policy must cover every supported Prize composition"
        )

    for composition in supported:
        row = target_probability_by_composition[composition]
        if not row:
            raise ValueError("each supported composition needs a target policy")
        total = 0.0
        for target, probability in row.items():
            if not target:
                raise ValueError("target labels must be non-empty")
            if not 0.0 <= probability <= 1.0:
                raise ValueError("target probabilities must lie in [0, 1]")
            total += probability
        if not isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(
                "target probabilities must sum to one for each composition"
            )


def condition_on_revealed_search_target(
    prizes: PrizeSlotVisibilityBelief,
    *,
    target_probability_by_composition: TargetSelectionPolicy,
    observed_target: str,
) -> PrizeSlotVisibilityBelief:
    """Condition an observer on a target chosen after private deck inspection."""

    if not observed_target:
        raise ValueError("observed_target must be non-empty")
    _validate_policy(prizes, target_probability_by_composition)

    groups = prizes.positions.groups
    weighted = []
    evidence = 0.0
    for state, prior_probability in prizes.positions.masses:
        composition = prize_composition_key(state, groups)
        likelihood = target_probability_by_composition[composition].get(
            observed_target,
            0.0,
        )
        probability = prior_probability * likelihood
        if probability == 0.0:
            continue
        weighted.append((state, probability))
        evidence += probability

    if isclose(evidence, 0.0, rel_tol=0.0, abs_tol=1e-15):
        raise ValueError("observed target has zero probability under policy")

    positions = PrizePositionBelief(
        groups,
        prizes.positions.prize_count,
        tuple(
            (state, probability / evidence)
            for state, probability in weighted
        ),
    )
    return PrizeSlotVisibilityBelief(positions, prizes.face_up)


def resolve_revealed_search_target_shuffle(
    prizes_by_observer: Sequence[tuple[str, PrizeSlotVisibilityBelief]],
    *,
    actor_id: str,
    actor_exact_prize_counts: Mapping[str, int],
    target_probability_by_composition: TargetSelectionPolicy,
    observed_target: str,
    observed_target_group: PrizeGroup,
    pre_search_group_pool_counts: Mapping[str, int],
    pre_search_pool_size: int,
) -> ObserverTopPrizeBeliefs:
    """Resolve public target signaling, target removal, and the following shuffle.

    The actor already learned the exact Prize composition from full deck
    inspection. Other observers see only the publicly revealed selected target,
    so their Prize beliefs are conditioned on the actor's target-selection
    policy. One searched card is then removed from the deck-plus-Prize pool
    before the shuffled top distribution is derived.
    """

    if not prizes_by_observer:
        raise ValueError("at least one observer is required")

    observer_ids = tuple(observer_id for observer_id, _ in prizes_by_observer)
    if len(observer_ids) != len(set(observer_ids)):
        raise ValueError("observer IDs must be unique")
    if actor_id not in observer_ids:
        raise ValueError("actor_id must identify an observer")

    reference = prizes_by_observer[0][1]
    groups = reference.positions.groups
    for _observer_id, prizes in prizes_by_observer:
        if prizes.positions.groups != groups:
            raise ValueError("all observers must use the same modeled groups")
        if prizes.face_up != reference.face_up:
            raise ValueError("all observers must agree on public Prize visibility")

    if set(pre_search_group_pool_counts) != set(groups):
        raise ValueError(
            "pre_search_group_pool_counts must cover every modeled group"
        )
    if pre_search_pool_size <= reference.positions.prize_count + 1:
        raise ValueError("search must leave at least one card in deck")
    if sum(pre_search_group_pool_counts.values()) > pre_search_pool_size:
        raise ValueError("modeled pool counts exceed pre_search_pool_size")

    actor_key = tuple(
        actor_exact_prize_counts[group]
        for group in groups
    )
    if actor_key not in target_probability_by_composition:
        raise ValueError("target-selection policy does not cover actor state")
    actor_likelihood = target_probability_by_composition[actor_key].get(
        observed_target,
        0.0,
    )
    if isclose(actor_likelihood, 0.0, rel_tol=0.0, abs_tol=1e-15):
        raise ValueError("actor's observed target has zero policy probability")

    after_pool_counts = dict(pre_search_group_pool_counts)
    if observed_target_group is not None:
        if observed_target_group not in after_pool_counts:
            raise ValueError("observed_target_group must be modeled or None")
        if after_pool_counts[observed_target_group] < 1:
            raise ValueError("searched target group is absent from the pool")
        after_pool_counts[observed_target_group] -= 1
    after_pool_size = pre_search_pool_size - 1

    updated = []
    for observer_id, prizes in prizes_by_observer:
        if observer_id == actor_id:
            conditioned = condition_prize_composition(
                prizes,
                actor_exact_prize_counts,
            )
        else:
            conditioned = condition_on_revealed_search_target(
                prizes,
                target_probability_by_composition=(
                    target_probability_by_composition
                ),
                observed_target=observed_target,
            )

        updated.append(
            (
                observer_id,
                post_shuffle_top_prize_belief(
                    conditioned,
                    group_pool_counts=after_pool_counts,
                    pool_size=after_pool_size,
                ),
            )
        )

    return ObserverTopPrizeBeliefs(tuple(updated))



def resolve_revealed_search_targets_shuffle(
    prizes_by_observer: Sequence[tuple[str, PrizeSlotVisibilityBelief]],
    *,
    actor_id: str,
    actor_exact_prize_counts: Mapping[str, int],
    target_probability_by_composition: TargetSelectionPolicy,
    observed_target: str,
    removed_target_groups: Sequence[PrizeGroup],
    pre_search_group_pool_counts: Mapping[str, int],
    pre_search_pool_size: int,
) -> ObserverTopPrizeBeliefs:
    """Resolve one public multi-target selection event and following shuffle.

    observed_target remains an arbitrary public policy label. Callers may encode
    an ordered tuple, an unordered set, or another canonical selection label
    according to the card effect. removed_target_groups separately describes the
    physical modeled groups removed from the deck-plus-Prize pool.
    """

    if not prizes_by_observer:
        raise ValueError("at least one observer is required")

    observer_ids = tuple(observer_id for observer_id, _ in prizes_by_observer)
    if len(observer_ids) != len(set(observer_ids)):
        raise ValueError("observer IDs must be unique")
    if actor_id not in observer_ids:
        raise ValueError("actor_id must identify an observer")
    if not observed_target:
        raise ValueError("observed_target must be non-empty")

    reference = prizes_by_observer[0][1]
    groups = reference.positions.groups
    for _observer_id, prizes in prizes_by_observer:
        if prizes.positions.groups != groups:
            raise ValueError("all observers must use the same modeled groups")
        if prizes.face_up != reference.face_up:
            raise ValueError("all observers must agree on public Prize visibility")

    if set(pre_search_group_pool_counts) != set(groups):
        raise ValueError(
            "pre_search_group_pool_counts must cover every modeled group"
        )
    removed = tuple(removed_target_groups)
    after_pool_size = pre_search_pool_size - len(removed)
    if after_pool_size <= reference.positions.prize_count:
        raise ValueError("search must leave at least one card in deck")
    if sum(pre_search_group_pool_counts.values()) > pre_search_pool_size:
        raise ValueError("modeled pool counts exceed pre_search_pool_size")

    actor_key = tuple(actor_exact_prize_counts[group] for group in groups)
    if actor_key not in target_probability_by_composition:
        raise ValueError("target-selection policy does not cover actor state")
    actor_likelihood = target_probability_by_composition[actor_key].get(
        observed_target,
        0.0,
    )
    if isclose(actor_likelihood, 0.0, rel_tol=0.0, abs_tol=1e-15):
        raise ValueError("actor's observed target has zero policy probability")

    after_pool_counts = dict(pre_search_group_pool_counts)
    for target_group in removed:
        if target_group is None:
            continue
        if target_group not in after_pool_counts:
            raise ValueError("removed target group must be modeled or None")
        if after_pool_counts[target_group] < 1:
            raise ValueError("removed target group is absent from the pool")
        after_pool_counts[target_group] -= 1

    updated = []
    for observer_id, prizes in prizes_by_observer:
        if observer_id == actor_id:
            conditioned = condition_prize_composition(
                prizes,
                actor_exact_prize_counts,
            )
        else:
            conditioned = condition_on_revealed_search_target(
                prizes,
                target_probability_by_composition=target_probability_by_composition,
                observed_target=observed_target,
            )
        updated.append(
            (
                observer_id,
                post_shuffle_top_prize_belief(
                    conditioned,
                    group_pool_counts=after_pool_counts,
                    pool_size=after_pool_size,
                ),
            )
        )

    return ObserverTopPrizeBeliefs(tuple(updated))
