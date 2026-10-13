"""Exact Quick Ball second-discard channel in the champion Shadow Rider fork.

Refines the one-Mysterious-Treasure/no-Fog-Crystal event. Quick Ball and
Mysterious Treasure each have separate mandatory discard costs. The tested
conservative sufficient condition is an accessible Quick Ball plus at least
two held Psychic Energy, allowing one Energy to be discarded while retaining
one. Discard Dialga-GX for Treasure. This is line access, not a win estimate.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import comb

from tools.shadow_rider_dialga_connector_fork import champion_results


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def quick_and_energy_probability(
    selected_filler: int, energy: int = 11, inert: int = 22,
) -> Fraction:
    """Chance of singleton Quick Ball and >=2 Energy in selected filler.

    Given s draws from 1 Quick Ball + energy interchangeable Psychic Energy
    + inert cards, Q appears with s/(1+energy+inert). Conditional on Q,
    the other s-1 selected cards are hypergeometric from energy+inert.
    """
    if selected_filler < 1:
        return Fraction(0)
    total = energy + inert + 1
    selected = selected_filler - 1
    valid = sum(
        choose(energy, e) * choose(inert, selected - e)
        for e in range(2, min(energy, selected) + 1)
    )
    return Fraction(selected_filler, total) * Fraction(
        valid, choose(total - 1, selected)
    )


def exact(
    b: int = 11, v: int = 4, t: int = 4, g: int = 4,
    e: int = 11, f: int = 22,
    hand: int = 7, prizes: int = 6, needed_v: int = 2,
) -> dict[str, Fraction]:
    """Exact all-deal fractions, including rejected Basic opening hands."""
    # Singleton D/M/R remain separate. Single Quick Ball joins Energy/filler.
    caps = (b, v, t, g, e + f + 1)
    n = sum(caps) + 3
    denominator = choose(n, hand) * (n - hand) * choose(n - hand - 1, prizes)
    parent = 0
    quick = Fraction(0)
    quick_energy2 = Fraction(0)
    for d_initial in (True, False):
        other_hand = hand - int(d_initial)
        ranges = [range(min(cap, other_hand) + 1) for cap in caps]
        for opened in product(*ranges):
            if sum(opened) != other_hand or opened[0] == 0:
                continue
            hand_ways = 1
            for cap, count in zip(caps, opened):
                hand_ways *= choose(cap, count)
            remaining = tuple(cap - count for cap, count in zip(caps, opened))
            for draw_index in (range(5) if d_initial else (-1,)):
                draw_ways = remaining[draw_index] if draw_index >= 0 else 1
                if not draw_ways:
                    continue
                left = list(remaining)
                if draw_index >= 0:
                    left[draw_index] -= 1
                held_t = opened[2] + int(draw_index == 2)
                held_g = opened[3] + int(draw_index == 3)
                if held_t != 1 or held_g != 0:
                    continue
                held_filler = opened[4] + int(draw_index == 4)
                max_prize_v = left[1] - needed_v
                if max_prize_v < 0:
                    continue
                non_v = sum(left) - left[1]
                prize_ways = sum(
                    choose(left[1], prized_v) *
                    choose(non_v, prizes - prized_v)
                    for prized_v in range(max_prize_v + 1)
                )
                ways = hand_ways * draw_ways * prize_ways
                parent += ways
                quick += ways * Fraction(held_filler, e + f + 1)
                quick_energy2 += ways * quick_and_energy_probability(
                    held_filler, e, f
                )
    assert quick.denominator == 1
    assert quick_energy2.denominator == 1
    return {
        "parent": Fraction(parent, denominator),
        "quick_access": quick / denominator,
        "quick_energy2": quick_energy2 / denominator,
    }


def physical_oracle(
    b: int, v: int, t: int, g: int, e: int, f: int,
    hand: int, prizes: int, needed_v: int,
) -> tuple[dict[str, Fraction], int]:
    """Brute-force individually labeled cards, without any group weighting."""
    cards = (
        ["D", "M", "R", "Q"] +
        [name + str(index)
         for name, number in
         (("B", b), ("V", v), ("T", t), ("G", g), ("E", e), ("F", f))
         for index in range(number)]
    )
    tally: Counter[str] = Counter()
    denominator = 0
    for opening in combinations(cards, hand):
        opened = set(opening)
        rem = [card for card in cards if card not in opened]
        for draw in rem:
            held = opened | {draw}
            rest = [card for card in rem if card != draw]
            for prizes_dealt in combinations(rest, prizes):
                denominator += 1
                deck = set(rest) - set(prizes_dealt)
                if not {"M", "R"} <= deck or "D" not in held:
                    continue
                if not any(card.startswith("B") for card in opening):
                    continue
                if sum(card.startswith("T") for card in held) != 1:
                    continue
                if any(card.startswith("G") for card in held):
                    continue
                if sum(card.startswith("V") for card in deck) < needed_v:
                    continue
                tally["parent"] += 1
                if "Q" in held:
                    tally["quick_access"] += 1
                    if sum(card.startswith("E") for card in held) >= 2:
                        tally["quick_energy2"] += 1
    return {name: Fraction(tally[name], denominator)
            for name in ("parent", "quick_access", "quick_energy2")}, denominator


def validate() -> dict[str, Fraction]:
    toy_cases = (
        (1, 1, 2, 1, 2, 2, 3, 2, 1),
        (2, 2, 2, 1, 2, 2, 3, 2, 1),
        (3, 2, 2, 1, 2, 1, 4, 2, 1),
    )
    for case in toy_cases:
        expected, worlds = physical_oracle(*case)
        assert exact(*case) == expected
        print("validated Quick Ball labeled deck", case, worlds, "deals")

    result = exact()
    assert result["parent"] == Fraction(117252153997, 9395695101975)
    assert result["quick_access"] == Fraction(79745583049, 56374170611850)
    assert result["quick_energy2"] == Fraction(79455309571, 210463570284240)
    basic_valid = Fraction(9797437, 11703240)
    assert result["parent"] / basic_valid == champion_results()[
        "single_treasure_no_fog"
    ]
    for name, p in result.items():
        print(name, p, f"{float(100*p/basic_valid):.9f}% of Basic-valid openings")
    return result


if __name__ == "__main__":
    validate()
