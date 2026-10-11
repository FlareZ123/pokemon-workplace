"""Exact joint availability and covariance of Bench-guarded intermediate actions.

Given uniform n->a->b Bench contractions, condition on final survivor S.
Each action's enabled event requires all its guard objects in intermediate A.
Compute their exact joint posterior from the *union* of required objects.
"""

from __future__ import annotations

import argparse
import json
import unittest
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations

from bench_guard_history_posterior import posterior
from bench_intermediate_guard_equivalence import choose


@dataclass(frozen=True)
class JointGuardPosterior:
    first_available: Fraction
    second_available: Fraction
    both_available: Fraction
    independent_product: Fraction
    covariance: Fraction
    independence_error: Fraction


def joint_posterior(
    n: int,
    a: int,
    b: int,
    *,
    first_guard: frozenset[int],
    second_guard: frozenset[int],
    final: tuple[int, ...],
) -> JointGuardPosterior:
    """Exact two-action posterior under a uniform conditional intermediate set."""
    first = posterior(n, a, b, guard=first_guard, final=final)
    second = posterior(n, a, b, guard=second_guard, final=final)
    union = posterior(
        n, a, b,
        guard=first_guard | second_guard,
        final=final,
    )
    p1 = first.guard_enabled_posterior
    p2 = second.guard_enabled_posterior
    both = union.guard_enabled_posterior
    independent = p1 * p2
    return JointGuardPosterior(
        first_available=p1,
        second_available=p2,
        both_available=both,
        independent_product=independent,
        covariance=both - independent,
        independence_error=independent - both,
    )


def brute_joint(
    n: int,
    a: int,
    b: int,
    *,
    first_guard: frozenset[int],
    second_guard: frozenset[int],
    final: tuple[int, ...],
) -> tuple[Fraction, Fraction, Fraction]:
    """Independent actual intermediate Bench set enumeration."""
    required_final = frozenset(final)
    count = count_first = count_second = count_both = 0
    for intermediate in combinations(range(n), a):
        live = frozenset(intermediate)
        if required_final <= live:
            count += 1
            x = first_guard <= live
            y = second_guard <= live
            count_first += x
            count_second += y
            count_both += x and y
    return (
        Fraction(count_first, count),
        Fraction(count_second, count),
        Fraction(count_both, count),
    )


def unconditional_joint(n: int, a: int,
                        first_guard: frozenset[int],
                        second_guard: frozenset[int]) -> JointGuardPosterior:
    """Unconditioned pair of event indicators at intermediate capacity a."""
    if not 0 <= a <= n:
        raise ValueError("invalid capacity")
    if any(not isinstance(i, int) or i < 0 or i >= n
           for i in first_guard | second_guard):
        raise ValueError("guard outside original Bench")
    total = choose(n, a)
    p1 = Fraction(choose(n-len(first_guard), a-len(first_guard)), total)
    p2 = Fraction(choose(n-len(second_guard), a-len(second_guard)), total)
    union = first_guard | second_guard
    p12 = Fraction(choose(n-len(union), a-len(union)), total)
    return JointGuardPosterior(
        p1, p2, p12, p1*p2, p12-p1*p2, p1*p2-p12
    )


class JointPosteriorTests(unittest.TestCase):
    def test_every_two_guard_pair_and_final_set_through_five(self) -> None:
        checked = 0
        for n in range(6):
            guards = tuple(
                frozenset(i for i in range(n) if mask & (1 << i))
                for mask in range(1 << n)
            )
            for first_guard in guards:
                for second_guard in guards:
                    for a in range(n+1):
                        for b in range(a+1):
                            for final in combinations(range(n), b):
                                with self.subTest(n=n, a=a, b=b,
                                                  first=first_guard,
                                                  second=second_guard,
                                                  final=final):
                                    x = joint_posterior(
                                        n, a, b,
                                        first_guard=first_guard,
                                        second_guard=second_guard,
                                        final=final,
                                    )
                                    self.assertEqual(
                                        (
                                            x.first_available,
                                            x.second_available,
                                            x.both_available,
                                        ),
                                        brute_joint(
                                            n, a, b,
                                            first_guard=first_guard,
                                            second_guard=second_guard,
                                            final=final,
                                        ),
                                    )
                                    checked += 1
        self.assertEqual(checked, 128397)

    def test_disjoint_named_luna_regi_guards_anticorrelate(self) -> None:
        first = frozenset({0, 1})
        second = frozenset({2, 3, 4, 5, 6, 7})
        x = unconditional_joint(8, 7, first, second)
        self.assertEqual(
            (x.first_available, x.second_available,
             x.both_available, x.independent_product, x.covariance),
            (Fraction(3, 4), Fraction(1, 4),
             Fraction(0), Fraction(3, 16), Fraction(-3, 16)),
        )
        conditional = joint_posterior(
            8, 7, 5,
            first_guard=first, second_guard=second,
            final=(0, 2, 3, 4, 5),
        )
        self.assertEqual(
            (conditional.first_available,
             conditional.second_available,
             conditional.both_available,
             conditional.independent_product,
             conditional.covariance),
            (Fraction(2, 3), Fraction(1, 3),
             Fraction(0), Fraction(2, 9), Fraction(-2, 9)),
        )

    def test_shared_missing_guard_positive_correlation(self) -> None:
        x = joint_posterior(
            5, 4, 3,
            first_guard=frozenset({0, 1}),
            second_guard=frozenset({1, 2}),
            final=(0, 2, 3),
        )
        self.assertEqual(
            (x.first_available,
             x.second_available,
             x.both_available,
             x.independent_product,
             x.covariance),
            (
                Fraction(1, 2), Fraction(1, 2),
                Fraction(1, 2), Fraction(1, 4), Fraction(1, 4),
            ),
        )

    def test_invalid_parameters(self) -> None:
        with self.assertRaises(ValueError):
            joint_posterior(
                5, 4, 3, first_guard=frozenset({7}),
                second_guard=frozenset(), final=(0, 1, 2)
            )
        with self.assertRaises(ValueError):
            unconditional_joint(5, 6, frozenset(), frozenset())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    if parser.parse_args().self_test:
        unittest.main(argv=["bench_guard_joint_posterior"], verbosity=2)
    else:
        a = frozenset({0, 1})
        b = frozenset({2, 3, 4, 5, 6, 7})
        print(json.dumps({
            "eight_slot_intermediate_joint": {
                k: str(v) for k, v in
                unconditional_joint(8, 7, a, b).__dict__.items()
            },
            "conditional_after_five_survivors": {
                k: str(v) for k, v in joint_posterior(
                    8, 7, 5, first_guard=a, second_guard=b,
                    final=(0, 2, 3, 4, 5)
                ).__dict__.items()
            },
        }, indent=2))


if __name__ == "__main__":
    main()
