"""Exact quotient size for one optional action between pure Bench contractions.

An optional action requires d specified distinct original Bench objects in play
at the intermediate stage, and has one fixed nontrivial off-board effect.
The source set is known; its identities do not matter to the count.
"""

from __future__ import annotations

import argparse
import json
import unittest
from dataclasses import dataclass
from itertools import combinations
from math import comb


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class GuardEquivalence:
    initial_bench: int
    intermediate_capacity: int
    final_capacity: int
    prerequisite_count: int
    skip_histories: int
    use_histories: int
    optional_action_histories: int
    final_survivor_sets: int
    action_reachable_survivor_sets: int
    distinct_full_terminal_states: int


def evaluate(n: int, a: int, b: int, d: int) -> GuardEquivalence:
    """Combinatorial exact count; no physical board enumeration required."""
    if not 0 <= d <= n or not 0 <= b <= a <= n:
        raise ValueError("expected 0 <= d <= n and 0 <= b <= a <= n")

    skips = choose(n, a) * choose(a, b)
    uses = choose(n - d, a - d) * choose(a, b)
    feasible = 0
    if a >= d:
        # r is number of prerequisite objects retained in final b.
        # A feasible intermediate a must hold all d prerequisites and
        # the b eventual survivors, so b+d-r <= a.
        for r in range(max(0, b + d - a), min(d, b) + 1):
            feasible += choose(d, r) * choose(n - d, b - r)
    finals = choose(n, b)
    assert feasible <= finals
    return GuardEquivalence(
        initial_bench=n,
        intermediate_capacity=a,
        final_capacity=b,
        prerequisite_count=d,
        skip_histories=skips,
        use_histories=uses,
        optional_action_histories=skips + uses,
        final_survivor_sets=finals,
        action_reachable_survivor_sets=feasible,
        distinct_full_terminal_states=finals + feasible,
    )


def brute_force(n: int, a: int, b: int, d: int) -> tuple[int, int, int]:
    """Independent enumeration over object-level intermediate/final subsets."""
    original = tuple(range(n))
    required = set(original[:d])
    final_flags: dict[tuple[int, ...], bool] = {}
    skips = uses = 0
    for intermediate in combinations(original, a):
        enabled = required.issubset(intermediate)
        for terminal in combinations(intermediate, b):
            skips += 1
            uses += enabled
            final_flags[terminal] = final_flags.get(terminal, False) or enabled
    full_states = len(final_flags) + sum(final_flags.values())
    return skips, uses, full_states


class GuardEquivalenceTests(unittest.TestCase):
    def test_all_small_cases_against_independent_oracle(self) -> None:
        tested = 0
        for n in range(9):
            for d in range(n + 1):
                for a in range(n + 1):
                    for b in range(a + 1):
                        with self.subTest(n=n, d=d, a=a, b=b):
                            x = evaluate(n, a, b, d)
                            self.assertEqual(
                                (x.skip_histories, x.use_histories,
                                 x.distinct_full_terminal_states),
                                brute_force(n, a, b, d),
                            )
                            tested += 1
        self.assertEqual(tested, 1155)

    def test_lunar_cycle_witness_matches_physical_census(self) -> None:
        x = evaluate(5, 4, 3, 2)
        self.assertEqual(
            (x.skip_histories, x.use_histories,
             x.optional_action_histories,
             x.final_survivor_sets, x.action_reachable_survivor_sets,
             x.distinct_full_terminal_states),
            (20, 12, 32, 10, 9, 19),
        )

    def test_eight_slot_exact_extension(self) -> None:
        x = evaluate(8, 5, 3, 2)
        self.assertEqual(
            (x.skip_histories, x.use_histories,
             x.final_survivor_sets, x.action_reachable_survivor_sets,
             x.distinct_full_terminal_states),
            (560, 200, 56, 56, 112),
        )

    def test_invalid_inputs(self) -> None:
        for args in [(-1, 0, 0, 0), (5, 3, 4, 2), (5, 4, 3, 6)]:
            with self.assertRaises(ValueError):
                evaluate(*args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    if parser.parse_args().self_test:
        unittest.main(argv=["bench_intermediate_guard_equivalence"], verbosity=2)
    else:
        print(json.dumps([
            evaluate(*params).__dict__
            for params in ((5, 4, 3, 2), (8, 5, 3, 2))
        ], indent=2))


if __name__ == "__main__":
    main()
