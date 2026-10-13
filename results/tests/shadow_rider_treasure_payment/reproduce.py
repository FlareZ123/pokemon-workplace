"""Exact Shadow Rider Path + Iron Thorns counter access with typed Treasure payment.

Conditional first-turn card access only, never a match win-rate estimate.
"""
from __future__ import annotations

from functools import lru_cache
from fractions import Fraction
from itertools import combinations
from math import comb, prod
from pathlib import Path
import json


# Radiant, VMAX, Treasure, Cologne, Flutter, Seal Stone, Shadow Rider V,
# other Basic, Path answers (Stadium or Field Blower), Psychic Energy, filler.
def allocations(n, caps):
    if len(caps) == 1:
        if 0 <= n <= caps[0]:
            yield (n,)
        return
    for x in range(min(n, caps[0]) + 1):
        for suffix in allocations(n - x, caps[1:]):
            yield (x,) + suffix


def capacities(c, f):
    assert 0 <= c and 0 <= f and c + f <= 4
    stadiums = max(0, 3 - c - f)
    return (1, 4, 4, c, f, 1, 3, 10, stadiums + 1, 11,
            25 - c - f - stadiums)


def feasible(op, hand, deck, energy_only):
    if deck[1] < 2 or (not op[4] and op[6] + op[7] == 0):
        return False
    stone = bool(hand[5] and hand[6])
    radiant = bool(hand[0] or (
        hand[2] and deck[0] and (not energy_only or hand[9])
    ))
    path_answer = bool(hand[8])
    thorns_answer = bool(op[4] or hand[3])
    missing = int(not radiant) + int(not path_answer) + int(not thorns_answer)
    if missing == 0:
        return True
    if missing > 1 or not stone:
        return False
    return bool(
        (not radiant and deck[0])
        or (not path_answer and deck[8])
        or (not thorns_answer and deck[3])
    )


@lru_cache(None)
def prize_distribution(q0, q1, q3, q8, residual, prizes):
    groups = (q0, q1, q3, q8, residual)
    return tuple(
        (p, prod(comb(q, x) for q, x in zip(groups, p)))
        for p in allocations(prizes, groups)
    )


def exact_counts(quantities, opening=7, prizes=6):
    n = sum(quantities)
    basics = quantities[0] + quantities[4] + quantities[6] + quantities[7]
    denominator = (
        (comb(n, opening) - comb(n - basics, opening))
        * (n - opening)
        * comb(n - opening - 1, prizes)
    )
    mass = unrestricted = strict = 0
    for op in allocations(opening, quantities):
        if not (op[0] + op[4] + op[6] + op[7]):
            continue
        opening_weight = prod(comb(q, x) for q, x in zip(quantities, op))
        remain = tuple(q - x for q, x in zip(quantities, op))
        for drawn, copies in enumerate(remain):
            if not copies:
                continue
            hand = tuple(op[i] + int(i == drawn) for i in range(len(op)))
            after = tuple(remain[i] - int(i == drawn) for i in range(len(op)))
            q0, q1, q3, q8 = (after[i] for i in (0, 1, 3, 8))
            residual = sum(after) - q0 - q1 - q3 - q8
            for (p0, p1, p3, p8, _), ways in prize_distribution(
                q0, q1, q3, q8, residual, prizes
            ):
                weight = opening_weight * copies * ways
                mass += weight
                deck = list(after)
                for i, count in ((0, p0), (1, p1), (3, p3), (8, p8)):
                    deck[i] -= count
                if feasible(op, hand, deck, False):
                    unrestricted += weight
                    if feasible(op, hand, deck, True):
                        strict += weight
    assert mass == denominator
    return Fraction(unrestricted, denominator), Fraction(strict, denominator)


EXPECTED_STRICT = {
    (0, 0): Fraction(0),
    (1, 0): Fraction(1792849491732723, 119654885314764800),
    (0, 1): Fraction(127505391231497, 8756028295014000),
    (2, 0): Fraction(16198356506621, 854677752248320),
    (1, 1): Fraction(99428246564641, 4903375845207840),
    (0, 2): Fraction(741822365694633, 37536991651070912),
    (3, 0): Fraction(1792849491732723, 119654885314764800),
    (2, 1): Fraction(16028317207599, 1021536634418300),
    (1, 2): Fraction(1248670545813, 77204836797760),
    (0, 3): Fraction(3017044197543009, 190973999943588680),
    (4, 0): Fraction(678716740800071, 35896465594429440),
    (3, 1): Fraction(2399323084012007, 122584396130196000),
    (2, 2): Fraction(7549162137163293, 375369916510709120),
    (1, 3): Fraction(7815668920826757, 381947999887177360),
    (0, 4): Fraction(49778992220593, 2484668020285920),
}


def verify_sources():
    from results.competitive_deck_baselines.shadow_rider_reproduce import (
        ENERGY, TRAINERS, POKEMON,
    )
    assert ENERGY == {"Psychic Energy": 11}
    assert TRAINERS["Mysterious Treasure"] == 4
    assert POKEMON["Radiant Eternatus"] == 1
    root = Path(__file__).resolve().parents[3]

    def card(cid):
        setid = cid.rsplit("-", 1)[0]
        path = root / "resources" / "cards" / "en" / f"{setid}.json"
        return next(
            row for row in json.loads(path.read_text(encoding="utf-8"))
            if row["id"] == cid
        )

    treasure = card("sm6-113")
    assert treasure["name"] == "Mysterious Treasure"
    assert any(
        "Discard a card from your hand. If you do" in rule
        for rule in treasure["rules"]
    )
    radiant = card("swsh12pt5-105")
    assert radiant["name"] == "Radiant Eternatus"
    assert any(a["name"] == "Climactic Gate" for a in radiant["abilities"])


def physical_oracle():
    # Independent chronological enumeration of labeled physical cards.
    toy = (1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1)
    physical = tuple(i for i, n in enumerate(toy) for _ in range(n))
    total = unrestricted = strict = 0
    for opener in combinations(range(len(physical)), 3):
        op = tuple(sum(physical[j] == i for j in opener)
                   for i in range(len(toy)))
        if not (op[0] + op[4] + op[6] + op[7]):
            continue
        remaining = set(range(len(physical))) - set(opener)
        for prizes in combinations(sorted(remaining), 2):
            retained = remaining - set(prizes)
            for draw in retained:
                hand = tuple(op[i] + int(physical[draw] == i)
                             for i in range(len(toy)))
                deck = tuple(
                    sum(physical[j] == i for j in retained if j != draw)
                    for i in range(len(toy))
                )
                total += 1
                unrestricted += feasible(op, hand, deck, False)
                strict += feasible(op, hand, deck, True)
    assert total == 72720
    assert (
        Fraction(unrestricted, total), Fraction(strict, total)
    ) == exact_counts(toy, 3, 2)
    print(f"PASS: {total}-world independent physical oracle")


def main():
    from results.shadow_rider_path_counter_frontier.robustness import EXPECTED
    verify_sources()
    physical_oracle()
    assert len(EXPECTED) == len(EXPECTED_STRICT) == 15
    for pair, wanted in EXPECTED_STRICT.items():
        unrestricted, strict = exact_counts(capacities(*pair))
        assert unrestricted == EXPECTED[pair], (pair, unrestricted)
        assert strict == wanted and strict <= unrestricted, (pair, strict)
        print(
            f"C={pair[0]} F={pair[1]} unrestricted={float(unrestricted):.9%} "
            f"Energy-only={float(strict):.9%}"
        )
    winners = {
        n: max((v, pair) for pair, v in EXPECTED_STRICT.items()
               if sum(pair) == n)
        for n in range(5)
    }
    assert [winners[n][1] for n in range(5)] == [
        (0, 0), (1, 0), (1, 1), (1, 2), (1, 3)
    ]
    assert winners[3][0] < winners[2][0] < winners[4][0]
    assert EXPECTED_STRICT[(1, 0)] == EXPECTED_STRICT[(3, 0)]
    print("PASS: all 15 rational policy comparisons")


if __name__ == "__main__":
    main()
