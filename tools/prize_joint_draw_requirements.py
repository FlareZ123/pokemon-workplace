"""Joint per-group draw requirements under a known prefix and hypergeom suffix.

For disjoint strategic card groups, compute the probability that the next d
draws simultaneously meet each group's minimum count. Each physical world's
unknown suffix has a multivariate hypergeometric distribution.
"""

from __future__ import annotations

from itertools import product
from math import comb, prod
from typing import Mapping

from prize_deck_prefix import PrizeDeckPrefixBelief
from prize_position_top_swap import CardGroup


def _multivariate_hypergeom_tail(
    *,
    total: int,
    group_counts: tuple[int, ...],
    required: tuple[int, ...],
    draws: int,
) -> float:
    """P(all group thresholds met) from an exchangeable finite population."""
    if all(n <= 0 for n in required):
        return 1.0
    if draws < 0 or draws > total:
        raise ValueError("invalid suffix draw count")
    others = total - sum(group_counts)
    if others < 0:
        raise ValueError("modeled groups exceed population")
    ranges = [
        range(max(0, minimum), min(count, draws) + 1)
        for count, minimum in zip(group_counts, required)
    ]
    ways = 0
    for sample_counts in product(*ranges):
        other_draws = draws - sum(sample_counts)
        if 0 <= other_draws <= others:
            ways += (
                prod(comb(pool_count, taken) for pool_count, taken in zip(
                    group_counts, sample_counts
                ))
                * comb(others, other_draws)
            )
    return ways / comb(total, draws)


def probability_joint_draw_requirements(
    belief: PrizeDeckPrefixBelief,
    *,
    requirements: Mapping[CardGroup, int],
    draw_count: int,
    shuffle_first: bool = False,
) -> float:
    """Probability next draw_count cards meet every per-group minimum.

    A target group may occur in only one requirement (mapping keys are
    unique). Card groups are mutually exclusive, unlike overlapping category
    tags. The deeper deck suffix is assumed exchangeable.
    """
    if draw_count < 0:
        raise ValueError("draw count must be nonnegative")
    if any(g is not None and g not in belief.groups for g in requirements):
        raise ValueError("requirement includes unmodeled group")
    if any(not isinstance(n, int) or n < 0 for n in requirements.values()):
        raise ValueError("minimum counts must be nonnegative integers")

    targets = tuple(requirements)
    threshold = tuple(requirements.values())
    labels: tuple[CardGroup, ...] = (*belief.groups, None)
    probability = 0.0
    for world, mass in belief.masses:
        base = world.pool
        deck_size = 1 + sum(base.remainder)
        if draw_count > deck_size:
            raise ValueError("requested draws exceed physical deck")

        if shuffle_first:
            group_counts = tuple(
                base.remainder[labels.index(group)] + int(base.top == group)
                for group in targets
            )
            term = _multivariate_hypergeom_tail(
                total=deck_size,
                group_counts=group_counts,
                required=threshold,
                draws=draw_count,
            )
        else:
            known = (base.top, *world.suffix_prefix)
            known_draws = min(draw_count, len(known))
            known_seen = known[:known_draws]
            unknown_count = draw_count - known_draws
            unknown_pool_size = sum(base.remainder) - len(world.suffix_prefix)
            unknown_groups = tuple(
                base.remainder[labels.index(group)]
                - world.suffix_prefix.count(group)
                for group in targets
            )
            needed = tuple(
                minimum - known_seen.count(group)
                for group, minimum in zip(targets, threshold)
            )
            term = _multivariate_hypergeom_tail(
                total=unknown_pool_size,
                group_counts=unknown_groups,
                required=needed,
                draws=unknown_count,
            )
        probability += mass * term
    return probability
