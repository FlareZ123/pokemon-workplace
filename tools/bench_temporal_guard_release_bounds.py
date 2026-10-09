"""Minimal Bench-only release budget to execute named guards sequentially.

A first conditional engine is already in play and has resolved its useful
effect. A fixed Active Pokémon remains. Remove selected Benched objects,
then bench missing named requirements for a second engine.

This abstracts release card availability, damage restrictions, and Ability costs.
"""
from __future__ import annotations

import argparse
import json
import unittest
from itertools import combinations
from math import comb
from pathlib import Path
from typing import Any

from bench_named_ability_dependencies import build
from bench_joint_named_guard_capacity import minimum_joint_bench


def guard_names(guard: dict[str, Any]) -> frozenset[str]:
    return frozenset((guard["source_name"], *guard["required_names"]))


def guard_forced_bench(guard: dict[str, Any]) -> frozenset[str]:
    if guard["location"] == "on your bench":
        return frozenset(guard["required_names"])
    return frozenset()


def sequential_budget(
    first: frozenset[str],
    second: frozenset[str],
    *,
    capacity: int,
    active: str,
    second_forced_bench: frozenset[str] = frozenset(),
    first_forced_bench: frozenset[str] = frozenset(),
) -> dict[str, Any] | None:
    """Minimum discards when only nonrequired Bench occupants can leave.

    Assume every required first-engine name occupies exactly one Pokémon object,
    the initial board contains no extra Pokémon, and the first engine has already
    delivered its desired effect.
    """
    if capacity < 0:
        raise ValueError("capacity must be nonnegative")
    if active not in first or active in first_forced_bench:
        return None
    if active in second_forced_bench:
        return None
    available_positions = capacity + 1
    if len(first) > available_positions:
        return None
    final_pinned = second | {active}
    if len(final_pinned) > available_positions:
        return None

    arrivals = second - first
    departures = max(0, len(first | second) - available_positions)
    discardable = first - second - {active}
    if departures > len(discardable):
        return None

    return {
        "active_kept": active,
        "initial_names": sorted(first),
        "later_names": sorted(second),
        "new_named_arrivals": sorted(arrivals),
        "minimum_departures": departures,
        "available_discardable": sorted(discardable),
        "new_capacity": capacity,
        "fits_one_two_discard_supporter": departures <= 2,
        "requires_additional_release": max(0, departures - 2),
    }


def best_guard_schedule(
    first: dict[str, Any], second: dict[str, Any], capacity: int
) -> dict[str, Any] | None:
    early_names = guard_names(first)
    later_names = guard_names(second)
    early_forced = guard_forced_bench(first)
    later_forced = guard_forced_bench(second)
    candidates = sorted(early_names - early_forced)
    schedules = [
        sequential_budget(
            early_names,
            later_names,
            capacity=capacity,
            active=active,
            first_forced_bench=early_forced,
            second_forced_bench=later_forced,
        )
        for active in candidates
    ]
    viable = [s for s in schedules if s is not None]
    if not viable:
        return None
    return min(
        viable, key=lambda row: (
            row["minimum_departures"], row["active_kept"]
        )
    )


def pairwise_release_census(root: Path) -> dict[str, Any]:
    guards = build(root)["entries"]
    rows = []
    for left, right in combinations(guards, 2):
        if left["source_name"] == right["source_name"]:
            continue
        joint = minimum_joint_bench((left, right))
        if joint["minimum_bench_slots"] <= 5:
            continue
        permutations = (best_guard_schedule(left, right, 5),
                        best_guard_schedule(right, left, 5))
        valid = [v for v in permutations if v is not None]
        if not valid:
            rows.append({
                "sources": [left["source_name"], right["source_name"]],
                "joint_min_bench": joint["minimum_bench_slots"],
                "sequential_feasible": False,
                "required_releases": None,
            })
            continue
        winner = min(valid, key=lambda r: (
            r["minimum_departures"], r["active_kept"]
        ))
        rows.append({
            "sources": [left["source_name"], right["source_name"]],
            "joint_min_bench": joint["minimum_bench_slots"],
            "sequential_feasible": True,
            "required_releases": winner["minimum_departures"],
            "active_kept": winner["active_kept"],
        })
    histogram: dict[str, int] = {}
    for row in rows:
        key = str(row["required_releases"])
        histogram[key] = histogram.get(key, 0) + 1
    return {
        "jointly_impossible_default_five_pairs": len(rows),
        "sequential_release_budget_histogram": dict(sorted(histogram.items())),
        "potentially_rescuable_with_one_two_discard_supporter": sum(
            row["sequential_feasible"] and row["required_releases"] <= 2
            for row in rows
        ),
        "require_more_than_two_releases": sum(
            row["sequential_feasible"] and row["required_releases"] > 2
            for row in rows
        ),
        "no_order_or_active_can_reach_second_guard": sum(
            not row["sequential_feasible"] for row in rows
        ),
        "rows": rows,
    }


def brute_min_departures(
    first: frozenset[str], second: frozenset[str],
    capacity: int, active: str
) -> int | None:
    """Independent full-subset oracle for the simplified occupancy problem."""
    if active not in first or len(first) > capacity + 1:
        return None
    others = sorted(first - {active})
    for count in range(len(others) + 1):
        for removed in combinations(others, count):
            survivor = first - set(removed)
            if not (survivor | second) <= (first | second):
                raise AssertionError("unexpected symbol")
            if len(survivor | second) <= capacity + 1 and (
                survivor | second
            ) >= second:
                return count
    return None


class SequentialBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        rows = build(Path("resources"))["entries"]
        cls.regigigas = next(
            row for row in rows
            if row["source_name"] == "Regigigas"
            and row["ability"] == "Ancient Wisdom"
        )
        cls.lunatone = next(
            row for row in rows
            if row["source_name"] == "Lunatone"
            and row["ability"] == "Lunar Cycle"
            and "me1-74" in row["print_ids"]
        )

    def test_known_two_departure_regigigas_lunatone_line(self) -> None:
        result = best_guard_schedule(self.regigigas, self.lunatone, 5)
        assert result is not None
        self.assertEqual(result["minimum_departures"], 2)
        self.assertEqual(len(result["new_named_arrivals"]), 2)
        self.assertTrue(result["fits_one_two_discard_supporter"])

    def test_three_new_species_require_three_departures(self) -> None:
        first = frozenset(("Regigigas", *(
            "Regirock", "Regice", "Registeel", "Regieleki", "Regidrago"
        )))
        second = frozenset(("Uxie", "Mesprit", "Azelf"))
        result = sequential_budget(
            first, second, capacity=5, active="Regigigas"
        )
        assert result is not None
        self.assertEqual(result["minimum_departures"], 3)
        self.assertEqual(result["requires_additional_release"], 1)

    def test_fixed_active_can_block_second_bench_guard(self) -> None:
        self.assertIsNone(sequential_budget(
            frozenset(("A", "B")), frozenset(("A", "C")),
            capacity=2, active="A", second_forced_bench=frozenset(("A",))
        ))

    def test_bruteforce_small_distinct_name_spaces(self) -> None:
        alphabet = tuple("ABCDEF")
        for capacity in range(1, 6):
            for first_size in range(1, min(6, capacity + 1) + 1):
                for initial in combinations(alphabet, first_size):
                    first = frozenset(initial)
                    active = initial[0]
                    for second_size in range(1, 7):
                        for later in combinations(alphabet, second_size):
                            second = frozenset(later)
                            symbolic = sequential_budget(
                                first, second, capacity=capacity, active=active
                            )
                            brute = brute_min_departures(
                                first, second, capacity, active
                            )
                            self.assertEqual(
                                None if symbolic is None else symbolic["minimum_departures"],
                                brute,
                            )

    def test_pinned_snapshot_pairwise_counts(self) -> None:
        census = pairwise_release_census(Path("resources"))
        self.assertEqual(census["jointly_impossible_default_five_pairs"], 23)
        self.assertEqual(
            census["potentially_rescuable_with_one_two_discard_supporter"], 15
        )
        self.assertEqual(census["require_more_than_two_releases"], 8)
        self.assertEqual(census["no_order_or_active_can_reach_second_guard"], 0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=["bench_temporal_guard_release_bounds"], verbosity=2)
    else:
        print(json.dumps(pairwise_release_census(Path("resources")), indent=2))


if __name__ == "__main__":
    main()
