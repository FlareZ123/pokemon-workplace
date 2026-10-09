"""Bayesian public search signals coarser than the physically selected target.

Preserves the selected target group as a latent observer variable whenever
multiple card classes project to the same observed label. This prevents an
observer from learning a physical target class merely because the actor knows
which class was removed from the deck.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from math import isclose

from deck_search_shuffle_belief import condition_prize_composition
from deck_search_target_signal import (
    TargetSelectionPolicy,
    condition_on_revealed_search_target,
    prize_composition_key,
)
from private_search_latent_target_belief import (
    LatentPrivateTargetJointBelief,
    ObserverLatentPrivateTargetBeliefs,
    post_private_search_with_latent_target,
)
from prize_position_belief import PrizeGroup
from prize_slot_visibility import PrizeSlotVisibilityBelief


def condition_coarse_revealed_search(
    prizes: PrizeSlotVisibilityBelief,
    *,
    target_probability_by_composition: TargetSelectionPolicy,
    public_label_by_target: Mapping[str, str],
    observed_public_label: str,
    pre_search_group_pool_counts: Mapping[str, int],
    pre_search_pool_size: int,
) -> LatentPrivateTargetJointBelief:
    """Condition a coarse public label, then retain the exact target as latent.

    Policies may include a no-search label in Prize worlds that cannot produce
    the observed searched-card label. Such worlds have zero observation
    likelihood and are excluded before physical target removal.
    """
    projected_policy: dict[tuple[int, ...], dict[str, float]] = {}
    for composition, choices in target_probability_by_composition.items():
        if not choices:
            raise ValueError("target-selection policy row cannot be empty")
        if any(not 0.0 <= p <= 1.0 for p in choices.values()):
            raise ValueError("target-selection probabilities must lie in [0, 1]")
        if not isclose(sum(choices.values()), 1.0, rel_tol=0, abs_tol=1e-12):
            raise ValueError("target-selection probabilities must sum to one")

        projected: defaultdict[str, float] = defaultdict(float)
        for target, probability in choices.items():
            if target not in public_label_by_target:
                raise ValueError("every policy target needs a public label")
            label = public_label_by_target[target]
            if not label:
                raise ValueError("public label cannot be empty")
            projected[label] += probability
        projected_policy[composition] = dict(projected)

    conditioned = condition_on_revealed_search_target(
        prizes,
        target_probability_by_composition=projected_policy,
        observed_target=observed_public_label,
    )

    remaining_compositions = {
        prize_composition_key(state, conditioned.positions.groups)
        for state, probability in conditioned.positions.masses
        if probability > 0.0
    }
    conditional_targets = {}
    for composition in remaining_compositions:
        likelihood = projected_policy[composition][observed_public_label]
        conditional_targets[composition] = {
            target: probability / likelihood
            for target, probability in target_probability_by_composition[
                composition
            ].items()
            if public_label_by_target[target] == observed_public_label
            and probability > 0.0
        }

    return post_private_search_with_latent_target(
        conditioned,
        pre_search_group_pool_counts=pre_search_group_pool_counts,
        pre_search_pool_size=pre_search_pool_size,
        target_probability_by_composition=conditional_targets,
    )


def resolve_coarse_revealed_search_for_observers(
    prizes_by_observer: Sequence[tuple[str, PrizeSlotVisibilityBelief]],
    *,
    actor_id: str,
    actor_exact_prize_counts: Mapping[str, int],
    actor_selected_target_group: PrizeGroup,
    target_probability_by_composition: TargetSelectionPolicy,
    public_label_by_target: Mapping[str, str],
    observed_public_label: str,
    pre_search_group_pool_counts: Mapping[str, int],
    pre_search_pool_size: int,
) -> ObserverLatentPrivateTargetBeliefs:
    """Actor gets K1/exact target; others condition on a coarse public label."""
    if not prizes_by_observer:
        raise ValueError("at least one observer is required")

    ids = tuple(observer_id for observer_id, _prizes in prizes_by_observer)
    if len(ids) != len(set(ids)) or actor_id not in ids:
        raise ValueError("observer IDs must be unique and include the actor")
    reference = prizes_by_observer[0][1]
    for _observer_id, prizes in prizes_by_observer:
        if prizes.positions.groups != reference.positions.groups:
            raise ValueError("observer Prize groups must agree")
        if prizes.face_up != reference.face_up:
            raise ValueError("public Prize visibility must agree")

    if actor_selected_target_group not in public_label_by_target:
        raise ValueError("actor target has no public observation label")
    if public_label_by_target[actor_selected_target_group] != observed_public_label:
        raise ValueError("actor physical target disagrees with public observation")

    groups = reference.positions.groups
    actor_key = tuple(actor_exact_prize_counts[group] for group in groups)
    if target_probability_by_composition.get(actor_key, {}).get(
        actor_selected_target_group, 0.0
    ) <= 0.0:
        raise ValueError("actor selected a target impossible under the policy")

    output = []
    for observer_id, prizes in prizes_by_observer:
        if observer_id == actor_id:
            exact = condition_prize_composition(
                prizes, actor_exact_prize_counts
            )
            actor_policy = {actor_key: {actor_selected_target_group: 1.0}}
            belief = post_private_search_with_latent_target(
                exact,
                pre_search_group_pool_counts=pre_search_group_pool_counts,
                pre_search_pool_size=pre_search_pool_size,
                target_probability_by_composition=actor_policy,
            )
        else:
            belief = condition_coarse_revealed_search(
                prizes,
                target_probability_by_composition=target_probability_by_composition,
                public_label_by_target=public_label_by_target,
                observed_public_label=observed_public_label,
                pre_search_group_pool_counts=pre_search_group_pool_counts,
                pre_search_pool_size=pre_search_pool_size,
            )
        output.append((observer_id, belief))

    return ObserverLatentPrivateTargetBeliefs(tuple(output))
