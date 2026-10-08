"""Exact accepted-opening access screen for Ticket plus Prize inspection Items.

Condition on designated singleton nonstarters having a particular exact K1
zone status: p in the original Prizes, m in the deck after pre-reset draws.
All remaining cards are exchangeable once those known identity constraints
and an accepted opening are imposed. This models only natural hand/draw access.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class TicketAccess:
    witness_probability_given_valid_opening: Fraction
    item_access_given_witness: Fraction
    joint_probability_given_valid_opening: Fraction


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def compositions(total: int, bounds: tuple[int, ...]):
    if len(bounds) == 1:
        if 0 <= total <= bounds[0]:
            yield (total,)
        return
    for n in range(min(total, bounds[0]) + 1):
        for tail in compositions(total - n, bounds[1:]):
            yield (n,) + tail


def analyze_natural_access(
    *,
    deck_size: int = 60,
    starters: int = 14,
    tickets: int = 4,
    town_maps: int = 4,
    original_prized_singletons: int = 1,
    original_deck_singletons: int = 2,
    opening_hand: int = 7,
    prize_cards: int = 6,
    later_draws: int = 1,
    needed_tickets: int = 3,
    needed_maps: int = 2,
) -> TicketAccess:
    """Compute natural joint Item access conditional on a specified K1 witness.

    The named singleton cards are non-starters and excluded from the accepted
    hand. The first group must be in initial Prizes; the second group must be
    in the deck after draws. Prize selection and later draws are uniformly
    random, without card-specific search or replacement. A player can first
    observe the exact zones after the draws without changing those zones.
    """
    n, h, p, d = deck_size, opening_hand, prize_cards, later_draws
    prized, live = original_prized_singletons, original_deck_singletons
    q = prized + live
    filler = n - q - starters - tickets - town_maps
    if min(n, starters, tickets, town_maps, prized, live, h, p, d, needed_tickets, needed_maps, filler) < 0:
        raise ValueError("counts must be nonnegative and fit the deck")
    if starters < 1 or h < 1 or n - h - p < d or prized > p or q + h > n:
        raise ValueError("the specified K1 witness and valid opener must be feasible")
    denominator_valid_hands = choose(n, h) - choose(n - starters, h)
    qualifying_hands = choose(n - q, h) - choose(n - q - starters, h)
    if denominator_valid_hands == 0 or qualifying_hands == 0:
        raise ValueError("accepted opener with the named K1 witness is impossible")

    witness = (
        Fraction(qualifying_hands, denominator_valid_hands)
        * Fraction(choose(n - h - q, p - prized), choose(n - h, p))
        * Fraction(choose(n - h - p - live, d), choose(n - h - p, d))
    )

    categories = (tickets, town_maps, starters, filler)
    n_other = n - q
    accepted_other = Fraction(qualifying_hands, choose(n_other, h))
    access = Fraction(0)
    for hand in compositions(h, categories):
        if not hand[2]:
            continue
        ways_hand = 1
        for available, count in zip(categories, hand):
            ways_hand *= choose(available, count)
        mass_hand = Fraction(ways_hand, choose(n_other, h)) / accepted_other
        remaining = tuple(a - b for a, b in zip(categories, hand))
        for seen in compositions(d, remaining):
            if hand[0] + seen[0] < needed_tickets or hand[1] + seen[1] < needed_maps:
                continue
            ways_draw = 1
            for available, count in zip(remaining, seen):
                ways_draw *= choose(available, count)
            access += mass_hand * Fraction(ways_draw, choose(n_other - h, d))

    return TicketAccess(witness, access, witness * access)


if __name__ == "__main__":
    for k in (1, 2, 3):
        result = analyze_natural_access(needed_tickets=k, needed_maps=k-1)
        print(k, f"witness={float(result.witness_probability_given_valid_opening):.9%}",
              f"conditional access={float(result.item_access_given_witness):.9%}",
              f"joint={float(result.joint_probability_given_valid_opening):.9%}")
