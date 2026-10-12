"""Exact paid Quick Ball extension of the 2026 Aichi Shadow Rider launch.

Categories: Radiant, Shadow Rider VMAX, Mysterious Treasure, Hisuian
Heavy Ball, Quick Ball, other starting Basics, Psychic Energy, remaining cards.
The policy variants are hypothetical resource-preservation rules.
"""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb, prod

COUNTS = (1, 4, 4, 1, 1, 13, 11, 25)


@lru_cache(None)
def allocate(total: int, caps: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    if len(caps) == 1:
        return ((total,),) if 0 <= total <= caps[0] else ()
    return tuple(
        (a,) + b
        for a in range(min(total, caps[0]) + 1)
        for b in allocate(total - a, caps[1:])
    )


def outcome(
    opening: tuple[int, ...],
    prize: tuple[int, ...],
    drawn: int,
    counts: tuple[int, ...] = COUNTS,
) -> str:
    if opening[0] + opening[5] == 0:
        return "reject"
    if opening[5] == 0:
        return "no_alternate_basic"
    hand = tuple(opening[i] + (drawn == i) for i in range(len(counts)))
    deck = tuple(
        counts[i] - opening[i] - prize[i] - (drawn == i)
        for i in range(len(counts))
    )
    if deck[1] < 2:
        return "vm_depleted"
    if hand[0]:
        return "direct"
    if hand[3] and prize[0]:
        return "heavy"
    if not deck[0]:
        return "no_radiant"
    if hand[2]:
        if hand[6]:
            return "treasure_energy_paid"
        if hand[2] >= 2 or hand[4]:
            return "treasure_ball_paid"
        return "treasure_unrestricted_only"
    if hand[4]:
        return "quick_energy_paid" if hand[6] else "quick_unrestricted_only"
    return "no_search_source"


def exact(
    counts: tuple[int, ...] = COUNTS,
    opening_n: int = 7,
    prizes_n: int = 6,
) -> dict[str, Fraction]:
    """Exact category-multiplicity, Prize and natural-draw enumeration."""
    n = sum(counts)
    accepted = comb(n, opening_n) - comb(
        n - counts[0] - counts[5], opening_n
    )
    denominator = accepted * comb(n - opening_n, prizes_n) * (
        n - opening_n - prizes_n
    )
    tally: Counter[str] = Counter()
    for op in allocate(opening_n, counts):
        if not op[0] and not op[5]:
            continue
        ways_op = prod(comb(x, y) for x, y in zip(counts, op))
        remaining = tuple(x - y for x, y in zip(counts, op))
        for pr in allocate(prizes_n, remaining):
            ways = ways_op * prod(comb(x, y) for x, y in zip(remaining, pr))
            post_prize = tuple(x - y for x, y in zip(remaining, pr))
            for drawn, copies in enumerate(post_prize):
                if copies:
                    tally[outcome(op, pr, drawn, counts)] += ways * copies
    assert sum(tally.values()) == denominator
    return {key: Fraction(value, denominator) for key, value in tally.items()}


def policy(tally: dict[str, Fraction], kind: str) -> Fraction:
    routes = ["direct", "heavy"]
    if kind == "unrestricted":
        routes += [
            "treasure_energy_paid", "treasure_ball_paid",
            "treasure_unrestricted_only", "quick_energy_paid",
            "quick_unrestricted_only",
        ]
    elif kind == "energy":
        routes += ["treasure_energy_paid", "quick_energy_paid"]
    elif kind == "energy_or_extra_search":
        routes += [
            "treasure_energy_paid", "treasure_ball_paid",
            "quick_energy_paid",
        ]
    else:
        raise ValueError(kind)
    return sum((tally.get(key, Fraction()) for key in routes), Fraction())


def labeled_toy(
    counts: tuple[int, ...], opening_n: int = 3, prizes_n: int = 2
) -> dict[str, Fraction]:
    """Independent physical-instance oracle using actual card movements."""
    cards = [i for i, copies in enumerate(counts) for _ in range(copies)]
    n = len(cards)
    total = 0
    tally: Counter[str] = Counter()
    available_indices = set(range(n))
    for opener in combinations(range(n), opening_n):
        opener_types = [cards[i] for i in opener]
        if 0 not in opener_types and 5 not in opener_types:
            continue
        remaining = available_indices.difference(opener)
        for prize in combinations(remaining, prizes_n):
            prize_types = [cards[i] for i in prize]
            for draw in remaining.difference(prize):
                total += 1
                hand = opener_types + [cards[draw]]
                deck = [
                    cards[i] for i in remaining.difference(prize)
                    if i != draw
                ]
                if 5 not in opener_types:
                    result = "no_alternate_basic"
                elif deck.count(1) < 2:
                    result = "vm_depleted"
                elif 0 in hand:
                    result = "direct"
                elif 3 in hand and 0 in prize_types:
                    result = "heavy"
                elif 0 not in deck:
                    result = "no_radiant"
                elif 2 in hand:
                    if 6 in hand:
                        result = "treasure_energy_paid"
                    elif hand.count(2) > 1 or 4 in hand:
                        result = "treasure_ball_paid"
                    else:
                        result = "treasure_unrestricted_only"
                elif 4 in hand:
                    result = (
                        "quick_energy_paid" if 6 in hand
                        else "quick_unrestricted_only"
                    )
                else:
                    result = "no_search_source"
                tally[result] += 1
    return {key: Fraction(value, total) for key, value in tally.items()}
