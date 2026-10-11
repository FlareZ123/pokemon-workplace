"""Exact draw probability of both disjoint packet pieces after discards.

Needed classes B and T have positive physical counts in an N-card draw
population. The chance of at least one of each in n unordered draws is
P=1-C(N-B,n)/C(N,n)-C(N-T,n)/C(N,n)+C(N-B-T,n)/C(N,n).

Remove m cards before drawing, including b pieces of B and t pieces of
T. The rest must be neutral filler. This isolates the packet acquisition
geometry, separate from tutor-rescue, Prize and Supporter constraints.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import comb


def _c(n: int,k: int) -> int:
    return comb(n,k) if 0<=k<=n else 0


@lru_cache(maxsize=None)
def joint_packet_hit(N: int,B: int,T: int,n: int) -> Fraction:
    if not (0<=B and 0<=T and B+T<=N and 0<=n<=N):
        raise ValueError("Invalid disjoint B/T population or draw quota")
    denominator=comb(N,n)
    return (1-Fraction(_c(N-B,n),denominator)
            -Fraction(_c(N-T,n),denominator)
            +Fraction(_c(N-B-T,n),denominator))


@lru_cache(maxsize=None)
def packet_discard_change(
    N: int,B: int,T: int,n: int,
    m: int,discard_B: int,discard_T: int
) -> dict[str,Fraction]:
    neutral=N-B-T
    neutral_discard=m-discard_B-discard_T
    if not (0<=discard_B<=B and 0<=discard_T<=T and
            0<=neutral_discard<=neutral and 0<=n<=N-m):
        raise ValueError("Invalid packet target and filler discards")
    original=joint_packet_hit(N,B,T,n)
    changed=joint_packet_hit(
        N-m,B-discard_B,T-discard_T,n
    )
    if discard_B==discard_T==0:
        assert changed>=original
    return {
        "before":original,
        "after":changed,
        "change":changed-original,
        "remaining_B":B-discard_B,
        "remaining_T":T-discard_T
    }
