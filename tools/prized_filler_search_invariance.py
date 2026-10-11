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
    """Independent equal-world Prize and observed-card subset enumeration."""
    exact(unseen, prizes, removed_names, seen)
    target = removed_names
    value = Fraction(0)
    worlds = 0
    for prize in combinations(range(unseen), prizes):
        excluded = set(prize)
        deck = tuple(i for i in range(removed_names, unseen) if i not in excluded)
        local_hits = local_total = 0
        for inspected in combinations(deck, seen):
            local_total += 1
            local_hits += int(target in inspected)
        value += Fraction(local_hits, local_total)
        worlds += 1
    return value / worlds


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


def target_count_probability(
    unseen: int, prizes: int, removed_names: int, seen: int,
    targets: int, hits: int,
) -> Fraction:
    """Exactly hits of targets distinct from named removed sources are observed."""
    exact(unseen, prizes, removed_names, seen)
    m = unseen-removed_names
    if not 0 <= targets <= m or not 0 <= hits <= min(targets,seen):
        raise ValueError("Invalid target multiplicity")
    return Fraction(
        (comb(targets,hits) * comb(m-targets,seen-hits)
         if 0 <= seen-hits <= m-targets else 0),
        comb(m,seen),
    )


def two_type_visibility(
    unseen: int, prizes: int, removed_names: int, seen: int,
    first_count: int, second_count: int,
) -> Fraction:
    """Observe at least one of each of two disjoint, unremoved target classes."""
    exact(unseen, prizes, removed_names, seen)
    m = unseen-removed_names
    if not (1 <= first_count and 1 <= second_count
            and first_count+second_count <= m):
        raise ValueError("Invalid target groups")

    def pick(top: int) -> int:
        return comb(top,seen) if top >= seen else 0

    return Fraction(
        (pick(m)-pick(m-first_count)-pick(m-second_count)
         +pick(m-first_count-second_count)),comb(m,seen),
    )


def physical_subset_distribution(
    unseen: int, prizes: int, removed_names: int, seen: int,
) -> dict[tuple[int, ...], Fraction]:
    """Enumerate physical Prize and Wish sets, weighting every Prize world equally."""
    exact(unseen, prizes, removed_names, seen)
    result: dict[tuple[int, ...], Fraction] = {}
    worlds = comb(unseen,prizes)
    for prize in combinations(range(unseen),prizes):
        prized = set(prize)
        deck = tuple(i for i in range(removed_names,unseen) if i not in prized)
        p_each = Fraction(1,worlds*comb(len(deck),seen))
        for observed in combinations(deck,seen):
            result[observed] = result.get(observed,Fraction(0))+p_each
    return result
