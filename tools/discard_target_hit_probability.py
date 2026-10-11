"""Exact finite-deck target hit after an explicit multi-card discard.

For a population of N cards containing K copies of a needed target,
drawing n without replacement succeeds with probability
  1 - C(N-K,n)/C(N,n).
When m cards are removed from the future draw population, of which
t are target copies, use (N-m,K-t) for the new probability.

If the post-discard target density does not fall, the n-card hit
probability cannot fall. This is a sufficient (not necessary) test.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import comb


@lru_cache(maxsize=None)
def hit_probability(N: int,K: int,n: int) -> Fraction:
    if not (0<=K<=N and 0<=n<=N):
        raise ValueError("Need N>=K>=0 and 0<=n<=N")
    return 1-Fraction(comb(N-K,n) if n<=N-K else 0,comb(N,n))


@lru_cache(maxsize=None)
def discard_hit_change(N: int,K: int,n: int,m: int,t: int):
    """Return baseline, after-discard, and exact signed difference."""
    if not (0<=t<=K and 0<=m-t<=N-K and
            0<=m<=N and 0<=n<=N-m):
        raise ValueError("Invalid physical target/non-target discard")
    before=hit_probability(N,K,n)
    after=hit_probability(N-m,K-t,n)
    density_sufficient=Fraction(K-t,N-m)>=Fraction(K,N) if N-m else n==0
    if density_sufficient:
        assert after>=before
    return {
        "before":before,
        "after":after,
        "difference":after-before,
        "target_density_before":Fraction(K,N) if N else Fraction(),
        "target_density_after":Fraction(K-t,N-m) if N-m else Fraction(),
        "density_nondecrease_is_sufficient":density_sufficient,
        "density_decreased_but_hit_improved":(
            not density_sufficient and after>before
        )
    }
