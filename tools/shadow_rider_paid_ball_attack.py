"""Direct or one Energy-paid Ball Radiant launch; exact next-turn energy and pivot.

Four Mysterious Treasure and one Quick Ball are equivalent *only for this
restricted Radiant search*: both find this Dragon Basic for a one-card discard.
Require that the discarded card is a held Basic Psychic Energy.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from math import prod

from tools.shadow_rider_direct_launch_attack import allocations, choose
from tools.shadow_rider_post_launch_energy import (
    EnergyWindow, attack_ready_probability, attack_and_pivot_ready_probability,
)
from tools.shadow_rider_valley_pivot_gate import dual_card_draw_probability

# Radiant, other Basics, VMAX, Psychic, Float Stone, paid-search Ball, neutral
COUNTS = (1, 13, 4, 11, 1, 5, 25)
ROUTES = ("direct", "psychic_paid_ball")


@dataclass(frozen=True)
class PaidAccess:
    launch: Fraction
    energy_three: Fraction
    energy_three_float: Fraction
    valley_two_float: Fraction
    either_float: Fraction
    overlap: Fraction
    grouped_states: int


def exact_paid(
    *,
    counts: tuple[int, int, int, int, int, int, int] = COUNTS,
    opening: int = 7,
    prizes: int = 6,
) -> dict[str, PaidAccess]:
    """Accepted-opening joint probability of launch, paid search and attack.

    Uses one natural draw on launch turn, two VMAX placed from deck, and one
    later natural draw before at most two Underworld Door draw-two uses.
    """
    n = sum(counts)
    if min(counts) < 0 or counts[0] != 1 or counts[2] < 2 or counts[4] != 1 or counts[6] < 1:
        raise ValueError("requires Radiant, two VMAX, Float, and one Valley")
    if opening <= 0 or prizes < 0 or n-opening-prizes < 6:
        raise ValueError("insufficient residual deck")
    accepted = choose(n, opening) - choose(n-counts[0]-counts[1], opening)
    common = accepted * choose(n-opening, prizes) * (n-opening-prizes)
    grouped: dict[tuple[str, int, int, int, int, int, int], Fraction] = defaultdict(Fraction)
    for hand in allocations(opening, counts):
        if not hand[1]:
            continue
        ways_hand = prod(choose(c, x) for c, x in zip(counts, hand))
        remaining = tuple(c-x for c, x in zip(counts, hand))
        for prize in allocations(prizes, remaining):
            ways_prize = prod(choose(c, x) for c, x in zip(remaining, prize))
            deck = tuple(c-x for c, x in zip(remaining, prize))
            for first, copies in enumerate(deck):
                if not copies:
                    continue
                after_first = list(deck)
                after_first[first] -= 1
                radiant_in_hand = hand[0] + int(first == 0)
                psychic_in_hand = hand[3] + int(first == 3)
                paid_ball_in_hand = hand[5] + int(first == 5)
                if radiant_in_hand:
                    route = "direct"
                    if after_first[2] < 2:
                        continue
                    psychic_payment = 0
                    radiant_from_deck = 0
                else:
                    route = "psychic_paid_ball"
                    if not (
                        after_first[0] and paid_ball_in_hand
                        and psychic_in_hand and after_first[2] >= 2
                    ):
                        continue
                    psychic_payment = 1
                    radiant_from_deck = 1
                after_first[0] -= radiant_from_deck
                after_first[2] -= 2
                draw2_count = n-opening-prizes-3-radiant_from_deck
                weight = ways_hand * ways_prize * copies
                for second, copies2 in enumerate(after_first):
                    if not copies2:
                        continue
                    after_second = list(after_first)
                    after_second[second] -= 1
                    key = (
                        route,
                        psychic_in_hand-psychic_payment+int(second == 3), after_second[3],
                        hand[4]+int(first == 4)+int(second == 4), after_second[4],
                        hand[6]+int(first == 6)+int(second == 6), after_second[6],
                    )
                    grouped[key] += Fraction(weight*copies2, common*draw2_count)
    fields = ("launch", "energy_three", "energy_three_float", "valley_two_float", "overlap")
    totals: dict[str, dict[str, Fraction]] = {
        route: dict.fromkeys(fields, Fraction()) for route in ROUTES
    }
    states = {route: 0 for route in ROUTES}
    for (route, he, de, hf, df, neutral_h, neutral_d), mass in grouped.items():
        searched = int(route == "psychic_paid_ball")
        remaining = n-opening-prizes-4-searched
        window = EnergyWindow(he, de, remaining)
        valley_held = Fraction(neutral_h, counts[6])
        valley_deck = Fraction(neutral_d, counts[6])
        energy3 = attack_ready_probability(window, 3)
        three_float = attack_and_pivot_ready_probability(
            window, 3, pivots_in_deck=df, pivots_in_hand=hf,
        )
        two_float_held = attack_and_pivot_ready_probability(
            window, 2, pivots_in_deck=df, pivots_in_hand=hf,
        )
        if neutral_d:
            two_float_deck = dual_card_draw_probability(he, de, remaining, hf, df, 0, 1, 2)
            three_float_deck = dual_card_draw_probability(he, de, remaining, hf, df, 0, 1, 3)
        else:
            two_float_deck = three_float_deck = Fraction()
        tally = totals[route]
        tally["launch"] += mass
        tally["energy_three"] += mass*energy3
        tally["energy_three_float"] += mass*three_float
        tally["valley_two_float"] += mass*(
            valley_held*two_float_held + valley_deck*two_float_deck
        )
        tally["overlap"] += mass*(
            valley_held*three_float + valley_deck*three_float_deck
        )
        states[route] += 1
    result: dict[str, PaidAccess] = {}
    for route, data in totals.items():
        result[route] = PaidAccess(
            data["launch"], data["energy_three"], data["energy_three_float"],
            data["valley_two_float"],
            data["energy_three_float"]+data["valley_two_float"]-data["overlap"],
            data["overlap"], states[route],
        )
    return result
