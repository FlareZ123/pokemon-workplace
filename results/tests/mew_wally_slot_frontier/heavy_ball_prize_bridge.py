"""Hisuian Heavy Ball rescues a prized singleton Tapu Lele for Wally access.

Restricted paper Expanded turn-one-going-second route: natural first draw,
Mew V opener, DCE, Benched Genesect, Mew VMAX and Wally in deck,
Hisuian Heavy Ball in hand and singleton Tapu Lele-GX in Prize cards.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from results.tests.mew_wally_first_attack.reproduce import opening_counts
from results.tests.mew_wally_tapu_variant.reproduce import survive

# Mew, Genesect, VMAX, Wally, DCE, VIP, Quick, Ultra, Lele,
# Hisuian Heavy Ball, other. Lele is a singleton for both decks.
EXPECTED = {
    1: Fraction(1171829613302, 930173815095525),
    2: Fraction(13172246169671, 10417946729069880),
}


def pool(wally: int) -> tuple[int, ...]:
    result = (4, 4, 3, wally, 4, 3, 4, 4, 1, 1, 32 - wally)
    assert sum(result) == 60
    return result


def exact(pool: tuple[int, ...], hand: int, prizes: int) -> Fraction:
    n = sum(pool)
    assert pool[8] == 1 and hand + prizes + 1 < n
    assert prizes >= 1
    result = Fraction(0)
    for opening, ways in opening_counts(pool, hand):
        if not opening[0]:  # Mew V must start Active before the first draw.
            continue
        for k, copies in enumerate(pool):
            remaining = copies - opening[k]
            if not remaining:
                continue
            held = list(opening)
            held[k] += 1
            if not held[4] or held[3] or held[8] or not held[9]:
                continue
            if not (held[1] or held[5] or held[6] or held[7]):
                continue
            # Wally and VMAX must survive Prizes for the deck-search
            # evolution. Genesect must survive only when not naturally held.
            targets = [pool[2] - held[2], pool[3] - held[3]]
            if not held[1]:
                targets.append(pool[1] - held[1])
            unobserved = n - hand - 1
            # Since Lele is a singleton and is absent from the observed hand,
            # the chance that it is in Prizes is prizes/unobserved.
            # After conditioning on this, the remaining prizes are drawn
            # from the other unobserved cards; jointly enforce deck survivors.
            chance = Fraction(prizes, unobserved) * survive(
                unobserved - 1, prizes - 1, targets
            )
            result += Fraction(
                ways * remaining, comb(n, hand) * (n - hand)
            ) * chance
    return result


def physical_oracle(pool: tuple[int, ...], hand: int, prizes: int) -> Fraction:
    cards = tuple(i for i, quantity in enumerate(pool) for _ in range(quantity))
    n = len(cards)
    den = comb(n, hand) * comb(n - hand, prizes) * (n - hand - prizes)
    hits = 0
    for chosen in combinations(range(n), hand):
        opening = set(chosen)
        if not any(cards[i] == 0 for i in opening):
            continue
        remaining = set(range(n)) - opening
        for selected in combinations(sorted(remaining), prizes):
            prize_set = set(selected)
            if not any(cards[i] == 8 for i in prize_set):
                continue
            for drawn in remaining - prize_set:
                held = Counter(cards[i] for i in opening | {drawn})
                deck = Counter(cards[i] for i in remaining - prize_set - {drawn})
                if not (held[4] and held[9] and deck[2] and deck[3]):
                    continue
                if held[3] or held[8]:
                    continue
                if held[1] or (
                    deck[1] and (held[5] or held[6] or held[7])
                ):
                    hits += 1
    return Fraction(hits, den)


def verify_card() -> None:
    path = ROOT / "resources/cards/en/swsh10.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    heavy = next(c for c in raw if c["id"] == "swsh10-146")
    rules = " ".join(heavy["rules"])
    assert "face-down Prize cards" in rules
    assert "Basic Pokémon" in rules
    assert "into your hand" in rules
    assert "this Hisuian Heavy Ball in its place" in rules


def main() -> None:
    verify_card()
    cases = (
        ((1, 1, 1, 2, 1, 0, 1, 0, 1, 1, 2), 3, 2),
        ((2, 1, 1, 1, 1, 1, 1, 0, 1, 1, 2), 3, 2),
        ((1, 2, 1, 2, 1, 1, 1, 0, 1, 1, 2), 4, 2),
    )
    for fixture, h, p in cases:
        expected = physical_oracle(fixture, h, p)
        measured = exact(fixture, h, p)
        assert expected == measured, (fixture, expected, measured)
        print(f"Prize-physical Heavy Ball oracle PASS N={sum(fixture)}: {expected}")
    for wally, pinned in EXPECTED.items():
        measured = exact(pool(wally), 7, 6)
        assert measured == pinned, (wally, measured, pinned)
        print(f"Wally={wally}: Lele-prized Heavy Ball rescue {float(measured):.12%}; {measured}")
    print("The rescued singleton Prize branch is disjoint from prior Lele-in-deck/hand routes.")


if __name__ == "__main__":
    main()
