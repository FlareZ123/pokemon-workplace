"""Exact policy-aware guard-history posterior for weighted Bench contractions.

Each a-survivor first-stage Bench subset has probability proportional to
the product of positive retained-occupant weights. The second contraction
can be uniform (fast elementary-symmetric-polynomial formula) or use a
separate product-weight survivor policy (exact finite-sum formula).

Weights are stylized action-policy parameters, not calibrated player data.
"""

from __future__ import annotations

import argparse
import json
import unittest
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb, prod

from bench_guard_history_posterior import posterior


def _product(indices: frozenset[int] | tuple[int, ...],
             weights: tuple[Fraction, ...]) -> Fraction:
    return prod((weights[i] for i in indices), start=Fraction(1))


def elementary_symmetric(weights: tuple[Fraction, ...], k: int) -> Fraction:
    """Exact k-subset product sum, O(k*number of weights)."""
    if k < 0 or k > len(weights):
        return Fraction(0)
    dp = [Fraction(0) for _ in range(k+1)]
    dp[0] = Fraction(1)
    for i, weight in enumerate(weights):
        for j in range(min(i+1, k), 0, -1):
            dp[j] += weight*dp[j-1]
    return dp[k]


def _validate(
    n: int, a: int, b: int,
    guard: frozenset[int], final: tuple[int, ...],
    weights: tuple[Fraction, ...],
) -> None:
    posterior(n, a, b, guard=guard, final=final)
    if len(weights) != n or any(weight <= 0 for weight in weights):
        raise ValueError("exactly n positive retention weights are required")


@dataclass(frozen=True)
class WeightedGuardPosterior:
    final_probability: Fraction
    joint_final_and_guard_probability: Fraction
    guard_given_final: Fraction


def weighted_first_uniform_second(
    n: int, a: int, b: int,
    *, guard: frozenset[int], final: tuple[int, ...],
    first_weights: tuple[Fraction, ...],
) -> WeightedGuardPosterior:
    """Weighted first contraction, uniform second, using symmetric polynomials."""
    _validate(n, a, b, guard, final, first_weights)
    final_set = frozenset(final)
    outside = frozenset(range(n)).difference(final_set)
    missing_guard = guard.difference(final_set)
    eligible_remaining = outside.difference(missing_guard)

    norm = elementary_symmetric(first_weights, a)
    pS_factor = _product(final_set, first_weights) / (
        norm * comb(a, b)
    )
    p_final = pS_factor * elementary_symmetric(
        tuple(first_weights[i] for i in sorted(outside)), a-b
    )
    p_both = pS_factor * _product(missing_guard, first_weights) * (
        elementary_symmetric(
            tuple(first_weights[i] for i in sorted(eligible_remaining)),
            a-b-len(missing_guard),
        )
    )
    return WeightedGuardPosterior(
        final_probability=p_final,
        joint_final_and_guard_probability=p_both,
        guard_given_final=p_both/p_final,
    )


def weighted_both_stages(
    n: int, a: int, b: int,
    *, guard: frozenset[int], final: tuple[int, ...],
    first_weights: tuple[Fraction, ...],
    second_weights: tuple[Fraction, ...],
) -> WeightedGuardPosterior:
    """Exact conditional finite-sum solution with two weighted survivor policies."""
    _validate(n, a, b, guard, final, first_weights)
    _validate(n, a, b, guard, final, second_weights)

    final_set = frozenset(final)
    outside = sorted(frozenset(range(n)).difference(final_set))
    missing_guard = guard.difference(final_set)
    denominator = numerator = Fraction(0)
    for extras in combinations(outside, a-b):
        intermediate = final_set.union(extras)
        # The factors from final S cancel in the conditional posterior.
        score = _product(extras, first_weights) / elementary_symmetric(
            tuple(second_weights[i] for i in sorted(intermediate)), b
        )
        denominator += score
        if missing_guard <= intermediate:
            numerator += score

    scale = _product(final_set, first_weights) * (
        _product(final_set, second_weights)
    ) / elementary_symmetric(first_weights, a)
    return WeightedGuardPosterior(
        final_probability=scale*denominator,
        joint_final_and_guard_probability=scale*numerator,
        guard_given_final=numerator/denominator,
    )


def brute_two_stage(
    n: int, a: int, b: int,
    *, guard: frozenset[int], final: tuple[int, ...],
    first_weights: tuple[Fraction, ...],
    second_weights: tuple[Fraction, ...] | None = None,
) -> WeightedGuardPosterior:
    """Independent full two-stage transition enumeration."""
    second = (
        second_weights if second_weights is not None
        else (Fraction(1),)*n
    )
    norm = sum(
        (_product(intermediate, first_weights)
         for intermediate in combinations(range(n), a)),
        start=Fraction(0),
    )
    final_set = frozenset(final)
    p_final = p_both = Fraction(0)
    for intermediate in combinations(range(n), a):
        live = frozenset(intermediate)
        first_prob = _product(intermediate, first_weights) / norm
        norm_second = sum(
            (_product(survivors, second)
             for survivors in combinations(intermediate, b)),
            start=Fraction(0),
        )
        for survivors in combinations(intermediate, b):
            if frozenset(survivors) == final_set:
                p = first_prob * _product(survivors, second)/norm_second
                p_final += p
                if guard <= live:
                    p_both += p
    return WeightedGuardPosterior(
        p_final, p_both, p_both/p_final
    )


class WeightedPosteriorTests(unittest.TestCase):
    def test_uniform_second_symmetry_formula_independent_oracle(self) -> None:
        tested = 0
        for n in range(8):
            profiles = (
                (Fraction(1),)*n,
                tuple(Fraction(1+(i % 3)) for i in range(n)),
                tuple(Fraction(2*i+1, i+1) for i in range(n)),
            )
            for first_weights in profiles:
                for d in range(n+1):
                    guard = frozenset(range(d))
                    for a in range(n+1):
                        for b in range(a+1):
                            for final in combinations(range(n), b):
                                with self.subTest(n=n, d=d, a=a, b=b,
                                                  final=final,
                                                  first_weights=first_weights):
                                    result = weighted_first_uniform_second(
                                        n, a, b, guard=guard, final=final,
                                        first_weights=first_weights,
                                    )
                                    self.assertEqual(
                                        result,
                                        brute_two_stage(
                                            n, a, b,
                                            guard=guard, final=final,
                                            first_weights=first_weights,
                                        ),
                                    )
                                    if all(x == 1 for x in first_weights):
                                        self.assertEqual(
                                            result.guard_given_final,
                                            posterior(
                                                n, a, b,
                                                guard=guard, final=final
                                            ).guard_enabled_posterior
                                        )
                                    tested += 1
        self.assertEqual(tested, 22269)

    def test_first_stage_weights_change_inference(self) -> None:
        n, a, b = 5, 4, 3
        final = (0, 2, 3)
        guard = frozenset({0, 1})
        pro = weighted_first_uniform_second(
            n, a, b, guard=guard, final=final,
            first_weights=(
                Fraction(1), Fraction(9), Fraction(1),
                Fraction(1), Fraction(1),
            ),
        )
        anti = weighted_first_uniform_second(
            n, a, b, guard=guard, final=final,
            first_weights=(
                Fraction(1), Fraction(1), Fraction(1),
                Fraction(1), Fraction(9),
            ),
        )
        self.assertEqual(pro.guard_given_final, Fraction(9, 10))
        self.assertEqual(anti.guard_given_final, Fraction(1, 10))

    def test_second_stage_weights_can_reverse_inference(self) -> None:
        first = (Fraction(1),)*5
        guard = frozenset({0, 1})
        final = (0, 2, 3)
        low = weighted_both_stages(
            5, 4, 3, guard=guard, final=final,
            first_weights=first,
            second_weights=(
                Fraction(1), Fraction(9), Fraction(1),
                Fraction(1), Fraction(1),
            ),
        )
        high = weighted_both_stages(
            5, 4, 3, guard=guard, final=final,
            first_weights=first,
            second_weights=(
                Fraction(1), Fraction(1), Fraction(1),
                Fraction(1), Fraction(9),
            ),
        )
        self.assertEqual(low.guard_given_final, Fraction(1, 8))
        self.assertEqual(high.guard_given_final, Fraction(7, 8))
        self.assertEqual(
            low,
            brute_two_stage(
                5, 4, 3, guard=guard, final=final,
                first_weights=first,
                second_weights=(
                    Fraction(1), Fraction(9), Fraction(1),
                    Fraction(1), Fraction(1),
                ),
            )
        )
        self.assertEqual(
            high,
            brute_two_stage(
                5, 4, 3, guard=guard, final=final,
                first_weights=first,
                second_weights=(
                    Fraction(1), Fraction(1), Fraction(1),
                    Fraction(1), Fraction(9),
                ),
            )
        )

    def test_probability_normalization_weighted_stages(self) -> None:
        for n, a, b in ((5,4,3), (6,3,2), (8,7,5)):
            w = tuple(Fraction(i+1) for i in range(n))
            v = tuple(Fraction(n-i) for i in range(n))
            for name, function in (
                ("first", lambda s: weighted_first_uniform_second(
                    n, a, b, guard=frozenset(range(min(n,2))),
                    final=s, first_weights=w,
                )),
                ("both", lambda s: weighted_both_stages(
                    n, a, b, guard=frozenset(range(min(n,2))),
                    final=s, first_weights=w, second_weights=v,
                )),
            ):
                probabilities = [
                    function(s).final_probability
                    for s in combinations(range(n), b)
                ]
                self.assertEqual(sum(probabilities, Fraction(0)), 1,
                                 msg=(n, a, b, name))

    def test_invalid_weights(self) -> None:
        with self.assertRaises(ValueError):
            weighted_first_uniform_second(
                5, 4, 3, guard=frozenset(),
                final=(0, 1, 2),
                first_weights=(Fraction(1),)*4,
            )
        with self.assertRaises(ValueError):
            weighted_both_stages(
                5, 4, 3, guard=frozenset(),
                final=(0, 1, 2),
                first_weights=(Fraction(1),)*5,
                second_weights=(Fraction(1), Fraction(0), Fraction(1),
                                Fraction(1), Fraction(1)),
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    if parser.parse_args().self_test:
        unittest.main(argv=["bench_weighted_guard_history_posterior"], verbosity=2)
    else:
        n, a, b = 5, 4, 3
        kwargs = {"guard": frozenset({0,1}), "final": (0,2,3)}
        examples = {
            "uniform": str(weighted_first_uniform_second(
                n, a, b, **kwargs,
                first_weights=(Fraction(1),)*5
            ).guard_given_final),
            "first_stage_guard_preference": str(
                weighted_first_uniform_second(
                    n, a, b, **kwargs,
                    first_weights=(Fraction(1),Fraction(9),Fraction(1),
                                   Fraction(1),Fraction(1))
                ).guard_given_final
            ),
            "second_stage_guard_retention_preference": str(
                weighted_both_stages(
                    n, a, b, **kwargs,
                    first_weights=(Fraction(1),)*5,
                    second_weights=(Fraction(1),Fraction(9),Fraction(1),
                                    Fraction(1),Fraction(1))
                ).guard_given_final
            ),
        }
        print(json.dumps(examples, indent=2))


if __name__ == "__main__":
    main()
