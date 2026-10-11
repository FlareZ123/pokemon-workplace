"""Exact Prize-invariance of pulling known non-targets before an observation.

U physically distinct initially unseen cards include one target and c
identified expendable non-target search sources. Place P uniform Prizes.
Search the deck for each of the c sources still unprized and remove it,
then inspect s uniform cards. When s <= U-c-P, target-hit incidence is
s/(U-c), independent of P.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from math import comb


def exact(unseen: int, prizes: int, removed_names: int, seen: int) -> Fraction:
    remaining_classes = unseen - removed_names
    if not (unseen >= 2 and 0 <= removed_names < unseen
            and 0 <= prizes < unseen and 1 <= seen <= remaining_classes - prizes):
        raise ValueError("Require enough unmarked deck cards for observation")
    return Fraction(seen, remaining_classes)


def enumerated(unseen: int, prizes: int, removed_names: int, seen: int) -> Fraction:
    """Exact physical Prize subsets, with hypergeometric target observation."""
    exact(unseen, prizes, removed_names, seen)
    target = removed_names
    hit = Fraction(0)
    worlds = 0
    for prize in combinations(range(unseen), prizes):
        excluded = set(prize)
        deck = [i for i in range(removed_names, unseen) if i not in excluded]
        if target in deck:
            hit += Fraction(seen, len(deck))
        worlds += 1
    return hit / worlds


def physical_observations(
    unseen: int, prizes: int, removed_names: int, seen: int,
) -> Fraction:
    """Independent physical Prize and observed-card subset enumeration."""
    exact(unseen, prizes, removed_names, seen)
    target = removed_names
    positive = total = 0
    for prize in combinations(range(unseen), prizes):
        excluded = set(prize)
        deck = tuple(i for i in range(removed_names, unseen) if i not in excluded)
        for inspected in combinations(deck, seen):
            total += 1
            positive += int(target in inspected)
    # Prize worlds must be equally weighted even though deck lengths differ.
    # This raw fraction is only valid if observed deck sizes are equal.
    return Fraction(positive, total)


def hypergeometric_by_prized_sources(
    unseen: int, prizes: int, removed_names: int, seen: int,
) -> Fraction:
    """Exact decomposition by J named search sources occupying Prize cards."""
    exact(unseen, prizes, removed_names, seen)
    m = unseen - removed_names
    value = Fraction(0)
    for j in range(max(0, prizes-m), min(removed_names, prizes)+1):
        prize_mass = Fraction(
            comb(removed_names, j)*comb(m, prizes-j), comb(unseen, prizes))
        unprized_unmarked = m-prizes+j
        assert unprized_unmarked >= seen
        survivor = Fraction(unprized_unmarked, m)
        hit_conditional = Fraction(seen, unprized_unmarked)
        value += prize_mass*survivor*hit_conditional
    return value
