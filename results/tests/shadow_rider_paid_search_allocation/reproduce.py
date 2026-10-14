"""Physical paid-source assignment for the Shadow Rider Path + Thorns launch.

Searches: Mysterious Treasure, Quick Ball, Fog Crystal, Forest Seal Stone.
All paid discard targets are Basic Psychic Energy. Conditional first-turn
access endpoint only; no claim about match win rates.
"""

from __future__ import annotations

import json
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from math import comb, prod
from pathlib import Path

from results.tests.shadow_rider_fog_marshadow.reproduce import (
    allocations,
    capacities as fog_capacities,
)
from results.tests.shadow_rider_fog_allocation.reproduce import (
    prize_masks,
    feasible as prior_feasible,
)


# Indices: Radiant0, VMAX1, Treasure2, Cologne3, Flutter4, Stone5,
# Shadow Rider V6, other Basic7, Marshadow8, other Path9, Energy10,
# Fog Crystal11, Quick Ball12, other cards13.
def capacities(cologne: int, flutter: int) -> tuple[int, ...]:
    prior = fog_capacities(cologne, flutter)
    counts = prior[:-1] + (1, prior[-1] - 1)
    assert sum(counts) == 60 and counts[-1] >= 0
    return counts


@lru_cache(maxsize=None)
def feasible(opening: tuple[int, ...], hand: tuple[int, ...],
             deck: tuple[int, ...]) -> bool:
    if deck[1] < 2:
        return False
    benchable_marshadow = bool(opening[4] or opening[6] or opening[7])
    if not (benchable_marshadow or opening[8]):
        return False

    # The three search targets R, M, V can each be held, searched, or absent.
    # Each assignment below consumes a physical source at most once.
    radiant_options = ["held"] if hand[0] else ["none"]
    if not hand[0] and deck[0]:
        if hand[2]:
            radiant_options.append("treasure")
        if hand[12]:
            radiant_options.append("quick")

    marshadow_options = ["none"]
    if benchable_marshadow:
        if hand[8]:
            marshadow_options = ["held"]
        elif deck[8]:
            if hand[11]:
                marshadow_options.append("fog")
            if hand[2]:
                marshadow_options.append("treasure")
            if hand[12]:
                marshadow_options.append("quick")

    v_options = ["none"]
    if hand[5]:
        if hand[6]:
            v_options = ["held"]
        elif deck[6]:
            if hand[11]:
                v_options.append("fog")
            if hand[2]:
                v_options.append("treasure")
            if hand[12]:
                v_options.append("quick")

    for radiant, marshadow, shadow_v in product(
        radiant_options, marshadow_options, v_options
    ):
        choices = (radiant, marshadow, shadow_v)
        treasure_uses = choices.count("treasure")
        quick_uses = choices.count("quick")
        if treasure_uses > hand[2] or quick_uses > hand[12]:
            continue
        fog_basic_uses = choices.count("fog")
        fog_energy_uses = max(0, treasure_uses + quick_uses - hand[10])
        if fog_basic_uses + fog_energy_uses > hand[11]:
            continue

        # Full deck has 11 Basic Psychic Energy, at most six Prized, and
        # at most five combined Treasure/Quick payments. The pool can always
        # supply the calculated Fog-to-Energy shortfall in this model.
        radiant_ready = radiant != "none"
        path_ready = bool(hand[9] or marshadow != "none")
        thorns_ready = bool(opening[4] or hand[3])
        missing = (int(not radiant_ready) + int(not path_ready)
                   + int(not thorns_ready))
        if missing == 0:
            return True
        if missing != 1 or not (hand[5] and shadow_v != "none"):
            continue
        # Star Alchemy searches exactly one remaining direct role.
        if ((not radiant_ready and deck[0])
            or (not path_ready and (
                deck[9] or (benchable_marshadow and deck[8])
            ))
            or (not thorns_ready and deck[3])):
            return True
    return False


def exact_counts(quantities: tuple[int, ...], opening: int = 7,
                 prizes: int = 6) -> tuple[Fraction, Fraction]:
    size = sum(quantities)
    basics = sum(quantities[i] for i in (0, 4, 6, 7, 8))
    prize_ways = comb(size - opening - 1, prizes)
    denominator = (
        (comb(size, opening) - comb(size - basics, opening))
        * (size - opening) * prize_ways
    )
    totals = [0, 0, 0]
    for opener in allocations(opening, quantities):
        if not sum(opener[i] for i in (0, 4, 6, 7, 8)):
            continue
        opening_weight = prod(comb(q, n) for q, n in zip(quantities, opener))
        after_opening = tuple(q - n for q, n in zip(quantities, opener))
        for drawn, copies in enumerate(after_opening):
            if not copies:
                continue
            hand = tuple(opener[i] + int(i == drawn)
                         for i in range(len(quantities)))
            after = tuple(after_opening[i] - int(i == drawn)
                          for i in range(len(quantities)))
            totals[0] += opening_weight * copies * prize_ways
            stocks = tuple(after[i] for i in (0, 1, 3, 8, 9, 6))
            for mask, prize_weight in prize_masks(
                stocks, size - opening - 1, prizes
            ):
                deck = list(after)
                for bit, index in enumerate((0, 3, 8, 9, 6)):
                    deck[index] = int(not mask & (1 << bit))
                deck[1] = 2
                weight = opening_weight * copies * prize_weight
                totals[1] += weight * prior_feasible(
                    opener, hand, deck, True, True
                )
                totals[2] += weight * feasible(opener, hand, tuple(deck))
    assert totals[0] == denominator
    return (
        Fraction(totals[1], denominator),
        Fraction(totals[2], denominator),
    )


def contract_tests() -> None:
    op = [0] * 14
    op[7] = 1  # Non-Marshadow Basic starting Active.
    hand = [0] * 14
    hand[5] = hand[3] = 1  # Forest Seal Stone, Canceling Cologne.
    deck = [0] * 14
    deck[1] = 2  # Two VMAX remain.
    deck[0] = deck[6] = deck[8] = 1  # R, V, Marshadow remain.
    hand[11] = 1
    assert not feasible(tuple(op), tuple(hand), tuple(deck))
    hand[11] = 2
    assert feasible(tuple(op), tuple(hand), tuple(deck))
    hand[11] = 1
    hand[2] = hand[10] = 1  # Paid Treasure can supply another Basic.
    assert feasible(tuple(op), tuple(hand), tuple(deck))
    hand[10] = 0
    assert not feasible(tuple(op), tuple(hand), tuple(deck))
    hand[11] = 2
    assert feasible(tuple(op), tuple(hand), tuple(deck))
    hand[2] = 0
    hand[11] = 1  # One Fog cannot fetch both required Basics.
    assert not feasible(tuple(op), tuple(hand), tuple(deck))
    print("PASS: shared Fog counts, paid source use, and Energy payment witnesses")


def physical_oracle() -> None:
    # With one Prize, three Energy guarantee any necessary Fog-to-Energy
    # retrieval in the toy (max two paid sources).
    toy = (1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1)
    physical = tuple(i for i, count in enumerate(toy)
                     for _ in range(count))
    counts = [0, 0, 0]
    for chosen in combinations(range(len(physical)), 3):
        opener = tuple(sum(physical[x] == i for x in chosen)
                       for i in range(len(toy)))
        if not sum(opener[i] for i in (0, 4, 6, 7, 8)):
            continue
        rest = set(range(len(physical))) - set(chosen)
        for prize in rest:
            for draw in rest - {prize}:
                hand = tuple(opener[i] + int(physical[draw] == i)
                             for i in range(len(toy)))
                deck = tuple(sum(physical[j] == i for j in rest
                                 if j not in (prize, draw))
                             for i in range(len(toy)))
                counts[0] += 1
                counts[1] += prior_feasible(
                    opener, hand, deck, True, True
                )
                counts[2] += feasible(opener, hand, deck)
    assert counts == [83720, 1929, 2490]
    assert exact_counts(toy, 3, 1) == tuple(
        Fraction(x, counts[0]) for x in counts[1:]
    )
    print("PASS: 83,720 labeled toy-world physical-card oracle")


def verify_prints() -> None:
    root = Path(__file__).resolve().parents[3]

    def card(identifier: str):
        set_id = identifier.rsplit("-", 1)[0]
        path = root / "resources" / "cards" / "en" / f"{set_id}.json"
        return next(row for row in json.loads(path.read_text(encoding="utf-8"))
                    if row["id"] == identifier)

    assert "Basic Psychic Pokémon" in card("swsh6-140")["rules"][0]
    assert "Discard a card from your hand" in card("sm6-113")["rules"][0]
    assert "discard another card from your hand" in (
        card("swsh1-179")["rules"][0]
    )
    assert card("swsh6-74")["types"] == ["Psychic"]
    assert card("sm10-81")["types"] == ["Psychic"]
    assert card("swsh12pt5-105")["types"] == ["Dragon"]


def main() -> None:
    verify_prints()
    contract_tests()
    physical_oracle()
    prior, expanded = exact_counts(capacities(1, 1))
    assert expanded >= prior
    print(
        f"C=1 F=1 shared-Fog-only={float(prior):.9%} "
        f"paid-source+Fog-Energy={float(expanded):.9%} "
        f"gain_pp={100 * float(expanded - prior):.9f}",
        flush=True,
    )
    print("PASS: exact 60-card source-allocation comparison")


if __name__ == "__main__":
    main()
