"""Exact, small-board retention solver for synergistic Bench occupants.

Utility scores are illustrative strategic inputs, not observed win probabilities.
Capacity contractions are caused by card text elsewhere in a game-state model.
"""
from __future__ import annotations

import argparse
import json
import unittest
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Iterable


@dataclass(frozen=True)
class Occupant:
    name: str
    base_value: int


@dataclass(frozen=True)
class PairBonus:
    first: str
    second: str
    bonus: int


def utility(kept: Iterable[str], values: dict[str, int], pairs: tuple[PairBonus, ...]) -> int:
    present = frozenset(kept)
    return sum(values[name] for name in present) + sum(
        pair.bonus for pair in pairs
        if pair.first in present and pair.second in present
    )


def best_retention(
    available: tuple[str, ...],
    capacity: int,
    values: dict[str, int],
    pairs: tuple[PairBonus, ...],
) -> tuple[tuple[str, ...], int]:
    """Keep exactly min(capacity, occupancy) occupants after forced discards."""
    keep_count = min(capacity, len(available))
    return max(
        ((chosen, utility(chosen, values, pairs))
         for chosen in combinations(available, keep_count)),
        key=lambda option: (option[1], option[0]),
    )


def first_stage_options(
    available: tuple[str, ...],
    first_capacity: int,
    possible_later_capacity: int,
    values: dict[str, int],
    pairs: tuple[PairBonus, ...],
) -> list[dict[str, object]]:
    """Enumerate each immediate discard choice and optimal later continuation."""
    rows: list[dict[str, object]] = []
    for survivors in combinations(available, min(first_capacity, len(available))):
        follow_up, later_value = best_retention(
            survivors, possible_later_capacity, values, pairs
        )
        rows.append({
            "first_survivors": list(survivors),
            "first_utility": utility(survivors, values, pairs),
            "later_survivors": list(follow_up),
            "later_utility": later_value,
        })
    return rows


def expected_terminal_utility(option: dict[str, object], later_chance: Fraction) -> Fraction:
    return (
        (1 - later_chance) * int(option["first_utility"])
        + later_chance * int(option["later_utility"])
    )


def preferred_option(options: list[dict[str, object]], later_chance: Fraction) -> dict[str, object]:
    return max(
        options,
        key=lambda option: (
            expected_terminal_utility(option, later_chance),
            tuple(option["first_survivors"]),
        ),
    )


def example() -> dict[str, object]:
    # E is an independently valuable core occupant; A+B denotes a conditional
    # synergy such as Lunatone (Lunar Cycle) supported by a Solrock in play.
    members = (
        Occupant("E_core", 100),
        Occupant("A_lunatone", 0),
        Occupant("B_solrock", 0),
        Occupant("C_attacker", 22),
        Occupant("D_attacker", 20),
    )
    pairs = (PairBonus("A_lunatone", "B_solrock", 30),)
    values = {occupant.name: occupant.base_value for occupant in members}
    names = tuple(occupant.name for occupant in members)
    four, four_value = best_retention(names, 4, values, pairs)
    direct_three, direct_three_value = best_retention(names, 3, values, pairs)
    myopic_three, myopic_three_value = best_retention(four, 3, values, pairs)
    options = first_stage_options(names, 4, 3, values, pairs)
    half = preferred_option(options, Fraction(1, 2))
    threshold = Fraction(5, 11)
    return {
        "fixture": {
            "base_values": values,
            "pair_bonuses": [vars(pair) for pair in pairs],
            "first_capacity": 4,
            "possible_later_capacity": 3,
        },
        "myopic_first_choice": list(four),
        "myopic_first_utility": four_value,
        "myopic_later_choice": list(myopic_three),
        "myopic_later_utility": myopic_three_value,
        "direct_three_choice": list(direct_three),
        "direct_three_utility": direct_three_value,
        "irreversible_path_loss": direct_three_value - myopic_three_value,
        "switch_probability": str(threshold),
        "synergy_regimes": [synergy_regime(b) for b in (0, 20, 21, 22, 23, 30, 41, 42, 50)],
        "at_one_half": {
            "optimal_first_choice": half["first_survivors"],
            "optimal_terminal_expectation": str(expected_terminal_utility(half, Fraction(1, 2))),
            "myopic_terminal_expectation": str(
                (1 - Fraction(1, 2)) * four_value + Fraction(1, 2) * myopic_three_value
            ),
        },
    }


def synergy_regime(bonus: int) -> dict[str, object]:
    """Enumerate how the pair's context-dependent value changes discard choices."""
    names = ("E", "A", "B", "C", "D")
    values = {"E": 100, "A": 0, "B": 0, "C": 22, "D": 20}
    pairs = (PairBonus("A", "B", bonus),)
    first, first_value = best_retention(names, 4, values, pairs)
    staged, staged_value = best_retention(first, 3, values, pairs)
    direct, direct_value = best_retention(names, 3, values, pairs)

    # E+C+D remains worth 142 regardless of the pair's bonus.
    # A strict 0<p<1 switch exists only if first_value>142>staged_value.
    threshold: Fraction | None = None
    if first_value > 142 and staged_value < 142:
        threshold = Fraction(first_value - 142, first_value - staged_value)
    return {
        "bonus": bonus,
        "first_survivors": list(first),
        "first_utility": first_value,
        "staged_survivors": list(staged),
        "staged_utility": staged_value,
        "direct_survivors": list(direct),
        "direct_utility": direct_value,
        "path_regret": direct_value - staged_value,
        "switch_probability": str(threshold) if threshold is not None else None,
    }


class BenchSynergyTests(unittest.TestCase):
    def setUp(self) -> None:
        e = example()["fixture"]
        self.values = e["base_values"]
        self.pairs = tuple(PairBonus(**p) for p in e["pair_bonuses"])
        self.members = tuple(self.values)

    def test_sequential_retention_can_be_strictly_suboptimal(self) -> None:
        first, initial = best_retention(self.members, 4, self.values, self.pairs)
        staged, final_staged = best_retention(first, 3, self.values, self.pairs)
        direct, final_direct = best_retention(self.members, 3, self.values, self.pairs)
        self.assertEqual((initial, final_staged, final_direct), (152, 130, 142))
        self.assertEqual(final_direct - final_staged, 12)
        self.assertFalse(set(direct).issubset(first))
        self.assertEqual(len(staged), 3)

    def test_terminal_probability_changes_first_discard_choice(self) -> None:
        options = first_stage_options(self.members, 4, 3, self.values, self.pairs)
        early = preferred_option(options, Fraction(0))
        late = preferred_option(options, Fraction(1, 2))
        self.assertEqual(early["first_utility"], 152)
        self.assertEqual(late["first_utility"], 142)
        self.assertEqual(late["later_utility"], 142)
        self.assertEqual(expected_terminal_utility(late, Fraction(1, 2)), 142)
        self.assertEqual(expected_terminal_utility(early, Fraction(1, 2)), 141)
        self.assertEqual(
            expected_terminal_utility(early, Fraction(5, 11)),
            expected_terminal_utility(late, Fraction(5, 11)),
        )

    def test_context_dependent_synergy_regime(self) -> None:
        expected = (
            (0, 142, 142, None),
            (20, 142, 142, None),
            (21, 143, 122, "1/21"),
            (22, 144, 122, "1/11"),
            (23, 145, 123, "3/22"),
            (30, 152, 130, "5/11"),
            (41, 163, 141, "21/22"),
            (42, 164, 142, None),
            (50, 172, 150, None),
        )
        for bonus, first_value, staged_value, threshold in expected:
            with self.subTest(bonus=bonus):
                row = synergy_regime(bonus)
                self.assertEqual(row["first_utility"], first_value)
                self.assertEqual(row["staged_utility"], staged_value)
                self.assertEqual(row["switch_probability"], threshold)
                self.assertEqual(row["path_regret"], max(0, row["direct_utility"] - staged_value))

    def test_additive_case_matches_top_k_independently(self) -> None:
        for count in range(1, 9):
            names = tuple(f"p{i}" for i in range(count))
            weights = {name: (i * 7) % 13 - 4 for i, name in enumerate(names)}
            for capacity in range(count + 1):
                _, achieved = best_retention(names, capacity, weights, ())
                expected = sum(sorted(weights.values(), reverse=True)[:capacity])
                self.assertEqual(achieved, expected)

    def test_pair_bonus_can_defeat_singleton_greedy_by_arbitrary_margin(self) -> None:
        for huge_bonus in (5, 30, 10000):
            names = ("pair_a", "pair_b", "filler")
            values = {"pair_a": 0, "pair_b": 0, "filler": 1}
            pair = (PairBonus("pair_a", "pair_b", huge_bonus),)
            kept, achieved = best_retention(names, 2, values, pair)
            self.assertEqual(kept, ("pair_a", "pair_b"))
            self.assertEqual(achieved, huge_bonus)
            self.assertEqual(utility(("pair_a", "filler"), values, pair), 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=["bench_synergy_contraction"], verbosity=2)
    else:
        print(json.dumps(example(), indent=2))


if __name__ == "__main__":
    main()
