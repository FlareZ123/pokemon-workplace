"""Exact draw-window feasibility with per-card alternative or multi-axis roles.

A card type has a finite set of allowed contribution vectors. Each physical
drawn copy can choose at most one profile. A profile may contribute on multiple
axes simultaneously when the modeled effect actually allows it.
"""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from itertools import product
from math import comb, prod
from typing import Mapping

from prize_deck_prefix import PrizeDeckPrefixBelief
from prize_position_top_swap import CardGroup

Profile = tuple[int, ...]
Signature = tuple[Profile, ...]


@lru_cache(maxsize=None)
def _can_allocate(
    required: tuple[int, ...],
    groups: tuple[tuple[Signature, int], ...],
) -> bool:
    reachable: set[tuple[int, ...]] = {(0,) * len(required)}
    for signature, count in groups:
        for _ in range(count):
            next_reachable = set(reachable)  # Ignore a drawn card.
            for state in reachable:
                for option in signature:
                    next_reachable.add(tuple(
                        min(required[i], state[i] + option[i])
                        for i in range(len(required))
                    ))
            reachable = next_reachable
    return required in reachable


def _world_probability(
    known: tuple[CardGroup, ...],
    unknown: tuple[tuple[CardGroup, int], ...],
    *,
    draw_unknown: int,
    requirements: tuple[int, ...],
    signatures: Mapping[CardGroup, Signature],
) -> float:
    buckets: dict[Signature, list[int]] = defaultdict(lambda: [0, 0])
    for group in known:
        buckets[signatures.get(group, ())][0] += 1
    for group, count in unknown:
        buckets[signatures.get(group, ())][1] += count

    active = tuple(
        (signature, counts[0], counts[1])
        for signature, counts in buckets.items()
        if signature
    )
    unknown_size = sum(count for _, count in unknown)
    unused = unknown_size - sum(count for _, _, count in active)
    denominator = comb(unknown_size, draw_unknown)
    success_ways = 0

    ranges = tuple(
        range(min(count, draw_unknown) + 1)
        for _, _, count in active
    )
    for draws_by_type in product(*ranges):
        unmodeled_draws = draw_unknown - sum(draws_by_type)
        if not 0 <= unmodeled_draws <= unused:
            continue
        chosen = tuple(
            (signature, known_count + taken)
            for (signature, known_count, _), taken in zip(
                active, draws_by_type
            )
        )
        if not _can_allocate(requirements, chosen):
            continue
        success_ways += (
            prod(
                comb(group_count, taken)
                for (_, _, group_count), taken in zip(active, draws_by_type)
            )
            * comb(unused, unmodeled_draws)
        )
    return success_ways / denominator


def probability_allocatable_draws(
    belief: PrizeDeckPrefixBelief,
    *,
    requirements: tuple[int, ...],
    profiles_by_group: Mapping[CardGroup, tuple[Profile, ...]],
    draw_count: int,
    shuffle_first: bool = False,
) -> float:
    """Chance cards exposed in the window can satisfy all resource channels."""
    if not requirements or any(
        not isinstance(n, int) or n < 0 for n in requirements
    ):
        raise ValueError("requirements must be nonempty nonnegative integers")
    if draw_count < 0:
        raise ValueError("draw count must be nonnegative")

    labels: tuple[CardGroup, ...] = (*belief.groups, None)
    signatures: dict[CardGroup, Signature] = {}
    for group, options in profiles_by_group.items():
        if group not in labels:
            raise ValueError("unmodeled card group in profiles")
        for option in options:
            if len(option) != len(requirements) or any(
                not isinstance(n, int) or n < 0 for n in option
            ):
                raise ValueError("profile vector has invalid dimensions or counts")
        signatures[group] = tuple(sorted(set(options)))

    result = 0.0
    for world, mass in belief.masses:
        base = world.pool
        if draw_count > 1 + sum(base.remainder):
            raise ValueError("requested draw window exceeds physical deck")

        if shuffle_first:
            known: tuple[CardGroup, ...] = ()
            unknown_counts = list(base.remainder)
            unknown_counts[labels.index(base.top)] += 1
            draw_unknown = draw_count
        else:
            positions = (base.top, *world.suffix_prefix)
            known = positions[:min(draw_count, len(positions))]
            draw_unknown = draw_count - len(known)
            unknown_counts = list(base.remainder)
            for card in world.suffix_prefix:
                unknown_counts[labels.index(card)] -= 1

        unknown = tuple(zip(labels, unknown_counts))
        result += mass * _world_probability(
            known, unknown, draw_unknown=draw_unknown,
            requirements=requirements, signatures=signatures,
        )
    return result
