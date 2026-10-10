"""Exact opposing Iono response after a Prize-awarded Beheeyem attack.

T2 first packet is from direct hand access or a physically held paid tutor;
the Mysterious Noise attacker and attached TAE and underlying Elgyem then
shuffle into the deck. The first attack independently awards r=0,1,2 Prizes.

Opponent subsequently plays Iono. All surviving player hand cards, including
new Prize cards, are shuffled and placed at the BOTTOM of the player's deck.
Assuming at least one player returned cards, Iono draws exactly 6-r cards.
A d-card T3 blind draw is then added, sampled from the already randomized
TOP 47/48 cards. Returned hand cards at the bottom remain searchable by a
newly drawn tutor but are never reached by these short-horizon blind draws.

This is exogenous legal Supporter disruption, with no opponent draw
effect, Attack KO chances or tactical response probabilities modeled.
"""
from __future__ import annotations

from functools import lru_cache
from fractions import Fraction
from math import comb

from beheeyem_physical_tutor import MODES, choose
from beheeyem_prize_packet import second_draw_success


@lru_cache(maxsize=None)
def exact_iono_after_prizes(
    B: int, T: int, T3_draws: int, tutor: str, prizes_awarded: int
) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    """Return first-packet, direct-both, T2-rescued-both, combined-both rates."""
    if not (1 <= B <= 4 and 1 <= T <= 4):
        raise ValueError("B and T must be 1..4")
    if not (0 <= T3_draws <= 5 and 0 <= prizes_awarded <= 2):
        raise ValueError("Study scope: T3 blind 0..5, Prize awards 0..2")
    if tutor not in MODES:
        raise ValueError("Unknown tutor")

    target, payment = MODES[tutor]
    F = 56-B-T
    first = direct_iono = rescue_iono = Fraction(0)
    denom = comb(57,6)*comb(51,6)
    # Bottomed hand cards are inaccessible to top-deck draw; the random
    # original deck contains every recycled packet class required by tutor.
    effective_top_draws = 6-prizes_awarded+T3_draws

    for b in range(B+1):
        for t in range(T+1):
            for c in range(2):
                f = 6-b-t-c
                hand_ways = choose(B,b)*choose(T,t)*choose(1,c)*choose(F,f)
                if not hand_ways:
                    continue
                direct = b > 0 and t > 0
                missing_b, missing_t = b == 0, t == 0
                rescue = (
                    not direct and c and f >= payment and (
                        (missing_b and t > 0 and target in ("pokemon","either"))
                        or (missing_t and b > 0 and target in ("energy","either"))
                    )
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
                            state_weight = Fraction(hand_ways*prize_ways,denom)
                            first += state_weight
                            if direct:
                                deck = (
                                    B-b-pb+1,T-t-pt+1,
                                    1-c-pc,F-f-pf+1
                                )
                                assert sum(deck) == 48
                            else:
                                deck = (
                                    B-b-pb+1-int(missing_b),
                                    T-t-pt+1-int(missing_t),
                                    0,F-f-pf+1
                                )
                                assert sum(deck) == 47

                            # After the hand is bottomed by Iono, all
                            # usable B/T/tutor/payment cards on T3 must
                            # arrive through this short top-deck draw.
                            probability = second_draw_success(
                                0,0,0,0,*deck,effective_top_draws,tutor
                            )
                            if direct:
                                direct_iono += state_weight*probability
                            else:
                                rescue_iono += state_weight*probability

    return (
        first,direct_iono,rescue_iono,direct_iono+rescue_iono
    )
