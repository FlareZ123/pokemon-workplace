"""Exact hypergeometric draw-exposure probabilities under ordered deck prefix.

A position-aware world has a fixed current top, a modeled ordered suffix
prefix, and an exchangeable remaining suffix. Compute threshold hit
probabilities for the next d draws, optionally after a full-deck shuffle.
"""

from __future__ import annotations

from math import comb
from typing import Iterable

from prize_deck_prefix import PrizeDeckPrefixBelief
from prize_position_top_swap import CardGroup


def _hypergeom_at_least(
    *,
    total: int,
    successes: int,
    draws: int,
    minimum: int,
) -> float:
    if minimum <= 0:
        return 1.0
    if minimum > draws or minimum > successes:
        return 0.0
    denominator = comb(total, draws)
    return sum(
        comb(successes, n) * comb(total - successes, draws - n)
        for n in range(max(minimum, draws - (total - successes)), min(draws, successes) + 1)
    ) / denominator


def probability_target_exposure(
    belief: PrizeDeckPrefixBelief,
    *,
    targets: Iterable[CardGroup],
    draw_count: int,
    at_least: int = 1,
    shuffle_first: bool = False,
) -> float:
    """Probability next draw_count deck cards include enough target-group cards.

    If shuffle_first=True, the entire current deck is uniformly shuffled
    before drawing, overriding any previously known top/prefix ordering.
    """
    target_set = frozenset(targets)
    if not target_set:
        raise ValueError("at least one target group is required")
    if any(g is not None and g not in belief.groups for g in target_set):
        raise ValueError("unmodeled target group")
    if draw_count < 0 or at_least < 0:
        raise ValueError("draw and threshold counts must be nonnegative")

    labels: tuple[CardGroup, ...] = (*belief.groups, None)
    result = 0.0
    for world, mass in belief.masses:
        base = world.pool
        deck_size = 1 + sum(base.remainder)
        if draw_count > deck_size:
            raise ValueError("requested draws exceed physical deck")

        if shuffle_first:
            successes = (
                int(base.top in target_set)
                + sum(
                    count for label, count in zip(labels, base.remainder)
                    if label in target_set
                )
            )
            probability = _hypergeom_at_least(
                total=deck_size,
                successes=successes,
                draws=draw_count,
                minimum=at_least,
            )
        else:
            known = (base.top, *world.suffix_prefix)
            known_draws = min(draw_count, len(known))
            known_hits = sum(card in target_set for card in known[:known_draws])
            unknown_draws = draw_count - known_draws
            if unknown_draws:
                remainder_hits = sum(
                    count for label, count in zip(labels, base.remainder)
                    if label in target_set
                ) - sum(card in target_set for card in world.suffix_prefix)
                probability = _hypergeom_at_least(
                    total=sum(base.remainder) - len(world.suffix_prefix),
                    successes=remainder_hits,
                    draws=unknown_draws,
                    minimum=at_least - known_hits,
                )
            else:
                probability = float(known_hits >= at_least)

        result += mass * probability
    return result


def uniform_shuffle_value(
    belief: PrizeDeckPrefixBelief,
    *,
    targets: Iterable[CardGroup],
    draw_count: int,
    at_least: int = 1,
) -> float:
    """Hit-probability change from fully shuffling before the specified draws."""
    targets = tuple(targets)
    return probability_target_exposure(
        belief,
        targets=targets,
        draw_count=draw_count,
        at_least=at_least,
        shuffle_first=True,
    ) - probability_target_exposure(
        belief,
        targets=targets,
        draw_count=draw_count,
        at_least=at_least,
    )
