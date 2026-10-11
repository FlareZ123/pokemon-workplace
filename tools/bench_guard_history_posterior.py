"""Exact latent intermediate-guard availability from final Bench survivors.

Assume each forced contraction retains a uniformly random legal survivor set:
n -> a -> b. Conditional on final survivor set S, the intermediate a-set
is uniformly distributed over supersets of S. A guard G was enabled at
the intermediate stage precisely if G was a subset of that a-set.

This is a *hypothetical random-discard policy*, not rational game strategy.
"""

from __future__ import annotations

import argparse
import json
import unittest
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb

from bench_intermediate_guard_equivalence import choose


@dataclass(frozen=True)
class GuardPosterior:
    initial_occupancy: int
    intermediate_capacity: int
    final_capacity: int
    guard_size: int
    guard_retained_in_final: int
    intermediate_paths_to_final: int
    guard_enabled_paths_to_final: int
    guard_enabled_posterior: Fraction


def posterior(
    n: int,
    a: int,
    b: int,
    *,
    guard: frozenset[int],
    final: tuple[int, ...],
) -> GuardPosterior:
    """Exact conditional probability of an intermediate guard given final S."""
    if not 0 <= b <= a <= n:
        raise ValueError("expected monotone capacities 0 <= b <= a <= n")
    if len(final) != b or len(set(final)) != b:
        raise ValueError("final survivor set has invalid cardinality")
    if any(not isinstance(i, int) or i < 0 or i >= n for i in final):
        raise ValueError("invalid final survivor identity")
    if any(not isinstance(i, int) or i < 0 or i >= n for i in guard):
        raise ValueError("invalid guard identity")
    missing_guards = len(guard.difference(final))
    all_paths = choose(n - b, a - b)
    eligible_paths = choose(n - b - missing_guards,
                            a - b - missing_guards)
    return GuardPosterior(
        initial_occupancy=n,
        intermediate_capacity=a,
        final_capacity=b,
        guard_size=len(guard),
        guard_retained_in_final=len(guard) - missing_guards,
        intermediate_paths_to_final=all_paths,
        guard_enabled_paths_to_final=eligible_paths,
        guard_enabled_posterior=Fraction(eligible_paths, all_paths),
    )


def endpoint_weights(
    n: int,
    a: int,
    b: int,
    *,
    guard: frozenset[int],
    final: tuple[int, ...],
    use_when_available: Fraction,
) -> tuple[Fraction, Fraction]:
    """Return P(final S, action used), P(final S, action not used).

    The optional action is performed with conditional probability p in an
    eligible intermediate state, independently of which intermediate A
    was selected. Its fixed resource effect is distinguishable.
    """
    if not 0 <= use_when_available <= 1:
        raise ValueError("action-use probability must lie in [0,1]")
    enabled = posterior(n, a, b, guard=guard, final=final)
    p_final = Fraction(1, comb(n, b))
    p_used = p_final * enabled.guard_enabled_posterior * use_when_available
    return p_used, p_final - p_used


def brute_posterior(
    n: int,
    a: int,
    b: int,
    *,
    guard: frozenset[int],
    final: tuple[int, ...],
) -> tuple[int, int]:
    """Independent enumeration over actual intermediate occupant sets."""
    target = frozenset(final)
    total = eligible = 0
    for intermediate in combinations(range(n), a):
        chosen = frozenset(intermediate)
        if target <= chosen:
            total += 1
            eligible += guard <= chosen
    return total, eligible


def census(n: int, a: int, b: int, *, guard: frozenset[int],
           probability: Fraction) -> dict[str, Fraction]:
    """Marginally sum the complete terminal-state probabilities."""
    used = skipped = Fraction(0)
    for final in combinations(range(n), b):
        current_used, current_skipped = endpoint_weights(
            n, a, b,
            guard=guard,
            final=final,
            use_when_available=probability,
        )
        used += current_used
        skipped += current_skipped
    expected_used = probability * Fraction(
        choose(n - len(guard), a - len(guard)),
        choose(n, a),
    )
    assert used == expected_used
    assert used + skipped == 1
    return {"used": used, "not_used": skipped}


class PosteriorTests(unittest.TestCase):
    def test_exact_all_small_configs_and_final_survivors(self) -> None:
        cases = 0
        for n in range(9):
            for d in range(n + 1):
                guard = frozenset(range(d))
                for a in range(n + 1):
                    for b in range(a + 1):
                        for final in combinations(range(n), b):
                            actual = posterior(
                                n, a, b, guard=guard, final=final
                            )
                            self.assertEqual(
                                (actual.intermediate_paths_to_final,
                                 actual.guard_enabled_paths_to_final),
                                brute_posterior(
                                    n, a, b, guard=guard, final=final
                                ),
                            )
                            cases += 1
        self.assertEqual(cases, 18943)

    def test_lunatone_posterior_depends_on_final_partner_count(self) -> None:
        guard = frozenset((0, 1))
        r2 = posterior(5, 4, 3, guard=guard, final=(0, 1, 2))
        r1 = posterior(5, 4, 3, guard=guard, final=(0, 2, 3))
        r0 = posterior(5, 4, 3, guard=guard, final=(2, 3, 4))
        self.assertEqual(
            (
                r2.guard_enabled_posterior,
                r1.guard_enabled_posterior,
                r0.guard_enabled_posterior,
            ),
            (Fraction(1), Fraction(1, 2), Fraction(0)),
        )
        self.assertEqual(
            census(5, 4, 3, guard=guard, probability=Fraction(1)),
            {"used": Fraction(3, 5), "not_used": Fraction(2, 5)},
        )

    def test_partial_optional_action_probability(self) -> None:
        result = census(
            5, 4, 3, guard=frozenset((0, 1)),
            probability=Fraction(1, 2),
        )
        self.assertEqual(
            result, {"used": Fraction(3, 10),
                     "not_used": Fraction(7, 10)},
        )

    def test_larger_eight_slot_example(self) -> None:
        guard = frozenset(range(6))
        p5 = posterior(8, 7, 5, guard=guard, final=(0, 1, 2, 3, 4))
        p4 = posterior(8, 7, 5, guard=guard, final=(0, 1, 2, 3, 6))
        p3 = posterior(8, 7, 5, guard=guard, final=(0, 1, 2, 6, 7))
        self.assertEqual(
            (
                p5.guard_enabled_posterior,
                p4.guard_enabled_posterior,
                p3.guard_enabled_posterior,
            ),
            (Fraction(2, 3), Fraction(1, 3), Fraction(0)),
        )
        self.assertEqual(
            census(8, 7, 5, guard=guard, probability=Fraction(1)),
            {"used": Fraction(1, 4), "not_used": Fraction(3, 4)},
        )

    def test_invalid_inputs(self) -> None:
        with self.assertRaises(ValueError):
            posterior(5, 3, 4, guard=frozenset(), final=(0, 1, 2, 3))
        with self.assertRaises(ValueError):
            posterior(5, 4, 3, guard=frozenset({5}), final=(0, 1, 2))
        with self.assertRaises(ValueError):
            endpoint_weights(
                5, 4, 3, guard=frozenset(), final=(0, 1, 2),
                use_when_available=Fraction(3, 2),
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    if parser.parse_args().self_test:
        unittest.main(argv=["bench_guard_history_posterior"], verbosity=2)
    else:
        g = frozenset((0, 1))
        output = {
            "posterior_by_final_guard_count": {
                str(r): str(posterior(
                    5, 4, 3,
                    guard=g,
                    final={
                        2: (0, 1, 2),
                        1: (0, 2, 3),
                        0: (2, 3, 4),
                    }[r],
                ).guard_enabled_posterior)
                for r in (2, 1, 0)
            },
            "always_use_marginal": {
                k: str(v) for k, v in
                census(5, 4, 3, guard=g,
                       probability=Fraction(1)).items()
            },
        }
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
