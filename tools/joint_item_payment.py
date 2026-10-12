"""Exact joint first-turn payability for three search Items in one deck.

Quick Ball, Ultra Ball, and Secret Box are individually playable when their
respective non-source hand-discard quotas (1, 2, 3) can be paid from F.
All other cards are protected, including other search Items. Sequential
events exclude fetched output, draws and any new discard targets.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from math import comb

NAMES = ("quick", "ultra", "secret")
COSTS = (1, 2, 3)
EVENTS = (
    "any_held", "any_payable", "two_individual", "two_sequential",
    "all_individual", "all_sequential",
    "quick_held", "ultra_held", "secret_held",
    "quick_payable", "ultra_payable", "secret_payable",
    "quick_ultra_individual", "quick_ultra_sequential",
    "quick_secret_individual", "quick_secret_sequential",
    "ultra_secret_individual", "ultra_secret_sequential",
)


def classify(b: int, q: int, u: int, s: int, f: int, protected: int) -> dict[str, bool]:
    del b, protected
    held = (q > 0, u > 0, s > 0)
    payable = tuple(h and f >= cost for h, cost in zip(held, COSTS))
    pairs = ((0, 1), (0, 2), (1, 2))
    individual = tuple(payable[i] and payable[j] for i, j in pairs)
    sequential = tuple(held[i] and held[j] and f >= COSTS[i] + COSTS[j]
                       for i, j in pairs)
    values = (
        any(held), any(payable), sum(payable) >= 2, any(sequential),
        all(payable), all(held) and f >= sum(COSTS),
        *held, *payable,
        individual[0], sequential[0],
        individual[1], sequential[1],
        individual[2], sequential[2],
    )
    return dict(zip(EVENTS, values))


def joint_item_payment(
    *, deck_size: int = 60, basics: int = 12,
    quick: int = 4, ultra: int = 4, secret: int = 1,
    filler: int = 8, opening: int = 7, prizes: int = 6,
) -> dict[str, Fraction]:
    """Condition on Basic-valid opening, promote one Basic, then draw once.

    After fixing the seven-card opener, uniformly dealing six Prize cards
    and subsequently drawing the top deck card marginalizes to one random
    draw from all nonopening cards. We do not peek at Prize contents.
    """
    counts = (basics, quick, ultra, secret, filler,
              deck_size - basics - quick - ultra - secret - filler)
    if any(type(x) is not int for x in (*counts, deck_size, opening, prizes)):
        raise TypeError("all sizes and counts must be integers")
    if (min(counts) < 0 or basics < 1 or quick < 1 or ultra < 1
            or secret != 1 or opening < 1 or prizes < 0
            or opening + prizes >= deck_size):
        raise ValueError("invalid deck or setup")
    accepted = comb(deck_size, opening) - comb(deck_size - basics, opening)
    if accepted == 0:
        raise ValueError("Basic-valid opening impossible")
    mass = {event: Fraction() for event in EVENTS}
    total = Fraction()
    for hand in product(*(range(min(n, opening) + 1) for n in counts)):
        if hand[0] == 0 or sum(hand) != opening:
            continue
        multiplicity = 1
        for n, held in zip(counts, hand):
            multiplicity *= comb(n, held)
        opener_mass = Fraction(multiplicity, accepted)
        for drawn_class, n in enumerate(counts):
            left = n - hand[drawn_class]
            if left == 0:
                continue
            final = list(hand)
            final[0] -= 1
            final[drawn_class] += 1
            weight = opener_mass * Fraction(left, deck_size - opening)
            total += weight
            for event, yes in classify(*final).items():
                if yes:
                    mass[event] += weight
    assert total == 1
    assert mass["any_held"] >= mass["any_payable"]
    assert mass["two_individual"] >= mass["two_sequential"]
    assert mass["all_individual"] >= mass["all_sequential"]
    for pair in ("quick_ultra", "quick_secret", "ultra_secret"):
        assert mass[f"{pair}_sequential"] <= mass[f"{pair}_individual"]
    return {
        "basic_valid": Fraction(accepted, comb(deck_size, opening)), **mass
    }


def brute_labeled(
    *, deck_size: int, basics: int, quick: int, ultra: int,
    secret: int, filler: int, opening: int, prizes: int,
) -> dict[str, Fraction]:
    """Independent physical-card oracle: enumerate openers, Prizes and draw."""
    labels = (["B"] * basics + ["Q"] * quick + ["U"] * ultra
              + ["S"] * secret + ["F"] * filler)
    labels += ["P"] * (deck_size - len(labels))
    indices = tuple(range(deck_size))
    totals = {event: 0 for event in EVENTS}
    worlds = 0
    for dealt in combinations(indices, opening):
        if not any(labels[i] == "B" for i in dealt):
            continue
        in_hand = set(dealt)
        unseen = tuple(i for i in indices if i not in in_hand)
        active = next(i for i in dealt if labels[i] == "B")
        in_hand.remove(active)
        for prize_cards in combinations(unseen, prizes):
            prize_set = set(prize_cards)
            for drawn in unseen:
                if drawn in prize_set:
                    continue
                hand = [
                    sum(labels[i] == kind for i in in_hand) + (labels[drawn] == kind)
                    for kind in ("B", "Q", "U", "S", "F", "P")
                ]
                present = classify(*hand)
                worlds += 1
                for event, yes in present.items():
                    totals[event] += yes
    return {event: Fraction(count, worlds) for event, count in totals.items()}
