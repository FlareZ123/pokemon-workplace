"""Exact conditional K1 ranking of opposing N versus Iono.

Evaluate a fixed T2 hand and six-Prize composition after Beheeyem's first
Mysterious Noise attack. Opposing N reshuffles the surviving player hand
and r newly taken random Prizes into the full deck; Iono bottoms that hand
and redraws from the unchanged top 47-/48-card population. Both redraw
6-r cards and are followed by d natural/other blind T3 draws.

This is a K1 (player-knows-Prize-composition) state analysis. The OPPONENT
playing N or Iono does NOT know the player's hidden hand or Prize contents;
the state-level winner is therefore an omniscient comparator, not an
implementable opponent action policy without extra information.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import comb

from beheeyem_physical_tutor import MODES, choose
from beheeyem_prize_packet import second_draw_success


@lru_cache(maxsize=None)
def exact_state_reset(
    B: int, T: int, draws: int, tutor: str, prizes_awarded: int
) -> tuple:
    """Return first, N/Iono means and sign-partition masses with witnesses.

    Indexes: first, mean_N, mean_Iono, N_better_mass, Iono_better_mass,
    tie_mass, positive_N_uplift, positive_Iono_uplift, number_K1_states,
    maximum_N_witness, maximum_Iono_witness.
    """
    if not (1 <= B <= 4 and 1 <= T <= 4 and 0 <= draws <= 5):
        raise ValueError("B/T 1..4 and T3 draws 0..5")
    if not (0 <= prizes_awarded <= 2 and tutor in MODES):
        raise ValueError("Prize award r=0..2 and known tutor")

    target, payment = MODES[tutor]
    F = 56-B-T
    denominator = comb(57,6)*comb(51,6)
    prize_denominator = comb(6,prizes_awarded)
    mass = mean_n = mean_iono = n_better = iono_better = tied = Fraction()
    gain_n = gain_iono = Fraction()
    states = 0
    max_n_witness = max_iono_witness = None

    for b in range(B+1):
        for t in range(T+1):
            for c in range(2):
                f = 6-b-t-c
                hand_ways = choose(B,b)*choose(T,t)*choose(1,c)*choose(F,f)
                if not hand_ways:
                    continue
                direct = b > 0 and t > 0
                missing_b, missing_t = b == 0, t == 0
                rescue = not direct and c and f >= payment and (
                    (missing_b and t > 0 and target in ("pokemon","either"))
                    or (missing_t and b > 0 and target in ("energy","either"))
                )
                if not (direct or rescue):
                    continue
                for pb in range(B-b+1):
                    for pt in range(T-t+1):
                        for pc in range(2-c):
                            pf = 6-pb-pt-pc
                            prize_ways = (
                                choose(B-b,pb)*choose(T-t,pt)*
                                choose(1-c,pc)*choose(F-f,pf)
                            )
                            if not prize_ways:
                                continue
                            if rescue and (
                                (missing_b and B-b-pb == 0) or
                                (missing_t and T-t-pt == 0)
                            ):
                                continue
                            weight = Fraction(hand_ways*prize_ways,denominator)
                            if direct:
                                hand = (b-1,t-1,c,f)
                                deck = (B-b-pb+1,T-t-pt+1,1-c-pc,F-f-pf+1)
                            else:
                                hand = (max(b-1,0),max(t-1,0),0,f-payment)
                                deck = (
                                    B-b-pb+1-int(missing_b),
                                    T-t-pt+1-int(missing_t),
                                    0,F-f-pf+1
                                )
                            prizes = (pb,pt,pc,pf)
                            redraw = 6-prizes_awarded+draws
                            q_iono = second_draw_success(
                                0,0,0,0,*deck,redraw,tutor
                            )
                            q_n = Fraction()
                            for xb in range(min(pb,prizes_awarded)+1):
                                for xt in range(min(pt,prizes_awarded-xb)+1):
                                    for xc in range(min(pc,prizes_awarded-xb-xt)+1):
                                        xf = prizes_awarded-xb-xt-xc
                                        ways = (
                                            choose(pb,xb)*choose(pt,xt)*
                                            choose(pc,xc)*choose(pf,xf)
                                        )
                                        if not ways:
                                            continue
                                        joined = tuple(
                                            x+y+z for x,y,z in zip(
                                                deck,hand,(xb,xt,xc,xf)
                                            )
                                        )
                                        q_n += Fraction(
                                            ways,prize_denominator
                                        )*second_draw_success(
                                            0,0,0,0,*joined,redraw,tutor
                                        )

                            mass += weight
                            mean_n += weight*q_n
                            mean_iono += weight*q_iono
                            states += 1
                            if q_n > q_iono:
                                n_better += weight
                                gain_n += weight*(q_n-q_iono)
                                if (
                                    max_n_witness is None
                                    or q_n-q_iono > max_n_witness[0]
                                ):
                                    max_n_witness = (
                                        q_n-q_iono,(b,t,c,f),prizes,
                                        hand,deck,q_n,q_iono
                                    )
                            elif q_iono > q_n:
                                iono_better += weight
                                gain_iono += weight*(q_iono-q_n)
                                if (
                                    max_iono_witness is None
                                    or q_iono-q_n > max_iono_witness[0]
                                ):
                                    max_iono_witness = (
                                        q_iono-q_n,(b,t,c,f),prizes,
                                        hand,deck,q_n,q_iono
                                    )
                            else:
                                tied += weight
    assert mass == n_better+iono_better+tied
    assert mean_n-mean_iono == gain_n-gain_iono
    return (
        mass,mean_n,mean_iono,n_better,iono_better,tied,
        gain_n,gain_iono,states,max_n_witness,max_iono_witness
    )
