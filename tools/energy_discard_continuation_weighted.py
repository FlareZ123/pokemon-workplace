"""Exact conditional probability of the DDE minimum-card continuation reversal.

This is a stylized uniformly sampled attachment-mix model, not a game simulator.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from math import comb


def combinations_or_zero(n: int, k: int) -> int:
    return comb(n, k) if n >= k else 0


def analytic_counts(grass: int, fire: int, other: int) -> dict[str, int | Fraction | None]:
    if min(grass, fire, other) < 0:
        raise ValueError("Counts must be nonnegative")
    n = grass + fire + other
    all_triples = combinations_or_zero(n, 3)
    initial_ready = all_triples - combinations_or_zero(other, 3)
    minimum_card_ready = combinations_or_zero(grass, 2) * fire
    reversed_cases = initial_ready - minimum_card_ready
    return {
        "all_triples": all_triples,
        "initial_apex_ready": initial_ready,
        "minimum_card_preserves_apex": minimum_card_ready,
        "minimum_card_breaks_but_two_cards_preserve_apex": reversed_cases,
        "reversal_given_initial_ready": (
            Fraction(reversed_cases, initial_ready) if initial_ready else None
        ),
    }


def brute_force_counts(grass: int, fire: int, other: int) -> dict[str, int]:
    types = ["Grass"] * grass + ["Fire"] * fire + ["Other"] * other
    result = {"all_triples": 0, "initial_apex_ready": 0,
              "minimum_card_preserves_apex": 0,
              "minimum_card_breaks_but_two_cards_preserve_apex": 0}
    for indexes in combinations(range(len(types)), 3):
        picks = [types[i] for i in indexes]
        result["all_triples"] += 1
        ready = ("Grass" in picks or "Fire" in picks)
        if not ready:
            continue
        result["initial_apex_ready"] += 1
        after_dde = (picks.count("Grass") >= 2 and picks.count("Fire") >= 1)
        if after_dde:
            result["minimum_card_preserves_apex"] += 1
        else:
            result["minimum_card_breaks_but_two_cards_preserve_apex"] += 1
    return result


def verify() -> dict[str, int | Fraction | None]:
    checks = 0
    for grass in range(6):
        for fire in range(6):
            for other in range(6):
                analytic = analytic_counts(grass, fire, other)
                brute = brute_force_counts(grass, fire, other)
                for key, value in brute.items():
                    assert analytic[key] == value, (grass, fire, other, key)
                checks += 1
    assert checks == 216
    example = analytic_counts(5, 3, 2)
    assert example["all_triples"] == 120
    assert example["initial_apex_ready"] == 120
    assert example["minimum_card_preserves_apex"] == 30
    assert example["minimum_card_breaks_but_two_cards_preserve_apex"] == 90
    assert example["reversal_given_initial_ready"] == Fraction(3, 4)
    # The published 2025 Expanded Regidrago example lists 4 DDE, 3 Grass
    # and 2 Fire. Treat Basic triples as hypothetical random attachments.
    published_energy_mix = analytic_counts(3, 2, 0)
    assert published_energy_mix["all_triples"] == 10
    assert published_energy_mix["initial_apex_ready"] == 10
    assert published_energy_mix["minimum_card_preserves_apex"] == 6
    assert published_energy_mix["minimum_card_breaks_but_two_cards_preserve_apex"] == 4
    assert published_energy_mix["reversal_given_initial_ready"] == Fraction(2, 5)
    return {"exhaustive_parameter_checks": checks, **example,
            "published_2025_regidrago_basic_mix": published_energy_mix}


if __name__ == "__main__":
    for label, result in verify().items():
        print(f"{label}: {result}")
    print("PASS")
