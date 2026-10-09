"""Physical capacity lower bounds for simultaneous named-Pokémon Ability guards.

Named-print guards are a conservative corpus. This tool solves a simultaneous
species-placement problem; other costs, ability suppression and action timing
remain external. Guards sharing a source species must have a common print.
"""
from __future__ import annotations

import argparse
import json
import unittest
from itertools import combinations
from pathlib import Path
from typing import Any

from bench_named_ability_dependencies import build


def minimum_joint_bench(guards: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    if not guards:
        raise ValueError("At least one Ability guard is required")

    print_sets: dict[str, set[str]] = {}
    names: set[str] = set()
    forced_bench: set[str] = set()
    for guard in guards:
        source = guard["source_name"]
        cards = set(guard["print_ids"])
        common = print_sets[source] & cards if source in print_sets else cards
        if not common:
            raise ValueError(
                f"Source '{source}' cannot realize all selected guards with one print"
            )
        print_sets[source] = common
        names.add(source)
        required = set(guard["required_names"])
        names.update(required)
        if guard["location"] == "on your bench":
            forced_bench.update(required)

    active_candidates = tuple(sorted(names - forced_bench))
    minimal_slots = len(names) - int(bool(active_candidates))
    return {
        "source_abilities": [
            {"source": row["source_name"], "ability": row["ability"]}
            for row in guards
        ],
        "distinct_required_names": sorted(names),
        "forced_bench_names": sorted(forced_bench),
        "active_candidates": list(active_candidates),
        "minimum_bench_slots": minimal_slots,
        "default_five_feasible_by_capacity": minimal_slots <= 5,
        "eight_slot_feasible_by_capacity": minimal_slots <= 8,
    }


def pairwise_catalog(root: Path) -> dict[str, Any]:
    guards = build(root)["entries"]
    outcomes = []
    for left, right in combinations(guards, 2):
        # Different print-conditional abilities of one species may require
        # separate physical sources. Keep this first census auditable.
        if left["source_name"] == right["source_name"]:
            continue
        result = minimum_joint_bench((left, right))
        outcomes.append({
            "sources": [left["source_name"], right["source_name"]],
            "abilities": [left["ability"], right["ability"]],
            "min_bench": result["minimum_bench_slots"],
        })
    histogram: dict[int, int] = {}
    for row in outcomes:
        k = row["min_bench"]
        histogram[k] = histogram.get(k, 0) + 1
    return {
        "guard_variants": len(guards),
        "different_source_pairs": len(outcomes),
        "minimum_bench_histogram": dict(sorted(histogram.items())),
        "pairs_impossible_at_default_five": sum(
            row["min_bench"] > 5 for row in outcomes
        ),
        "pairs_impossible_at_eight": sum(
            row["min_bench"] > 8 for row in outcomes
        ),
        "highest_capacity_pairs": sorted(
            outcomes,
            key=lambda row: (
                -row["min_bench"], row["sources"], row["abilities"]
            ),
        )[:12],
    }


class JointGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        rows = build(Path("resources"))["entries"]
        cls.regigigas = next(
            x for x in rows
            if x["source_name"] == "Regigigas"
            and x["ability"] == "Ancient Wisdom"
        )
        cls.lunatone = next(
            x for x in rows
            if x["source_name"] == "Lunatone"
            and x["ability"] == "Lunar Cycle"
            and "me1-74" in x["print_ids"]
        )
        cls.solrock = next(
            x for x in rows
            if x["source_name"] == "Solrock"
            and "Lunatone" in x["required_names"]
        )

    def test_regigigas_and_lunatone_require_seven_bench(self) -> None:
        result = minimum_joint_bench((self.regigigas, self.lunatone))
        self.assertEqual(result["minimum_bench_slots"], 7)
        self.assertEqual(len(result["distinct_required_names"]), 8)
        self.assertFalse(result["default_five_feasible_by_capacity"])
        self.assertTrue(result["eight_slot_feasible_by_capacity"])

    def test_reciprocal_pairs_share_two_names(self) -> None:
        result = minimum_joint_bench((self.lunatone, self.solrock))
        self.assertEqual(result["minimum_bench_slots"], 1)
        self.assertEqual(result["distinct_required_names"], ["Lunatone", "Solrock"])

    def test_three_guards_can_share_required_names(self) -> None:
        result = minimum_joint_bench(
            (self.regigigas, self.lunatone, self.solrock)
        )
        self.assertEqual(result["minimum_bench_slots"], 7)

    def test_explicit_bench_only_requirement_cannot_be_active(self) -> None:
        a = {
            "source_name": "A", "ability": "a", "print_ids": ["a1"],
            "required_names": ["B"], "location": "on your bench",
        }
        b = {
            "source_name": "B", "ability": "b", "print_ids": ["b1"],
            "required_names": ["A"], "location": "on your bench",
        }
        row = minimum_joint_bench((a, b))
        self.assertEqual(row["minimum_bench_slots"], 2)
        self.assertEqual(row["active_candidates"], [])

    def test_incompatible_prints_same_source_are_rejected(self) -> None:
        a = {
            "source_name": "A", "ability": "a", "print_ids": ["a1"],
            "required_names": ["B"], "location": "in play",
        }
        b = {
            "source_name": "A", "ability": "b", "print_ids": ["a2"],
            "required_names": ["B"], "location": "in play",
        }
        with self.assertRaises(ValueError):
            minimum_joint_bench((a, b))

    def test_default_capacity_pairwise_census_is_deterministic(self) -> None:
        census = pairwise_catalog(Path("resources"))
        self.assertEqual(census["guard_variants"], 25)
        self.assertGreater(census["different_source_pairs"], 0)
        self.assertEqual(
            sum(census["minimum_bench_histogram"].values()),
            census["different_source_pairs"],
        )
        self.assertGreater(census["pairs_impossible_at_default_five"], 0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=["bench_joint_named_guard_capacity"], verbosity=2)
    else:
        print(json.dumps(pairwise_catalog(Path("resources")), indent=2))


if __name__ == "__main__":
    main()
