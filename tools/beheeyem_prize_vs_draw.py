"""Exact K1 comparison: one random Prize award versus one extra blind T3 draw.

Both scenarios preserve the same fixed physical T2 hand and known six-Prize
multiset. They share the same first packet and T3 d-draw budget. One option
reveals and adds an additional face-down Prize card; the other draws an extra
card from the already shuffled 48-/47-card T3 deck.

The comparison is a counterfactual resource-value diagnostic, not a legal
choice between taking Prizes and drawing from the deck.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import comb

from beheeyem_physical_tutor import MODES, choose
from beheeyem_prize_packet import second_draw_success


@lru_cache(maxsize=None)
def compare_known_prizes(
    B: int, T: int, draws: int, tutor: str
) -> tuple:
    """Return K1 probability masses, positive/negative option value and witnesses.

    Tuple: (first, one_prize, extra_draw, prize_better_mass,
    deck_better_mass, tie_mass, positive_prize_advantage,
    positive_deck_advantage, reachable_state_count,
    prize_favoured_state_count, best_prize_witness, best_deck_witness).

    Masses are unconditional in the initial 57-card residual shuffle.
    """
    if not (1 <= B <= 4 and 1 <= T <= 4 and 0 <= draws <= 46):
        raise ValueError("B/T 1..4 and T3 base draws 0..46")
    if tutor not in MODES:
        raise ValueError("Unknown tutor")

    target, payment = MODES[tutor]
    F = 56 - B - T
    hp_space = comb(57,6) * comb(51,6)
    first = better = worse = tie = prize = extra = pos = neg = Fraction()
    states = prize_favoured_states = 0
    best_prize = best_deck = None

    for b in range(B+1):
        for t in range(T+1):
            for c in range(2):
                f = 6-b-t-c
                wh = (choose(B,b)*choose(T,t)*choose(1,c)*choose(F,f))
                if not wh:
                    continue
                direct = b > 0 and t > 0
                missing_b, missing_t = b == 0, t == 0
                rescue = not direct and c and f >= payment and (
                    (missing_b and t > 0 and target in ("pokemon","either")) or
                    (missing_t and b > 0 and target in ("energy","either"))
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
                            weight = Fraction(wh*wp,hp_space)
                            if direct:
                                hand = (b-1,t-1,c,f)
                                deck = (B-b-pb+1,T-t-pt+1,1-c-pc,F-f-pf+1)
                                assert sum(deck) == 48
                            else:
                                hand = (max(b-1,0),max(t-1,0),0,f-payment)
                                deck = (
                                    B-b-pb+1-int(missing_b),
                                    T-t-pt+1-int(missing_t),
                                    0,F-f-pf+1
                                )
                                assert sum(deck) == 47

                            prizes = (pb,pt,pc,pf)
                            prize_prob = Fraction()
                            for i, available in enumerate(prizes):
                                if available == 0:
                                    continue
                                updated = list(hand)
                                updated[i] += 1
                                prize_prob += Fraction(available,6)*second_draw_success(
                                    *updated,*deck,draws,tutor)

                            extra_prob = second_draw_success(
                                *hand,*deck,draws+1,tutor)
                            first += weight
                            prize += weight*prize_prob
                            extra += weight*extra_prob
                            states += 1
                            if prize_prob > extra_prob:
                                better += weight
                                pos += weight*(prize_prob-extra_prob)
                                prize_favoured_states += 1
                                if best_prize is None or prize_prob-extra_prob > best_prize[0]:
                                    best_prize = (
                                        prize_prob-extra_prob,
                                        (b,t,c,f),prizes,hand,deck,prize_prob,extra_prob
                                    )
                            elif prize_prob < extra_prob:
                                worse += weight
                                neg += weight*(extra_prob-prize_prob)
                                if best_deck is None or extra_prob-prize_prob > best_deck[0]:
                                    best_deck = (
                                        extra_prob-prize_prob,
                                        (b,t,c,f),prizes,hand,deck,prize_prob,extra_prob
                                    )
                            else:
                                tie += weight
    assert first == better+worse+tie
    assert prize-extra == pos-neg
    return (
        first, prize, extra, better, worse, tie, pos, neg,
        states, prize_favoured_states, best_prize, best_deck,
    )
