"""Reproduce source-checked Regidrago Crispin source-pool calculation."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path

from tools.aichi_regidrago_crispin_energy_supply import both_types_in_deck, build


def brute_supply(population: int, grass: int, fire: int, outside: int) -> Fraction:
    names = ("G",) * grass + ("F",) * fire + ("X",) * (population - grass - fire)
    hit = total = 0
    for outside_indices in combinations(range(population), outside):
        outside_set = set(outside_indices)
        retained = [name for i, name in enumerate(names) if i not in outside_set]
        hit += "G" in retained and "F" in retained
        total += 1
    return Fraction(hit, total)


def main() -> None:
    checked = 0
    for population in range(2, 11):
        for grass in range(population + 1):
            for fire in range(population - grass + 1):
                for outside in range(population + 1):
                    direct = brute_supply(population, grass, fire, outside)
                    exact = both_types_in_deck(population, grass, fire, outside)
                    assert direct == exact, (population, grass, fire, outside)
                    checked += 1
    assert checked == 2424
    result = build(Path("."))
    assert result["grass_placement_weak_dominance_m"] == 59
    assert result["strict_advantage_m_count"] == 56
    print("independent small-deck full outside-set checks:", checked)
    print("source-list type supply:", result["rows"])
    print("PASS: exact source-state and physical enumeration agree")


if __name__ == "__main__":
    main()
