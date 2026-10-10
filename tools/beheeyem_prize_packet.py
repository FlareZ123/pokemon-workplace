"""Exact prize-take extension for physical Beheeyem packet recurrence.

T2 starts with an established three-Basic board and six cards sampled from
57 remaining; six Prizes are then selected from unseen cards. After a first
Mysterious Noise attack, either zero, one or two face-down Prize cards enter
hand, before a reshuffled deck supplies d blind T3 draws. One optional
physical tutor can search one missing packet class if its payment is feasible.

The Prize reward count is EXOGENOUS. This script does not predict a KO.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import comb

from beheeyem_physical_tutor import MODES, choose


@lru_cache(maxsize=None)
def second_draw_success(hb: int, ht: int, hc: int, hf: int,
                        db: int, dt: int, dc: int, df: int,
                        draws: int, tutor: str) -> Fraction:
    """Packet completion in hand after d draws and at most one paid tutor."""
    target, payment = MODES[tutor]
    N = db + dt + dc + df
    if not 0 <= draws <= N:
        raise ValueError("Invalid draw budget")
    denom = comb(N, draws)
    if hb and ht:
        return Fraction(1)
    favourable = 0
    for b in range(min(db, draws) + 1):
        for t in range(min(dt, draws - b) + 1):
            for c in range(min(dc, draws - b - t) + 1):
                f = draws - b - t - c
                ways = choose(db, b) * choose(dt, t) * choose(dc, c) * choose(df, f)
                if not ways:
                    continue
                has_b, has_t = hb + b > 0, ht + t > 0
                via_tutor = (hc + c > 0 and hf + f >= payment and (
                    (not has_b and has_t and target in ("pokemon", "either")) or
                    (has_b and not has_t and target in ("energy", "either"))))
                if (has_b and has_t) or via_tutor:
                    favourable += ways
    return Fraction(favourable, denom)


@lru_cache(maxsize=None)
def exact_prize_take(B: int, T: int, draws: int, tutor: str,
                     prizes_taken: int) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    """Return first, direct-both, T2-tutor-rescued-both, all-both rates."""
    if not (1 <= B <= 4 and 1 <= T <= 4):
        raise ValueError("B and T must be 1..4")
    if not (0 <= draws <= 47):
        raise ValueError("T3 draw budget must fit either branch")
    if tutor not in MODES:
        raise ValueError("Unknown tutor")
    if not 0 <= prizes_taken <= 2:
        raise ValueError("This study considers r=0,1,2 only")

    F = 56 - B - T
    target, payment = MODES[tutor]
    denom_hp = comb(57, 6) * comb(51, 6)
    denom_prize = comb(6, prizes_taken)
    first = direct_second = rescued_second = Fraction(0)

    for b in range(min(B, 6) + 1):
        for t in range(min(T, 6-b) + 1):
            for c in range(2):
                f = 6-b-t-c
                wh = choose(B,b)*choose(T,t)*choose(1,c)*choose(F,f)
                if not wh:
                    continue
                direct = b > 0 and t > 0
                missing_b = b == 0
                missing_t = t == 0
                rescue = False
                if not direct and c and f >= payment:
                    rescue = (
                        missing_b and t > 0 and target in ("pokemon", "either")
                    ) or (
                        missing_t and b > 0 and target in ("energy", "either")
                    )
                if not (direct or rescue):
                    continue
                for pb in range(B-b+1):
                    for pt in range(T-t+1):
                        for pc in range(2-c):
                            pf = 6-pb-pt-pc
                            wp = (choose(B-b,pb)*choose(T-t,pt)*
                                  choose(1-c,pc)*choose(F-f,pf))
                            if not wp:
                                continue
                            if rescue and (
                                (missing_b and B-b-pb == 0) or
                                (missing_t and T-t-pt == 0)
                            ):
                                continue
                            weight = Fraction(wh*wp, denom_hp)
                            first += weight
                            if direct:
                                hand = (b-1, t-1, c, f)
                                deck = (B-b-pb+1,T-t-pt+1,1-c-pc,F-f-pf+1)
                                assert sum(deck) == 48
                            else:
                                hand = (max(b-1,0),max(t-1,0),0,f-payment)
                                deck = (B-b-pb+1-int(missing_b),
                                        T-t-pt+1-int(missing_t),0,F-f-pf+1)
                                assert sum(deck) == 47
                            conditional = Fraction(0)
                            for xb in range(min(pb, prizes_taken)+1):
                                for xt in range(min(pt, prizes_taken-xb)+1):
                                    for xc in range(min(pc, prizes_taken-xb-xt)+1):
                                        xf = prizes_taken-xb-xt-xc
                                        ways = (choose(pb,xb)*choose(pt,xt)*
                                                choose(pc,xc)*choose(pf,xf))
                                        if not ways:
                                            continue
                                        next_hand = tuple(x+y for x,y in zip(
                                            hand,(xb,xt,xc,xf)))
                                        conditional += Fraction(ways,denom_prize)*second_draw_success(
                                            *next_hand,*deck,draws,tutor)
                            if direct:
                                direct_second += weight*conditional
                            else:
                                rescued_second += weight*conditional
    return first, direct_second, rescued_second, direct_second+rescued_second
