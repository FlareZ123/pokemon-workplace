"""Exact finite belief-state policy for Arc Phone and Trekking Shoes feedback.

Arc Phone may exchange deck top with a chosen Prize after observing top.
Trekking Shoes observes and takes top into hand. If the card is not TARGET,
the next deck top is assumed to be known, target-irrelevant filler. Newly
retrieved Arc Phone and Trekking Shoes cards become usable immediately.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import permutations

Physical = tuple[tuple[str, ...], str]
Belief = tuple[tuple[Physical, Fraction], ...]


def normalize(states: dict[Physical, Fraction]) -> Belief:
    total = sum(states.values(), Fraction())
    if total <= 0:
        raise ValueError("empty belief")
    return tuple(sorted(
        ((world, mass / total) for world, mass in states.items() if mass),
        key=lambda row: row[0]
    ))


def exact_composition(prizes: tuple[str, ...], top: str = "F") -> Belief:
    layouts = set(permutations(prizes))
    mass = Fraction(1, len(layouts))
    return normalize({(layout, top): mass for layout in layouts})


def observations(belief: Belief) -> dict[str, tuple[Fraction, Belief]]:
    grouped: dict[str, dict[Physical, Fraction]] = defaultdict(dict)
    for world, mass in belief:
        grouped[world[1]][world] = mass
    return {
        top: (sum(states.values(), Fraction()), normalize(states))
        for top, states in grouped.items()
    }


def swap_prize_slot(belief: Belief, position: int) -> Belief:
    next_states: dict[Physical, Fraction] = defaultdict(Fraction)
    for (prizes, top), mass in belief:
        outgoing = prizes[position]
        after = prizes[:position] + (top,) + prizes[position + 1:]
        next_states[(after, outgoing)] += mass
    return normalize(next_states)


def take_top_with_shoes(belief: Belief) -> Belief:
    """Conditioned top has been seen; draw it, leaving a known filler top."""
    next_states: dict[Physical, Fraction] = defaultdict(Fraction)
    for (prizes, _), mass in belief:
        next_states[(prizes, "F")] += mass
    return normalize(next_states)


@lru_cache(maxsize=None)
def optimal_retrieval(belief: Belief, arc: int, shoes: int) -> Fraction:
    """Best same-turn probability of taking TARGET into hand."""
    if arc < 0 or shoes < 0:
        raise ValueError("negative Item inventory")
    if arc == 0 and shoes == 0:
        return Fraction()
    possible = [Fraction()]
    grouped = observations(belief)

    if shoes:
        expectation = Fraction()
        for top, (weight, conditioned) in grouped.items():
            if top == "T":
                continuation = Fraction(1)
            else:
                next_arc = arc + int(top == "A")
                next_shoes = shoes - 1 + int(top == "S")
                continuation = optimal_retrieval(
                    take_top_with_shoes(conditioned), next_arc, next_shoes
                )
            expectation += weight * continuation
        possible.append(expectation)

    if arc:
        expectation = Fraction()
        for _top, (weight, conditioned) in grouped.items():
            size = len(conditioned[0][0][0])
            # The exchange is optional, but observing top consumes Arc Phone.
            # Declining to swap can keep TARGET on top for a later Shoes.
            branches = [optimal_retrieval(conditioned, arc - 1, shoes)]
            branches.extend(
                optimal_retrieval(swap_prize_slot(conditioned, pos), arc - 1, shoes)
                for pos in range(size)
            )
            expectation += weight * max(branches)
        possible.append(expectation)

    return max(possible)


def alternating_policy(prizes: tuple[str, ...], arc: int, shoes: int) -> bool:
    """Independent physical policy: Arc -> Shoes, test the next slot."""
    board = list(prizes)
    top = "F"
    for position in range(len(board)):
        if not arc or not shoes:
            return False
        arc -= 1
        top, board[position] = board[position], top
        shoes -= 1
        if top == "T":
            return True
        arc += int(top == "A")
        shoes += int(top == "S")
        top = "F"
    return False


def free_top_information_after_swap(
    belief: Belief, arc: int, shoes: int, slot: int
) -> Fraction:
    """Counterfactual: freely observe the outgoing top after this Arc swap."""
    after = swap_prize_slot(belief, slot)
    return sum(
        (weight * optimal_retrieval(conditioned, arc - 1, shoes)
         for weight, conditioned in observations(after).values()),
        Fraction()
    )


if __name__ == "__main__":
    for groups, items in (
        (("T", "A", "S"), (2, 2)),
        (("T", "A", "S", "F"), (3, 2)),
        (("T", "A", "S", "F", "F", "F"), (3, 2)),
    ):
        prior = exact_composition(groups)
        print(len(groups), optimal_retrieval(prior, *items))
