"""Exact addition of Marshadow Resetting Hole to the Shadow Rider Path counter."""

from __future__ import annotations

import json
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb, prod
from pathlib import Path

from results.tests.shadow_rider_treasure_payment.reproduce import (
    allocations, capacities as old_capacities,
    exact_counts as old_exact_counts,
)

# Radiant, VMAX, Treasure, Cologne, Flutter, Seal Stone, Shadow Rider V,
# other Basics, Marshadow, other Path answers, Psychic Energy, residual.
def capacities(c, f):
    assert 0 <= c and 0 <= f and c + f <= 4
    stadiums = max(0, 3 - c - f)
    return (1, 4, 4, c, f, 1, 3, 9, 1, stadiums + 1, 11,
            25 - c - f - stadiums)


@lru_cache(None)
def prize_distributions(q0, q1, q3, q8, q9, other, prize_count):
    groups = (q0, q1, q3, q8, q9, other)
    return tuple(
        (choice, prod(comb(q, n) for q, n in zip(groups, choice)))
        for choice in allocations(prize_count, groups)
    )


def feasible(op, hand, deck, energy_only, marshadow):
    if deck[1] < 2:
        return False
    flutter_active = bool(op[4])
    # A sole opening Marshadow must start Active, disabling Resetting Hole.
    bench_marshadow = bool(op[4] or op[6] or op[7])
    if not (bench_marshadow or op[8]):
        return False
    stone = bool(hand[5] and hand[6])
    radiant = bool(
        hand[0] or (hand[2] and deck[0]
                    and (not energy_only or hand[10]))
    )
    path_answer = bool(
        hand[9] or (marshadow and bench_marshadow and hand[8])
    )
    thorns_answer = bool(flutter_active or hand[3])
    missing = int(not radiant) + int(not path_answer) + int(not thorns_answer)
    if missing == 0:
        return True
    if missing > 1 or not stone:
        return False
    return bool(
        (not radiant and deck[0])
        or (not path_answer and (
            deck[9] or (marshadow and bench_marshadow and deck[8])
        ))
        or (not thorns_answer and deck[3])
    )


def exact_counts(quantities, opening=7, prize_count=6):
    n = sum(quantities)
    basics = sum(quantities[i] for i in (0, 4, 6, 7, 8))
    denominator = (
        (comb(n, opening) - comb(n - basics, opening))
        * (n - opening)
        * comb(n - opening - 1, prize_count)
    )
    mass = [0] * 5
    for op in allocations(opening, quantities):
        if not sum(op[i] for i in (0, 4, 6, 7, 8)):
            continue
        opener_weight = prod(comb(q, x) for q, x in zip(quantities, op))
        after_opener = tuple(q - x for q, x in zip(quantities, op))
        for drawn, copies in enumerate(after_opener):
            if not copies:
                continue
            hand = tuple(
                op[i] + int(drawn == i) for i in range(len(op))
            )
            after_draw = tuple(
                after_opener[i] - int(drawn == i)
                for i in range(len(op))
            )
            tracked = tuple(after_draw[i] for i in (0, 1, 3, 8, 9))
            residual = sum(after_draw) - sum(tracked)
            for prizes, ways in prize_distributions(
                *tracked, residual, prize_count
            ):
                weight = opener_weight * copies * ways
                mass[0] += weight
                deck = list(after_draw)
                for i, npr in zip((0, 1, 3, 8, 9), prizes):
                    deck[i] -= npr
                for (energy_only, with_marshadow), index in (
                    ((False, False), 1),
                    ((True, False), 2),
                    ((False, True), 3),
                    ((True, True), 4),
                ):
                    mass[index] += weight * feasible(
                        op, hand, deck, energy_only, with_marshadow
                    )
    assert mass[0] == denominator
    return tuple(Fraction(value, denominator) for value in mass[1:])


EXPECTED_WITH_MARSHADOW_ENERGY_ONLY = {
    (0, 0): Fraction(0),
    (1, 0): Fraction(6734525643697217, 358964655944294400),
    (0, 1): Fraction(961295239426783, 52536169770084000),
    (2, 0): Fraction(183424159584717, 7038522665574400),
    (1, 1): Fraction(66286992390107, 2357392233273000),
    (0, 2): Fraction(5161668511212201, 187684958255354560),
    (3, 0): Fraction(442517053147349, 17093555044966400),
    (2, 1): Fraction(240654607731463, 8756028295014000),
    (1, 2): Fraction(25830425069307, 902331530073820),
    (0, 3): Fraction(268282771976523, 9548699997179434),
    (4, 0): Fraction(11695296292483229, 358964655944294400),
    (3, 1): Fraction(1393768243326681, 40861465376732000),
    (2, 2): Fraction(349366513589781, 9878155697650240),
    (1, 3): Fraction(13843242558303513, 381947999887177360),
    (0, 4): Fraction(1149969188725393, 32300684263716960),
}


def verify_prints():
    root = Path(__file__).resolve().parents[3]

    def card(identifier):
        set_id = identifier.rsplit("-", 1)[0]
        source = root / "resources" / "cards" / "en" / f"{set_id}.json"
        return next(
            row for row in json.loads(source.read_text(encoding="utf-8"))
            if row["id"] == identifier
        )

    marshadow = card("sm10-81")
    assert marshadow["name"] == "Marshadow" and marshadow["hp"] == "80"
    assert not marshadow.get("rules")
    assert any(
        a["name"] == "Resetting Hole"
        and "on your Bench" in a["text"]
        and "discard any Stadium card in play" in a["text"]
        for a in marshadow["abilities"]
    )
    assert any(
        "Pokémon with a Rule Box" in rule and "no Abilities" in rule
        for rule in card("swsh6-148")["rules"]
    )
    assert card("sv6-77")["name"] == "Iron Thorns ex"


def physical_oracle():
    # Independent chronological labeled 5-card openers, 1 Prize, 1 draw.
    toy = (1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
    physical = tuple(i for i, q in enumerate(toy) for _ in range(q))
    counts = [0] * 5
    for opener in combinations(range(len(physical)), 5):
        op = tuple(
            sum(physical[i] == t for i in opener)
            for t in range(len(toy))
        )
        if not sum(op[i] for i in (0, 4, 6, 7, 8)):
            continue
        rest = set(range(len(physical))) - set(opener)
        for prizes in combinations(sorted(rest), 1):
            retained = rest - set(prizes)
            for drawn in retained:
                hand = tuple(
                    op[i] + int(physical[drawn] == i)
                    for i in range(len(toy))
                )
                deck = tuple(
                    sum(physical[j] == i for j in retained if j != drawn)
                    for i in range(len(toy))
                )
                counts[0] += 1
                for policy, index in (
                    ((False, False), 1), ((True, False), 2),
                    ((False, True), 3), ((True, True), 4),
                ):
                    counts[index] += feasible(op, hand, deck, *policy)
    assert counts == [68936, 5019, 4291, 7225, 6331]
    assert exact_counts(toy, 5, 1) == tuple(
        Fraction(n, counts[0]) for n in counts[1:]
    )
    print("PASS: 68,936-world physical-card oracle")


def main():
    from results.tests.shadow_rider_treasure_payment.reproduce import (
        EXPECTED_STRICT,
    )
    verify_prints()
    physical_oracle()
    assert len(EXPECTED_WITH_MARSHADOW_ENERGY_ONLY) == 15
    for pair, wanted in EXPECTED_WITH_MARSHADOW_ENERGY_ONLY.items():
        old_u, old_s, new_u, new_s = exact_counts(capacities(*pair))
        standard_u, standard_s = old_exact_counts(old_capacities(*pair))
        assert (old_u, old_s) == (standard_u, standard_s)
        assert old_s == EXPECTED_STRICT[pair]
        assert new_s == wanted and new_s >= old_s
        assert new_u >= old_u
        print(
            f"C={pair[0]} F={pair[1]} old={float(old_s):.9%} "
            f"with Marshadow={float(new_s):.9%}"
        )
    assert (
        EXPECTED_WITH_MARSHADOW_ENERGY_ONLY[(1, 0)]
        != EXPECTED_WITH_MARSHADOW_ENERGY_ONLY[(3, 0)]
    )
    print("PASS: 15 exact Marshadow corrections and baseline conservation")


if __name__ == "__main__":
    main()
