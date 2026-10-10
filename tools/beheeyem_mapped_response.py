"""Town Map selection optimality and regret under an opposing N response.

Compare perfectly mapped Prize choices intended for an uninterrupted hand
with choices optimized knowing that opponent N will shuffle every remaining
hand card and Prize pickup into the full deck, then redraw by remaining
Prizes. Physical T2 packet and 47/48 deck setup is unchanged.

Per K1 state, evaluate all r-card Prize category subsets and both
counterfactual payoffs. The "surprise N regret" is the exact loss when
optimizing for no opponent reset but N occurs; among tied no-reset optimal
choices, allow the most N-favorable tie-break. Thus the computed regret is
a conservative measure of policy incompatibility.
"""
from __future__ import annotations

from functools import lru_cache
from fractions import Fraction
from math import comb

from beheeyem_physical_tutor import MODES, choose
from beheeyem_prize_packet import second_draw_success
from beheeyem_supporter_reset import exact_supporter_reset
from beheeyem_mapped_prizes import exact_mapped_prizes


@lru_cache(maxsize=None)
def exact_mapping_response(
    B: int, T: int, draws: int, tutor: str, prizes_awarded: int
) -> tuple:
    """Return first, N blind/mapped, no-reply mapped, surprise-N regret and witnesses.

    (first, blind_N, optimal_mapped_N, mapping_uplift_N, optimal_mapped_no_reply,
    N_success_with_no_reply_optimal_choice, regret,
    probability_mass_with_strict_conflict, conflict_state_count, witness).
    """
    if not (1 <= B <= 4 and 1 <= T <= 4 and 0 <= draws <= 5):
        raise ValueError("B/T 1..4 and T3 draws 0..5")
    if not (0 <= prizes_awarded <= 2 and tutor in MODES):
        raise ValueError("Prize awards 0..2 and known tutor")

    target, payment = MODES[tutor]
    F = 56-B-T
    hp_denominator = comb(57,6)*comb(51,6)
    prize_denominator = comb(6,prizes_awarded)
    first = blind_N = optimal_N = chosen_for_no_reply_N = Fraction()
    optimal_no_reply = conflict_mass = Fraction()
    conflict_count = 0
    witness = None

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
                            weight = Fraction(
                                hand_ways*prize_ways,hp_denominator
                            )
                            first += weight
                            if direct:
                                hand = (b-1,t-1,c,f)
                                deck = (
                                    B-b-pb+1,T-t-pt+1,1-c-pc,F-f-pf+1
                                )
                            else:
                                hand = (max(b-1,0),max(t-1,0),0,f-payment)
                                deck = (
                                    B-b-pb+1-int(missing_b),
                                    T-t-pt+1-int(missing_t),
                                    0,F-f-pf+1
                                )

                            prizes = (pb,pt,pc,pf)
                            candidate_payoffs = []
                            blind_conditional_N = Fraction()
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
                                        selected = (xb,xt,xc,xf)
                                        selected_hand = tuple(
                                            x+y for x,y in zip(hand,selected)
                                        )
                                        joined = tuple(
                                            x+y for x,y in zip(deck,selected_hand)
                                        )
                                        p_no_reply = second_draw_success(
                                            *selected_hand,*deck,draws,tutor
                                        )
                                        p_after_N = second_draw_success(
                                            0,0,0,0,*joined,
                                            6-prizes_awarded+draws,tutor
                                        )
                                        candidate_payoffs.append(
                                            (selected,p_no_reply,p_after_N)
                                        )
                                        blind_conditional_N += Fraction(
                                            ways,prize_denominator
                                        )*p_after_N

                            best_no_reply = max(
                                option[1] for option in candidate_payoffs
                            )
                            best_after_N = max(
                                option[2] for option in candidate_payoffs
                            )
                            best_N_given_no_reply_choice = max(
                                option[2] for option in candidate_payoffs
                                if option[1] == best_no_reply
                            )
                            regret = (
                                best_after_N-best_N_given_no_reply_choice
                            )

                            blind_N += weight*blind_conditional_N
                            optimal_N += weight*best_after_N
                            chosen_for_no_reply_N += weight*best_N_given_no_reply_choice
                            optimal_no_reply += weight*best_no_reply
                            if regret > 0:
                                conflict_count += 1
                                conflict_mass += weight
                                if witness is None or regret > witness[0]:
                                    witness = (
                                        regret,(b,t,c,f),prizes,hand,deck,
                                        prizes_awarded,
                                        [x for x in candidate_payoffs
                                         if x[1] == best_no_reply],
                                        [x for x in candidate_payoffs
                                         if x[2] == best_after_N],
                                        best_no_reply,best_after_N
                                    )

    assert blind_N == exact_supporter_reset(
        B,T,draws,tutor,prizes_awarded,"N"
    )[3]
    assert optimal_no_reply == exact_mapped_prizes(
        B,T,draws,tutor,prizes_awarded
    )[2]
    assert chosen_for_no_reply_N <= optimal_N
    return (
        first,blind_N,optimal_N,optimal_N-blind_N,
        optimal_no_reply,chosen_for_no_reply_N,
        optimal_N-chosen_for_no_reply_N,
        conflict_mass,conflict_count,witness
    )
