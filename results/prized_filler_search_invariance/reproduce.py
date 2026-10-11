"""SFT: exact no-cost, Prize-invariant retrieval of named non-target cards."""
from __future__ import annotations

from fractions import Fraction

from tools.prized_filler_search_invariance import (
    exact, enumerated, hypergeometric_by_prized_sources,
    physical_observations, physical_subset_distribution,
    target_count_probability, two_type_visibility,
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

    # The stronger theorem is that each full observed subset is uniform
    # among all non-source cards, even after a random Prize exclusion.
    subset_cases = 0
    from math import comb
    for u in range(5, 10):
        for c in range(0, min(3, u)):
            for p in range(0, min(3, u)):
                for s in range(1, min(4, u-c-p)+1):
                    dist = physical_subset_distribution(u,p,c,s)
                    m = u-c
                    assert len(dist) == comb(m,s)
                    assert set(dist.values()) == {Fraction(1,comb(m,s))}
                    for q in range(m+1):
                        targets = set(range(c,c+q))
                        for x in range(min(q,s)+1):
                            observed = sum((
                                weight for subset,weight in dist.items()
                                if sum(i in targets for i in subset) == x
                            ), Fraction(0))
                            assert observed == target_count_probability(u,p,c,s,q,x)
                    for first in range(1, min(3,m)):
                        for second in range(1,min(3,m-first)+1):
                            a = set(range(c,c+first))
                            b = set(range(c+first,c+first+second))
                            hit = sum((
                                weight for subset,weight in dist.items()
                                if bool(a.intersection(subset))
                                and bool(b.intersection(subset))
                            ), Fraction(0))
                            assert hit == two_type_visibility(u,p,c,s,first,second)
                    subset_cases += 1
    print(f"PASS: {subset_cases} fully uniform observation distributions and target-packet laws")

    for p in range(0, 5):
        assert exact(12, p, 1, 5) == Fraction(5, 11)
        assert exact(12, p, 3, 5) == Fraction(5, 9)
    assert exact(12, 2, 3, 5) - exact(12, 2, 1, 5) == Fraction(10, 99)
    print("PASS: Aichi G&H named-source toy reproduces 5/11 -> 5/9")
    print("PASS: mean Ticket access invariant across P=0,1,2,3,4")


if __name__ == "__main__":
    main()
