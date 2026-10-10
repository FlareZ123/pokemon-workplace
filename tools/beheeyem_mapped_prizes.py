"""Exact K1 Prize-selection upper bound when every Prize face is known.

For Beheeyem B + Triple Acceleration Energy T packet recurrence, compare:
- blind r-Prize award (uniform subset of six face-down Prizes);
- perfect mapping (Town Map effect already active): optimally choose exactly
  r physical Prize positions with known face-up identities to maximize next
  T3 packet access, before d T3 blind deck draws.

Town Map (bw7-136) exposes Prize faces. The model treats that information as
free, ignoring obtaining, paying for and playing Town Map itself; it is
therefore an upper-bound component rather than an actionable decklist claim.
"""
from __future__ import annotations

from functools import lru_cache
from fractions import Fraction
from math import comb

from beheeyem_physical_tutor import MODES, choose
from beheeyem_prize_packet import exact_prize_take, second_draw_success


@lru_cache(maxsize=None)
def exact_mapped_prizes(
    B: int, T: int, draws: int, tutor: str, prizes_awarded: int
) -> tuple:
    """Return first, blind, mapped, uplift, improved-K1 mass, count, witness."""
    if not (1 <= B <= 4 and 1 <= T <= 4 and 0 <= draws <= 5):
        raise ValueError("Packet copies 1..4, T3 blind draws 0..5")
    if not (0 <= prizes_awarded <= 2 and tutor in MODES):
        raise ValueError("Prizes taken 0..2, known tutor")

    target, payment = MODES[tutor]
    filler = 56-B-T
    denominator = comb(57,6)*comb(51,6)
    prize_denominator = comb(6,prizes_awarded)
    first = mapped = blind = improved_mass = Fraction()
    improved_states = 0
    best_witness = None

    for b in range(B+1):
        for t in range(T+1):
            for c in range(2):
                f = 6-b-t-c
                hand_ways = (
                    choose(B,b)*choose(T,t)*choose(1,c)*choose(filler,f)
                )
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
                                choose(1-c,pc)*choose(filler-f,pf)
                            )
                            if not prize_ways:
                                continue
                            if rescue and (
                                (missing_b and B-b-pb == 0) or
                                (missing_t and T-t-pt == 0)
                            ):
                                continue

                            weight = Fraction(
                                hand_ways*prize_ways,denominator
                            )
                            first += weight
                            if direct:
                                hand = (b-1,t-1,c,f)
                                deck = (
                                    B-b-pb+1,T-t-pt+1,1-c-pc,filler-f-pf+1
                                )
                            else:
                                hand = (max(b-1,0),max(t-1,0),0,f-payment)
                                deck = (
                                    B-b-pb+1-int(missing_b),
                                    T-t-pt+1-int(missing_t),
                                    0,filler-f-pf+1
                                )
                            prizes = (pb,pt,pc,pf)
                            blind_cond = Fraction()
                            optimal_cond = Fraction(-1)
                            optimal_selection = None

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
                                        chosen = (xb,xt,xc,xf)
                                        next_hand = tuple(
                                            x+y for x,y in zip(hand,chosen)
                                        )
                                        probability = second_draw_success(
                                            *next_hand,*deck,draws,tutor
                                        )
                                        blind_cond += Fraction(
                                            ways,prize_denominator
                                        )*probability
                                        if probability > optimal_cond:
                                            optimal_cond = probability
                                            optimal_selection = chosen

                            assert optimal_cond >= blind_cond
                            blind += weight*blind_cond
                            mapped += weight*optimal_cond
                            if optimal_cond > blind_cond:
                                improved_states += 1
                                improved_mass += weight
                                if (
                                    best_witness is None
                                    or optimal_cond-blind_cond > best_witness[0]
                                ):
                                    best_witness = (
                                        optimal_cond-blind_cond,
                                        (b,t,c,f),prizes,hand,deck,
                                        prizes_awarded,optimal_selection,
                                        optimal_cond,blind_cond
                                    )
    assert blind == exact_prize_take(
        B,T,draws,tutor,prizes_awarded
    )[3]
    return (
        first,blind,mapped,mapped-blind,
        improved_mass,improved_states,best_witness
    )
