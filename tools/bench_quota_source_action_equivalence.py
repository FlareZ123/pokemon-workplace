"""Exact action-history quotients with a live Bench-based Supporter quota grant.

A normal one-Supporter limit permits choosing zero or one of two distinct
abstract Supporter transactions. An unsuppressed in-play Magnezone bw8-46
Dual Brains source raises the limit to two for the current turn. This model
treats each Supporter transaction as resource-ready with a distinct final
off-board effect, isolating quota-source/Bench-state geometry.
"""

from __future__ import annotations

import argparse
import json
import unittest
from dataclasses import dataclass
from itertools import combinations, product

from bench_intermediate_guard_equivalence import choose


@dataclass(frozen=True)
class QuotaEquivalence:
    original_bench: int
    intermediate_capacity: int
    final_capacity: int
    source_object: int
    support_transactions: int
    ordinary_one_supporter_histories: int
    live_source_extra_histories: int
    all_action_histories: int
    ordinary_terminal_states: int
    live_source_extra_states: int
    total_terminal_states: int


def _guard_union(
    subset: tuple[int, ...],
    guards: tuple[frozenset[int], ...],
    *,
    quota_source: int,
) -> frozenset[int]:
    required = frozenset().union(*(guards[j] for j in subset))
    if len(subset) == 2:
        required |= frozenset({quota_source})
    return required


def _final_reachable_sets(n: int, a: int, b: int, d: int) -> int:
    if a < d:
        return 0
    return sum(
        choose(d, r) * choose(n - d, b - r)
        for r in range(max(0, b + d - a), min(d, b) + 1)
    )


def evaluate(
    n: int,
    a: int,
    b: int,
    *,
    source: int,
    guards: tuple[frozenset[int], ...],
) -> QuotaEquivalence:
    """Closed-form quotient with a two-Supporter live-source ceiling."""
    if not 1 <= n or not 0 <= b <= a <= n:
        raise ValueError("invalid Bench capacity progression")
    if not 0 <= source < n:
        raise ValueError("quota source must be one of the original Bench objects")
    if any(not all(isinstance(i, int) and 0 <= i < n for i in guard)
           for guard in guards):
        raise ValueError("invalid action guard")
    if len(guards) > 3:
        raise ValueError("at most three alternative Supporter transactions")

    ordinary_histories = source_histories = 0
    ordinary_states = source_states = 0
    for k in range(min(2, len(guards)) + 1):
        for subset in combinations(range(len(guards)), k):
            d = len(_guard_union(subset, guards, quota_source=source))
            h = choose(n - d, a - d) * choose(a, b)
            q = _final_reachable_sets(n, a, b, d)
            if k < 2:
                ordinary_histories += h
                ordinary_states += q
            else:
                source_histories += h
                source_states += q
    return QuotaEquivalence(
        original_bench=n,
        intermediate_capacity=a,
        final_capacity=b,
        source_object=source,
        support_transactions=len(guards),
        ordinary_one_supporter_histories=ordinary_histories,
        live_source_extra_histories=source_histories,
        all_action_histories=ordinary_histories + source_histories,
        ordinary_terminal_states=ordinary_states,
        live_source_extra_states=source_states,
        total_terminal_states=ordinary_states + source_states,
    )


def brute_force(
    n: int,
    a: int,
    b: int,
    *,
    source: int,
    guards: tuple[frozenset[int], ...],
) -> tuple[int, int, int, int]:
    """Independent explicit source-presence, action-subset and board scan."""
    histories_ordinary = histories_extra = 0
    states_ordinary: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    states_extra: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    original = tuple(range(n))
    for intermediate in combinations(original, a):
        live = frozenset(intermediate)
        quota = 2 if source in live else 1
        options = tuple(
            i for i, guard in enumerate(guards)
            if guard <= live
        )
        for final in combinations(intermediate, b):
            for k in range(min(len(options), quota) + 1):
                for subset in combinations(options, k):
                    item = (final, subset)
                    if k < 2:
                        histories_ordinary += 1
                        states_ordinary.add(item)
                    else:
                        histories_extra += 1
                        states_extra.add(item)
    return (
        histories_ordinary,
        histories_extra,
        len(states_ordinary),
        len(states_extra),
    )


class QuotaEquivalenceTests(unittest.TestCase):
    def test_every_small_two_action_guard_pair(self) -> None:
        checked = 0
        for n in range(1, 6):
            possible = tuple(
                frozenset(i for i in range(n) if (mask & (1 << i)))
                for mask in range(1 << n)
            )
            for source in range(n):
                for guards in product(possible, repeat=2):
                    for a in range(n + 1):
                        for b in range(a + 1):
                            with self.subTest(n=n, a=a, b=b,
                                              source=source, guards=guards):
                                actual = evaluate(
                                    n, a, b,
                                    source=source, guards=guards,
                                )
                                self.assertEqual(
                                    (
                                        actual.ordinary_one_supporter_histories,
                                        actual.live_source_extra_histories,
                                        actual.ordinary_terminal_states,
                                        actual.live_source_extra_states,
                                    ),
                                    brute_force(
                                        n, a, b,
                                        source=source, guards=guards,
                                    ),
                                )
                                checked += 1
        self.assertEqual(checked, 125004)

    def test_magnezone_disappearing_from_final_bench(self) -> None:
        # Two fully resource-ready abstract Supporter transactions,
        # no other source restrictions; Magnezone object 0 grants quota 2.
        r = evaluate(5, 4, 3, source=0, guards=(frozenset(), frozenset()))
        self.assertEqual(
            (
                r.ordinary_one_supporter_histories,
                r.live_source_extra_histories,
                r.all_action_histories,
                r.ordinary_terminal_states,
                r.live_source_extra_states,
                r.total_terminal_states,
            ),
            (60, 16, 76, 30, 10, 40),
        )
        first_with_grant = (0, 1, 2, 3)
        second_without_grant = (1, 2, 3)
        assert 0 in first_with_grant
        assert 0 not in second_without_grant
        # Two Supporters played while Magnezone was live remain historical
        # legal usage even after its source leaves during contraction.

    def test_source_gone_at_first_step_prevents_double_support(self) -> None:
        r = evaluate(5, 3, 3, source=0, guards=(frozenset(), frozenset()))
        self.assertEqual(
            (r.ordinary_terminal_states,
             r.live_source_extra_states,
             r.total_terminal_states),
            (30, 6, 36),
        )

    def test_three_options_include_three_distinct_pairs(self) -> None:
        guards = (frozenset(),) * 3
        r = evaluate(5, 4, 3, source=0, guards=guards)
        self.assertEqual(
            (r.all_action_histories, r.total_terminal_states),
            (128, 70),
        )
        self.assertEqual(
            (
                r.ordinary_one_supporter_histories,
                r.live_source_extra_histories,
                r.ordinary_terminal_states,
                r.live_source_extra_states,
            ),
            brute_force(5, 4, 3, source=0, guards=guards),
        )

    def test_invalid_inputs(self) -> None:
        for args in (
            (0, 0, 0, 0),
            (5, 3, 4, 0),
            (5, 4, 3, 5),
        ):
            with self.assertRaises(ValueError):
                evaluate(
                    args[0], args[1], args[2],
                    source=args[3], guards=(frozenset(),),
                )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    if parser.parse_args().self_test:
        unittest.main(argv=["bench_quota_source_action_equivalence"], verbosity=2)
    else:
        print(json.dumps([
            evaluate(5, 4, 3, source=0,
                     guards=(frozenset(), frozenset())).__dict__,
            evaluate(5, 3, 3, source=0,
                     guards=(frozenset(), frozenset())).__dict__,
        ], indent=2))


if __name__ == "__main__":
    main()
