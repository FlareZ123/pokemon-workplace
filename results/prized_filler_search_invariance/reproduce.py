"""SFT: exact no-cost, Prize-invariant retrieval of named non-target cards."""
from __future__ import annotations

from fractions import Fraction

from tools.prized_filler_search_invariance import (
    exact, enumerated, hypergeometric_by_prized_sources,
    physical_observations,
)


def main() -> None:
    cases = 0
    for u in range(4, 15):
        for c in range(0, min(4, u)):
            for p in range(0, min(5, u)):
                for s in range(1, min(5, u-c-p)+1):
                    target = Fraction(s, u-c)
                    assert exact(u, p, c, s) == target
                    assert enumerated(u, p, c, s) == target
                    assert hypergeometric_by_prized_sources(u, p, c, s) == target
                    cases += 1
    print(f"PASS: {cases} exact formula, prize-subset and stratum decompositions")

    fully_physical = 0
    for u in range(4, 10):
        for c in range(0, min(3, u)):
            for p in range(0, min(3, u)):
                for s in range(1, min(3, u-c-p)+1):
                    assert physical_observations(u, p, c, s) == exact(u, p, c, s)
                    fully_physical += 1
    print(f"PASS: {fully_physical} independent exhaustive Prize plus top-card-subset models")

    for p in range(0, 5):
        assert exact(12, p, 1, 5) == Fraction(5, 11)
        assert exact(12, p, 3, 5) == Fraction(5, 9)
    assert exact(12, 2, 3, 5) - exact(12, 2, 1, 5) == Fraction(10, 99)
    print("PASS: Aichi G&H named-source toy reproduces 5/11 -> 5/9")
    print("PASS: mean Ticket access invariant across P=0,1,2,3,4")


if __name__ == "__main__":
    main()
