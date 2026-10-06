"""Reproduce the exact prize-rescue-collapse tables and a small exhaustive check."""

from __future__ import annotations

from itertools import combinations
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_rescue_collapse import (  # noqa: E402
    any_critical_prized_probability,
    collapse_probability,
    conditional_collapse_probability,
)


def pct(value: float) -> str:
    return f"{100 * value:.5f}%"


def exhaustive_collapse_probability(
    deck_size: int,
    prize_count: int,
    critical_singletons: int,
    rescue_copies: int,
) -> float:
    cards = ["C"] * critical_singletons + ["G"] * rescue_copies
    cards += ["F"] * (deck_size - len(cards))

    collapsed = 0
    total = 0
    for prize_indices in combinations(range(deck_size), prize_count):
        total += 1
        critical_prized = sum(cards[i] == "C" for i in prize_indices)
        rescuers_prized = sum(cards[i] == "G" for i in prize_indices)
        if critical_prized > rescue_copies - rescuers_prized:
            collapsed += 1
    return collapsed / total


def main() -> None:
    deck_size = 60
    prize_count = 6

    print("Single critical singleton")
    print("Gladion copies | unconditional collapse | conditional collapse")
    for rescue_copies in range(1, 5):
        unconditional = collapse_probability(deck_size, prize_count, 1, rescue_copies)
        conditional = conditional_collapse_probability(deck_size, prize_count, 1, rescue_copies)
        print(f"{rescue_copies:14d} | {pct(unconditional):>22} | {pct(conditional):>20}")

    print("\nMultiple critical singletons: conditional collapse")
    print("Criticals | 1 Gladion | 2 Gladion | 3 Gladion | 4 Gladion")
    for critical_singletons in range(1, 6):
        values = [
            pct(conditional_collapse_probability(deck_size, prize_count, critical_singletons, g))
            for g in range(1, 5)
        ]
        print(f"{critical_singletons:9d} | " + " | ".join(f"{value:>9}" for value in values))

    print("\nAt least one critical singleton Prized")
    for critical_singletons in range(1, 6):
        p = any_critical_prized_probability(deck_size, prize_count, critical_singletons)
        print(f"{critical_singletons}: {pct(p)}")

    exact = collapse_probability(12, 4, 3, 2)
    exhaustive = exhaustive_collapse_probability(12, 4, 3, 2)
    assert abs(exact - exhaustive) < 1e-15
    assert comb(12, 4) == 495
    print(f"\nExhaustive validation N=12, P=4, C=3, G=2: {exact:.12f}")


if __name__ == "__main__":
    main()
