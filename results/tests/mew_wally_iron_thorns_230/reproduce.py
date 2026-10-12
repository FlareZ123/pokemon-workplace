"""Exact natural Muscle Band 230-damage first-turn Mew vs Iron Thorns ex.

Opponent Iron Thorns ex is already Active, suppressing Tapu Wonder Tag.
The engine assumes no additional damage prevention or Tool suppression.
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

from results.tests.mew_wally_first_attack.reproduce import (
    opening_counts, probability_all_prized,
)

# Mew V, Genesect V, Mew VMAX, Wally, DCE, VIP, Quick,
# Ultra, Muscle Band, other.
POOL = (4, 4, 3, 1, 4, 3, 4, 4, 2, 31)
ROUTES = ("direct", "vip", "quick", "ultra")
EXPECTED = Fraction(412371942273, 175386308570200)


def exact(pool: tuple[int, ...], hand: int, prizes: int) -> list[Fraction]:
    n = sum(pool)
    results = [Fraction(0)] * 4
    for opening, ways in opening_counts(pool, hand):
        if not opening[0]:
            continue  # Must start original Mew V Active before first draw.
        for i, copies in enumerate(pool):
            remaining = copies - opening[i]
            if not remaining:
                continue
            held = list(opening)
            held[i] += 1
            if not (held[3] and held[4] and held[8]):
                continue  # Wally, DCE, Muscle Band physically held/drawn.
            vm = pool[2] - held[2]
            gene = pool[1] - held[1]
            available = 1 - probability_all_prized(
                n - hand - 1, prizes, vm
            )
            if held[1]:
                route = 0
            elif held[5]:
                route = 1
            elif held[6]:
                route = 2
            elif held[7]:
                route = 3
            else:
                continue
            if route:
                available -= probability_all_prized(
                    n - hand - 1, prizes, gene
                )
                available += probability_all_prized(
                    n - hand - 1, prizes, vm + gene
                )
            results[route] += Fraction(
                ways * remaining, comb(n, hand) * (n - hand)
            ) * available
    return results


def oracle(pool: tuple[int, ...], hand: int, prizes: int):
    physical = tuple(k for k, copies in enumerate(pool) for _ in range(copies))
    n = len(physical)
    den = comb(n, hand) * comb(n - hand, prizes) * (n - hand - prizes)
    hits = [0] * 4
    for opening in combinations(range(n), hand):
        initial = set(opening)
        if not any(physical[i] == 0 for i in initial):
            continue
        left = set(range(n)) - initial
        for prize in combinations(sorted(left), prizes):
            p = set(prize)
            for d in left - p:
                held = Counter(physical[i] for i in initial | {d})
                deck = Counter(physical[i] for i in left - p - {d})
                if not (held[3] and held[4] and held[8] and deck[2]):
                    continue
                if held[1]:
                    route = 0
                elif deck[1] and held[5]:
                    route = 1
                elif deck[1] and held[6]:
                    route = 2
                elif deck[1] and held[7]:
                    route = 3
                else:
                    continue
                hits[route] += 1
    return [Fraction(x, den) for x in hits]


def verify_source_cards():
    def card(print_id: str):
        set_id = print_id.rsplit("-", 1)[0]
        data = json.loads(
            (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
            .read_text(encoding="utf-8")
        )
        return next(x for x in data if x["id"] == print_id)

    iron = card("sv6-77")
    band = card("xy1-121")
    mew = card("swsh8-114")
    gene = card("swsh8-185")
    assert int(iron["hp"]) == 230
    assert not iron.get("resistances")
    assert mew["types"] == ["Psychic"]
    assert any(a["name"] == "Initialization" and
               "Pokémon with a Rule Box" in a["text"]
               for a in iron["abilities"])
    assert any("20 more damage" in rule for rule in band["rules"])
    assert any(a["name"] == "Techno Blast" and a["damage"] == "210"
               for a in gene["attacks"])


def main():
    verify_source_cards()
    for pool, hand, prizes in (
        ((1, 1, 1, 1, 1, 0, 1, 1, 1, 4), 3, 2),
        ((2, 1, 1, 1, 1, 1, 1, 1, 2, 3), 4, 2),
    ):
        assert exact(pool, hand, prizes) == oracle(pool, hand, prizes)
        print(f"Physical ID oracle PASS N={sum(pool)}")
    rates = exact(POOL, 7, 6)
    assert sum(rates) == EXPECTED
    for label, fraction in zip(ROUTES, rates):
        print(f"{label}: {float(fraction):.12%}; exact={fraction}")
    base_valid = 1 - Fraction(comb(49, 7), comb(60, 7))
    candidate_valid = 1 - Fraction(comb(48, 7), comb(60, 7))
    print(f"First-turn OHKO: {float(sum(rates)):.12%}; exact={EXPECTED}")
    print(f"Conditional on original deck Basic-valid: "
          f"{float(sum(rates) / base_valid):.12%}")
    print(f"Conditional on +Tapu Basic-valid: "
          f"{float(sum(rates) / candidate_valid):.12%}")


if __name__ == "__main__":
    main()
