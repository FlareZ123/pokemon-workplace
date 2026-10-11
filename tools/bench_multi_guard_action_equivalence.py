"""Exact complete-state quotient for independent intermediate Bench-guard actions.

Each optional action requires a named subset of the initial n Bench objects.
For a selected group of actions U, every required object in the union of
their guards must fit alongside the final survivors in some intermediate a.
Used action identities have distinguishable independent resource effects.
"""

from __future__ import annotations

import argparse
import json
import unittest
from dataclasses import dataclass
from itertools import combinations, product

from bench_intermediate_guard_equivalence import choose


def action_subsets(m: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        selected
        for k in range(m + 1)
        for selected in combinations(range(m), k)
    )


@dataclass(frozen=True)
class MultiGuardCensus:
    original_bench: int
    intermediate_capacity: int
    final_capacity: int
    action_count: int
    action_annotated_histories: int
    final_survivor_sets: int
    distinct_terminal_states: int
    action_set_union_sizes: tuple[int, ...]


def evaluate(
    n: int,
    a: int,
    b: int,
    guards: tuple[frozenset[int], ...],
) -> MultiGuardCensus:
    if not 0 <= b <= a <= n:
        raise ValueError("expected 0 <= final <= intermediate <= n")
    if any(not all(isinstance(i, int) and 0 <= i < n for i in g)
           for g in guards):
        raise ValueError("guard objects must be valid Bench indices")

    histories = terminal_states = 0
    union_sizes = []
    for chosen_actions in action_subsets(len(guards)):
        required = frozenset().union(
            *(guards[i] for i in chosen_actions)
        )
        d = len(required)
        union_sizes.append(d)
        # Each action subset has its own distinguishable, fixed resource
        # signature. Requisite objects must coexist on intermediate Bench.
        histories += choose(n - d, a - d) * choose(a, b)
        if a >= d:
            # Count final S with r shared required objects and enough
            # intermediate capacity to hold both S and the action guards.
            terminal_states += sum(
                choose(d, r) * choose(n - d, b - r)
                for r in range(max(0, b + d - a), min(d, b) + 1)
            )
    return MultiGuardCensus(
        original_bench=n,
        intermediate_capacity=a,
        final_capacity=b,
        action_count=len(guards),
        action_annotated_histories=histories,
        final_survivor_sets=choose(n, b),
        distinct_terminal_states=terminal_states,
        action_set_union_sizes=tuple(union_sizes),
    )


def brute_force(
    n: int,
    a: int,
    b: int,
    guards: tuple[frozenset[int], ...],
) -> tuple[int, int]:
    original = range(n)
    reachable: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    histories = 0
    for intermediate in combinations(original, a):
        live = frozenset(intermediate)
        available_actions = frozenset(
            j for j, guard in enumerate(guards) if guard <= live
        )
        for final in combinations(intermediate, b):
            for chosen in action_subsets(len(guards)):
                if frozenset(chosen) <= available_actions:
                    histories += 1
                    reachable.add((final, chosen))
    return histories, len(reachable)


class MultiGuardTests(unittest.TestCase):
    def test_all_up_to_five_and_two_actions(self) -> None:
        cases = 0
        for n in range(6):
            possible_guards = tuple(
                frozenset(i for i in range(n) if mask & (1 << i))
                for mask in range(1 << n)
            )
            for m in range(3):
                for guard_tuple in product(possible_guards, repeat=m):
                    for a in range(n + 1):
                        for b in range(a + 1):
                            with self.subTest(n=n, a=a, b=b, g=guard_tuple):
                                actual = evaluate(n, a, b, guard_tuple)
                                self.assertEqual(
                                    (
                                        actual.action_annotated_histories,
                                        actual.distinct_terminal_states,
                                    ),
                                    brute_force(n, a, b, guard_tuple),
                                )
                                cases += 1
        self.assertEqual(cases, 27172)

    def test_disjoint_lunatone_regigigas_guard_geometry(self) -> None:
        # Two named sources: Lunatone/Solrock (2) and
        # Regigigas plus five other named Regis (6); all eight
        # are separate Bench objects for this abstract witness.
        guards = (
            frozenset({0, 1}),
            frozenset({2, 3, 4, 5, 6, 7}),
        )
        result = evaluate(8, 7, 5, guards)
        self.assertEqual(result.action_set_union_sizes, (0, 2, 6, 8))
        self.assertEqual(result.action_annotated_histories, 336)
        self.assertEqual(result.final_survivor_sets, 56)
        self.assertEqual(result.distinct_terminal_states, 148)
        self.assertEqual(brute_force(8, 7, 5, guards), (336, 148))

    def test_shared_prerequisite_reduces_union_cost(self) -> None:
        guards = (frozenset({0, 1}), frozenset({1, 2}))
        x = evaluate(5, 4, 3, guards)
        self.assertEqual(x.action_set_union_sizes, (0, 2, 2, 3))
        self.assertEqual(
            (x.action_annotated_histories, x.distinct_terminal_states),
            brute_force(5, 4, 3, guards),
        )

    def test_invalid_guards(self) -> None:
        with self.assertRaises(ValueError):
            evaluate(5, 4, 3, (frozenset({6}),))
        with self.assertRaises(ValueError):
            evaluate(5, 3, 4, (frozenset({0}),))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    if parser.parse_args().self_test:
        unittest.main(argv=["bench_multi_guard_action_equivalence"], verbosity=2)
    else:
        guards = (frozenset({0, 1}), frozenset({2, 3, 4, 5, 6, 7}))
        print(json.dumps(evaluate(8, 7, 5, guards).__dict__, indent=2))


if __name__ == "__main__":
    main()
