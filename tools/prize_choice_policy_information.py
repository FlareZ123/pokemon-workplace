"""Information-set-adapted public choice policies for Prize positions.

A player may condition a stochastic strategy on its own observations, not on
unobserved hidden card placements. Each possible world is assigned an
information-set label; a policy maps that label to a distribution over public
choices. This construction enforces behavioral strategy measurability.
"""

from __future__ import annotations

from collections.abc import Hashable, Mapping

from prize_position_top_swap import PrizePositionTopBelief, World


def is_world_likelihood_admissible(
    belief: PrizePositionTopBelief,
    information_by_world: Mapping[World, Hashable],
    likelihood_by_world: Mapping[World, float],
) -> bool:
    """Check whether P(observed action | world) uses only actor information."""
    support = {world for world, _ in belief.masses}
    if set(information_by_world) != support or set(likelihood_by_world) != support:
        raise ValueError("information and likelihoods must cover exactly the support")
    if any(not 0 <= p <= 1 for p in likelihood_by_world.values()):
        raise ValueError("action likelihoods must be valid probabilities")
    values: dict[Hashable, float] = {}
    for world in support:
        information = information_by_world[world]
        probability = likelihood_by_world[world]
        if information in values and abs(values[information] - probability) > 1e-12:
            return False
        values[information] = probability
    return True


def condition_on_admissible_position_choice(
    belief: PrizePositionTopBelief,
    *,
    actor_information_by_world: Mapping[World, Hashable],
    policy_by_information: Mapping[Hashable, Mapping[int, float]],
    chosen_position: int,
) -> PrizePositionTopBelief:
    """Bayesian update on observing one face-down-position selection.

    The actor's epistemic information set determines the entire stochastic
    choice distribution over the currently eligible Prize positions.
    """
    if not 0 <= chosen_position < belief.prize_count:
        raise IndexError("chosen Prize position out of range")
    if belief.face_up[chosen_position]:
        raise ValueError("cannot select face-up Prize position")

    worlds = {world for world, _ in belief.masses}
    if set(actor_information_by_world) != worlds:
        raise ValueError("actor information mapping must cover exactly the support")
    classes = set(actor_information_by_world.values())
    if set(policy_by_information) != classes:
        raise ValueError("every information class needs a policy")

    available = {i for i, face_up in enumerate(belief.face_up) if not face_up}
    for probabilities in policy_by_information.values():
        if set(probabilities) != available:
            raise ValueError("policy must specify every eligible physical position")
        if any(not 0 <= value <= 1 for value in probabilities.values()):
            raise ValueError("selection probabilities must be in [0,1]")
        if abs(sum(probabilities.values()) - 1) > 1e-12:
            raise ValueError("choice probabilities must sum to one")

    likelihood = {
        world: policy_by_information[actor_information_by_world[world]][chosen_position]
        for world in worlds
    }
    return belief.condition_on_public_world_choice(likelihood)
