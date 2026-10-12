"""Aichi Mew/Genesect Special Red Card natural-exposure opportunity cost.

The candidate +1 Battle VIP Pass / -1 Special Red Card shifts early setup
access at the expense of a late conditional hand-disruption Item. Compute an
exact upper-bound proxy for naturally possessing at least one copy after r
non-Prize draws, with a legal Basic-containing seven-card starting hand.
"""

from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path


def naturally_seen(
    *, total: int, basics: int, red: int,
    opening: int, prizes: int, later_draws: int,
) -> Fraction:
    """Conditional on opening with >=1 Basic, P(>=1 Red seen by draw r).

    Prize cards are uniformly sampled from the cards outside the opening
    hand, and draws are uniformly sampled from the cards outside the Prize
    zone. After integrating over hidden Prize composition, the r draws
    marginally form a uniform r-subset of the unopened (N-opening) cards.
    The fact that r <= N-opening-prizes is checked explicitly.
    """
    assert 0 <= red <= total - basics
    assert 1 <= basics and 1 <= opening <= total
    assert 0 <= prizes <= total - opening
    assert 0 <= later_draws <= total - opening - prizes

    initial_combinations = comb(total, opening)
    valid_initials = initial_combinations - comb(total - basics, opening)
    assert valid_initials > 0

    valid_without_red = (
        comb(total - red, opening)
        - comb(total - red - basics, opening)
    )
    none_later = Fraction(
        comb(total - opening - red, later_draws),
        comb(total - opening, later_draws),
    )
    return 1 - Fraction(valid_without_red, valid_initials) * none_later


def physical_prize_oracle(
    *, total: int, basics: int, red: int,
    opening: int, prizes: int, later_draws: int,
) -> tuple[Fraction, int]:
    """Exhaust every labeled valid hand, Prize set and later-draw subset."""
    assert total <= 13
    labels = tuple(
        ("basic", i) if i < basics
        else ("red", i) if i < basics + red
        else ("other", i)
        for i in range(total)
    )
    all_ids = tuple(range(total))
    favorable = total_worlds = 0
    for hand in combinations(all_ids, opening):
        if not any(labels[i][0] == "basic" for i in hand):
            continue
        remainder = tuple(i for i in all_ids if i not in hand)
        for prize_set in combinations(remainder, prizes):
            drawable = tuple(i for i in remainder if i not in prize_set)
            for drawn in combinations(drawable, later_draws):
                seen_red = any(
                    labels[i][0] == "red" for i in (*hand, *drawn)
                )
                total_worlds += 1
                favorable += seen_red
    return Fraction(favorable, total_worlds), total_worlds


def verify_printed_effect_and_deck_counts() -> None:
    root = Path(__file__).resolve().parents[2]
    source = root / "resources" / "cards" / "en" / "me4.json"
    cards = json.loads(source.read_text(encoding="utf-8"))
    card = next(c for c in cards if c["id"] == "me4-82")
    assert card["name"] == "Special Red Card"
    assert card["subtypes"] == ["Item"]
    assert "opponent has 3 or fewer Prize cards remaining" in card["rules"][0]
    assert "bottom of their deck" in card["rules"][0]
    assert "draw 3 cards" in card["rules"][0]

    from results.competitive_deck_baselines.mew_genesect_reproduce import (
        POKEMON, TRAINERS,
    )
    assert TRAINERS["Special Red Card"] == 2
    assert TRAINERS["Battle VIP Pass"] == 3
    # The source deck's eleven Basic starters stay constant under the swap.
    assert sum(
        POKEMON[name] for name in (
            "Mew V", "Genesect V", "Dedenne-GX", "Crobat V",
            "Lillie's Clefairy ex",
        )
    ) == 11


def self_test() -> None:
    verify_printed_effect_and_deck_counts()
    for red in (0, 1, 2):
        for drawn in (0, 1, 2):
            theory = naturally_seen(
                total=12, basics=3, red=red,
                opening=3, prizes=2, later_draws=drawn,
            )
            measured, worlds = physical_prize_oracle(
                total=12, basics=3, red=red,
                opening=3, prizes=2, later_draws=drawn,
            )
            assert theory == measured, (red, drawn, theory, measured)
            print(f"Toy red={red}, drawn={drawn}: {worlds} physical worlds agree")
    for draws in (1, 3, 6, 10, 14, 20):
        single = naturally_seen(
            total=60, basics=11, red=1,
            opening=7, prizes=6, later_draws=draws,
        )
        double = naturally_seen(
            total=60, basics=11, red=2,
            opening=7, prizes=6, later_draws=draws,
        )
        assert double > single > 0
        print(
            f"r={draws:2} unprized random draws: "
            f"published 2 Red={float(double):.9%}, "
            f"+VIP / -Red 1 Red={float(single):.9%}, "
            f"lost={float(double-single)*100:.9f} pp"
        )


if __name__ == "__main__":
    self_test()
