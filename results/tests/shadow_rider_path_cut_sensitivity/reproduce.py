"""Exact first-turn Path-counter slot sensitivity in the hypothetical
one-Cologne / one-Flutter Shadow Rider variant.

All outputs are information-privileged conditional access, not match results.
"""
from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from results.tests.shadow_rider_paid_search_allocation.reproduce import capacities
from results.tests.shadow_rider_thorns_continuation.reproduce import (
    classify,
    exact_partition,
)


EXPECTED = {
    0: (26946742764678720, 15179524312860506,
        13303043774784568, 1535825322966354),
    1: (29572861682407603, 16798362820676094,
        14480600858376261, 1706101996644752),
    2: (31952714935078134, 18279148614073453,
        15537423102327602, 1863856781322921),
}
DENOMINATOR = 367753188390588000


def modified_capacities(extra_path: int) -> tuple[int, ...]:
    assert extra_path in (0, 1, 2)
    counts = list(capacities(1, 1))
    # In the preexisting restricted solver, index 9 combines Stadium Path
    # replacement and Field Blower. Index 13 is inert *for this endpoint*;
    # in reality every card chosen for this slot has tactical opportunity cost.
    counts[9] += extra_path
    counts[13] -= extra_path
    assert counts[9] == 2 + extra_path
    assert counts[13] == 17 - extra_path
    assert sum(counts) == 60
    return tuple(counts)


def verify_prints() -> None:
    root = Path(__file__).resolve().parents[3]

    def card(identifier: str) -> dict:
        set_name = identifier.rsplit("-", 1)[0]
        cards = json.loads(
            (root / "resources" / "cards" / "en" / f"{set_name}.json")
            .read_text(encoding="utf-8")
        )
        return next(row for row in cards if row["id"] == identifier)

    assert card("xy6-89")["name"] == "Sky Field"
    assert "8 Pokémon" in card("xy6-89")["rules"][0]
    assert card("xy4-93")["name"] == "Dimension Valley"
    assert "attacks" in card("xy4-93")["rules"][0]
    assert card("sm2-125")["name"] == "Field Blower"
    assert "Stadium cards" in card("sm2-125")["rules"][0]


def physical_toy_oracle() -> None:
    """Each slot swap conserves total physical cards in a labeled toy."""
    base = (1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 3)
    # Test both extra-Path extremes against weighted enumeration.
    for extra in (0, 2):
        toy = list(base)
        toy[9] += extra
        toy[13] -= extra
        toy = tuple(toy)
        cards = tuple(i for i, copies in enumerate(toy)
                      for _ in range(copies))
        raw = [0] * 5
        for chosen in combinations(range(len(cards)), 3):
            opening = tuple(sum(cards[pos] == i for pos in chosen)
                            for i in range(len(toy)))
            if not sum(opening[i] for i in (0, 4, 6, 7, 8)):
                continue
            available = set(range(len(cards))) - set(chosen)
            for prized in available:
                for drawn in available - {prized}:
                    hand = tuple(opening[i] + int(cards[drawn] == i)
                                 for i in range(len(toy)))
                    deck = tuple(sum(cards[pos] == i for pos in available
                                     if pos not in (prized, drawn))
                                 for i in range(len(toy)))
                    raw[0] += 1
                    flags = classify(opening, hand, deck)
                    for i, flag in enumerate(flags):
                        raw[i + 1] += flag
        exact = exact_partition(toy, opening=3, prizes=1)
        assert exact == tuple(Fraction(n, raw[0]) for n in raw[1:])
        print(f"PASS: physical toy swap extra_path={extra}, {raw[0]} worlds")


def main() -> None:
    verify_prints()
    physical_toy_oracle()
    base = tuple(Fraction(n, DENOMINATOR) for n in EXPECTED[0])
    rates = [base]
    for extra in (1, 2):
        rate = exact_partition(modified_capacities(extra))
        assert rate == tuple(
            Fraction(n, DENOMINATOR) for n in EXPECTED[extra]
        )
        assert rate[0] == rate[1] + rate[2] - rate[3]
        rates.append(rate)
        print(
            f"Retain {extra} extra Stadium(s): "
            f"launch={float(rate[0]):.9%}, "
            f"Cologne-only={float(rate[1] - rate[3]):.9%}, "
            f"Flutter-backed={float(rate[2]):.9%}",
            flush=True,
        )
    assert rates[0][0] < rates[1][0] < rates[2][0]
    assert rates[0][2] < rates[1][2] < rates[2][2]
    for extra in (1, 2):
        print(
            f"extra_path={extra} access_gain_pp="
            f"{100 * float(rates[extra][0] - base[0]):.9f}",
            flush=True,
        )
    print("PASS: exact physical slot sensitivity, no matchup claims")


if __name__ == "__main__":
    main()
