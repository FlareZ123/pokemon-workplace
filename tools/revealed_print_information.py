"""Exact print-versus-name information in one publicly revealed deck search.

Model: unique physical card instances, uniformly random ordered Prize slots,
a deterministic legal search policy, and a uniform shuffled top afterwards.
Each emitted branch has equal probability conditional on search success.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations
from math import log2
from typing import Callable, Sequence


@dataclass(frozen=True)
class SearchCard:
    print_id: str
    name: str


@dataclass(frozen=True)
class RevealedSearchBranch:
    ordered_prize_ids: tuple[str, ...]
    selected_print_id: str
    selected_name: str
    top_print_id: str


SearchPolicy = Callable[[frozenset[str], frozenset[str]], str | None]
Observation = Callable[[RevealedSearchBranch], str]
Event = Callable[[RevealedSearchBranch], bool]


def enumerate_revealed_search_branches(
    cards: Sequence[SearchCard],
    prize_count: int,
    policy: SearchPolicy,
) -> tuple[RevealedSearchBranch, ...]:
    """Enumerate equiprobable successful-search/next-top labeled branches.

    A policy returning None represents no search target. Such initial worlds
    are excluded from returned branches; probabilities condition on success.
    """
    names_by_print = {card.print_id: card.name for card in cards}
    if len(names_by_print) != len(cards):
        raise ValueError("print IDs must be unique")
    if not 0 <= prize_count < len(cards) - 1:
        raise ValueError("search must leave a card to draw after Prizes")

    ids = tuple(names_by_print)
    branches: list[RevealedSearchBranch] = []
    for prizes in permutations(ids, prize_count):
        prize_set = frozenset(prizes)
        deck = tuple(card for card in ids if card not in prize_set)
        selected = policy(prize_set, frozenset(deck))
        if selected is None:
            continue
        if selected not in deck:
            raise ValueError("selection policy chose a card absent from deck")

        for top in deck:
            if top != selected:
                branches.append(
                    RevealedSearchBranch(
                        prizes, selected, names_by_print[selected], top
                    )
                )
    return tuple(branches)


def conditional_event_probability(
    branches: Sequence[RevealedSearchBranch],
    observation: Observation,
    observed_value: str,
    event: Event,
) -> Fraction:
    """Exact conditional probability from equal-mass completed branches."""
    matching = tuple(
        branch for branch in branches
        if observation(branch) == observed_value
    )
    if not matching:
        raise ValueError("observation has no positive-probability branches")
    return Fraction(sum(bool(event(branch)) for branch in matching), len(matching))


def binary_entropy(probability: Fraction) -> float:
    """Binary Shannon entropy in bits."""
    p = float(probability)
    return -sum(value * log2(value) for value in (p, 1 - p) if value)


def conditional_information_gain(
    branches: Sequence[RevealedSearchBranch],
    coarse_observation: Observation,
    coarse_value: str,
    fine_observation: Observation,
    event: Event,
) -> float:
    """I(binary event; fine observation | one given coarse observation).

    Both channels must describe the same physical branches. The fine channel
    may distinguish prints that the coarse channel merges under one name.
    """
    selected = tuple(
        branch for branch in branches
        if coarse_observation(branch) == coarse_value
    )
    if not selected:
        raise ValueError("coarse observation has zero probability")

    prior = Fraction(sum(bool(event(x)) for x in selected), len(selected))
    groups: dict[str, list[RevealedSearchBranch]] = defaultdict(list)
    for branch in selected:
        groups[fine_observation(branch)].append(branch)

    conditional_entropy = sum(
        len(group) / len(selected)
        * binary_entropy(
            Fraction(sum(bool(event(x)) for x in group), len(group))
        )
        for group in groups.values()
    )
    return binary_entropy(prior) - conditional_entropy
