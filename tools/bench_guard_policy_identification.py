"""Policy-free identification limits for hidden intermediate Bench guard state.

After conditioning on final S, let N=n-b original objects be absent, k=a-b
of them have survived temporarily, and g of them be missing guard objects.
Give every missing guard weight t>0 and every other absent object weight 1.
The guard-enabled posterior is a rational binomial polynomial in t.
"""

from __future__ import annotations

import argparse
import json
import unittest
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations

from bench_intermediate_guard_equivalence import choose


@dataclass(frozen=True)
class GuardIdentification:
    unseen_outside_final: int
    temporarily_retained_outside_final: int
    missing_guard_objects: int
    classification: str
    posterior: Fraction


def posterior_tilt(
    N: int, k: int, g: int,
    *, guard_retention_ratio: Fraction,
) -> GuardIdentification:
    """Exact posterior under equal t weights for all missing guard members."""
    if not 0 <= k <= N or not 0 <= g <= N:
        raise ValueError("expected 0 <= k,g <= N")
    if guard_retention_ratio <= 0:
        raise ValueError("retention ratio must be positive")

    low = max(0, k-(N-g))
    high = min(k, g)
    norm = sum(
        (choose(g, j) * choose(N-g, k-j) * guard_retention_ratio**j
         for j in range(low, high+1)),
        start=Fraction(0),
    )
    joint = choose(N-g, k-g) * guard_retention_ratio**g
    p = joint / norm

    if g == 0 or k == N:
        status = "certain"
        assert p == 1
    elif g > k:
        status = "impossible"
        assert p == 0
    else:
        status = "policy_sensitive"
        assert 0 < p < 1
    return GuardIdentification(N, k, g, status, p)


def brute_tilt(
    N: int, k: int, g: int,
    t: Fraction,
) -> Fraction:
    """Independent weighted enumeration of each intermediate-choice subset."""
    guard = frozenset(range(g))
    total = enabled = Fraction(0)
    for intermediate in combinations(range(N), k):
        live = frozenset(intermediate)
        weight = t**len(guard & live)
        total += weight
        if guard <= live:
            enabled += weight
    return enabled/total


class GuardIdentificationTests(unittest.TestCase):
    def test_all_eight_item_geometries_and_odds(self) -> None:
        cases = 0
        for N in range(9):
            for k in range(N+1):
                for g in range(N+1):
                    for t in (Fraction(1, 5), Fraction(1),
                              Fraction(5), Fraction(25)):
                        x = posterior_tilt(
                            N, k, g, guard_retention_ratio=t
                        )
                        self.assertEqual(x.posterior, brute_tilt(N,k,g,t))
                        cases += 1
        self.assertEqual(cases, 1140)

    def test_classification_exhaustive_monotonicity(self) -> None:
        for N in range(9):
            for k in range(N+1):
                for g in range(N+1):
                    x = posterior_tilt(
                        N,k,g,guard_retention_ratio=Fraction(1)
                    )
                    p_low = posterior_tilt(
                        N,k,g,guard_retention_ratio=Fraction(1,1000)
                    ).posterior
                    p_high = posterior_tilt(
                        N,k,g,guard_retention_ratio=Fraction(1000)
                    ).posterior
                    if x.classification == "policy_sensitive":
                        self.assertLess(p_low, x.posterior)
                        self.assertLess(x.posterior, p_high)
                    else:
                        self.assertEqual(p_low, x.posterior)
                        self.assertEqual(x.posterior, p_high)

    def test_lunatone_hidden_missing_guard(self) -> None:
        # In the 5->4->3 example, N=2, k=1, g=1.
        values = [
            posterior_tilt(
                2,1,1,guard_retention_ratio=t
            ).posterior
            for t in (Fraction(1,1000), Fraction(1), Fraction(9),
                      Fraction(1000))
        ]
        self.assertEqual(values, [
            Fraction(1,1001), Fraction(1,2), Fraction(9,10),
            Fraction(1000,1001),
        ])

    def test_structural_certainty_and_impossibility(self) -> None:
        self.assertEqual(
            posterior_tilt(3,2,0,guard_retention_ratio=Fraction(9)
            ).classification, "certain"
        )
        self.assertEqual(
            posterior_tilt(3,3,2,guard_retention_ratio=Fraction(9)
            ).classification, "certain"
        )
        self.assertEqual(
            posterior_tilt(3,1,2,guard_retention_ratio=Fraction(9)
            ).classification, "impossible"
        )

    def test_invalid_parameters(self) -> None:
        for args in ((2,3,1,Fraction(1)), (2,1,3,Fraction(1)),
                     (2,1,1,Fraction(0))):
            with self.assertRaises(ValueError):
                posterior_tilt(
                    args[0],args[1],args[2],
                    guard_retention_ratio=args[3],
                )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    if parser.parse_args().self_test:
        unittest.main(argv=["bench_guard_policy_identification"], verbosity=2)
    else:
        print(json.dumps([
            {
                "guard_retention_ratio": str(t),
                "posterior": str(
                    posterior_tilt(
                        2,1,1,guard_retention_ratio=t
                    ).posterior
                ),
            }
            for t in (Fraction(1,1000), Fraction(1),
                      Fraction(9), Fraction(1000))
        ], indent=2))


if __name__ == "__main__":
    main()
