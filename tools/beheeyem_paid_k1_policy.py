"""Two-window physically paid Ultra Ball K1 action before Beheeyem Item lock.

Opponent: B12 / Ultra Ball4 / Ace4 / Judge4 / own-X4 / filler32.
After a Basic-valid opening7 and two prelock draws, optionally play one
Ultra Ball, discarding the Item and exactly two disposable fillers. Search
the whole deck but choose zero Pokémon (legal constrained target search),
then shuffle. This grants K1 knowledge of remaining Prized own-X copies.

Following Beheeyem's Mysterious Noise, one additional opponent draw
arrives. Item lock now prevents a previously unplayed Ultra Ball from
generating K1. Opponent chooses pass/Judge/Ace after observing its hand,
its actual K1 status and optional public first-Beheeyem-tutor route.

The early action is optimized under a declared scalar cost tau, distinct
from the physical three-card cost that alters the subsequent reset-deck
size. This isolates strategically-priced information and deck thinning.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import comb

from beheeyem_physical_tutor import choose,exact_physical_tutor
from beheeyem_prize_packet import exact_prize_take
from beheeyem_supporter_reset import exact_supporter_reset
from beheeyem_prelock_k1_search import search_window_probabilities


@lru_cache(maxsize=None)
def initial_prelock_masses(k_pre: int=2):
    """Return exact {(a,j,x,payable): mass} after Basic-valid opener."""
    h=7+k_pre
    B,A,J,X,U,F=12,4,4,4,4,32
    valid7=comb(60,7)-comb(48,7)
    den=comb(60,h)*comb(h,7)*valid7
    masses={}
    total=Fraction()
    for b in range(min(B,h)+1):
        valid_in_observed=comb(h,7)-choose(h-b,7)
        if not valid_in_observed:
            continue
        for a in range(min(A,h-b)+1):
            for j in range(min(J,h-b-a)+1):
                for x in range(min(X,h-b-a-j)+1):
                    for u in range(min(U,h-b-a-j-x)+1):
                        f=h-b-a-j-x-u
                        ways=(choose(B,b)*choose(A,a)*choose(J,j)*
                              choose(X,x)*choose(U,u)*choose(F,f))
                        if not ways:
                            continue
                        p=Fraction(
                            ways*valid_in_observed*comb(60,7),den
                        )
                        key=(a,j,x,bool(u>=1 and f>=2))
                        masses[key]=masses.get(key,Fraction())+p
                        total+=p
    assert total==1
    assert sum(p for (a,j,x,ok),p in masses.items() if ok)==(
        search_window_probabilities(k_pre)["paid_search_feasible"]
    )
    return masses


@lru_cache(maxsize=None)
def exact_early_search_policy(
    B: int=4,T: int=4,d: int=1,tutor: str="computer_search",
    r: int=1,opponent_prizes_left: int=6,
    lambda_weight: Fraction=Fraction(10),
    tau: Fraction=Fraction(),
    k_pre: int=2,k_reply: int=1,
    route_observed: bool=True
) -> dict[str,Fraction]:
    """Expected optimal utility for early U search vs no prelock search.

    Here q=6 (no own Prizes taken), k_pre=2 by default. Earlier search
    decision is based on observed prelock own A/J/X and U/F availability,
    before seeing the next reply draw or Beheeyem's first tutor-use route.
    """
    if not (opponent_prizes_left==6 and 0<=k_pre<=5 and
            0<=k_reply<=5 and lambda_weight>=0 and tau>=0):
        raise ValueError("Only q=6, nonnegative costs, limited windows modeled")
    if not 0<=r<=2:
        raise ValueError("Beheeyem first attack may award 0..2 Prizes")
    intact=exact_prize_take(B,T,d,tutor,r)
    judge=exact_supporter_reset(B,T,d,tutor,r,"Judge")
    ace_legal=opponent_prizes_left>6-r
    responses={"pass":intact,"judge":judge}
    if ace_legal:
        responses["ace"]=exact_supporter_reset(
            B,T,d,tutor,r,"Ace Trainer"
        )
    first=intact[0]
    direct_first=exact_physical_tutor(B,T,d,tutor)[0]
    branch_weights=((1,direct_first/first),
                    (2,(first-direct_first)/first))

    def packet_risk(action,route):
        packet=responses[action]
        return (packet[3]/first if not route_observed
                else packet[route]/
                (direct_first if route==1 else first-direct_first))

    @lru_cache(maxsize=None)
    def terminal(a,j,x,spent,knows_prizes):
        """Best expected own-X-minus-packet utility after reply draw.

        If K1, the decision is allowed to depend on z; if K0 it must
        optimize after integrating its Prize distribution.
        """
        source=("pass",)+(("judge",) if j else ())+(
            ("ace",) if a and ace_legal else ()
        )
        N=53-(3 if spent else 0)  # 6 own Prizes, discarded U+2 F.
        h=7+k_pre+k_reply
        unseen=60-h

        def prize_probs():
            for z in range(5):
                count=(choose(4-x,z)*
                       choose(unseen-(4-x),6-z))
                if count:
                    yield z,Fraction(count,comb(unseen,6))

        possible=tuple(prize_probs())
        assert sum(w for z,w in possible)==1
        total=Fraction()
        for route,route_weight in branch_weights:
            if not route_weight:
                continue
            def own(action,z):
                if action=="pass":
                    return Fraction(int(x>0))
                quota=6 if action=="ace" else 4
                return 1-Fraction(
                    choose(N-(4-z),quota),comb(N,quota)
                )

            if knows_prizes:
                value=sum(
                    w*max(own(action,z)-
                          lambda_weight*packet_risk(action,route)
                          for action in source)
                    for z,w in possible
                )
            else:
                value=max(
                    sum(w*own(action,z) for z,w in possible)-
                    lambda_weight*packet_risk(action,route)
                    for action in source
                )
            total+=route_weight*value
        return total

    @lru_cache(maxsize=None)
    def continuation(a,j,x,spent,knows):
        # The physically shuffled search whiff does not alter the set of
        # future deck cards. After prelock 9 observed cards, the next k
        # reply draws are uniform among the remaining 51 physical cards,
        # because the six original Prizes are exchangeable.
        total=Fraction()
        available=51
        base_others=available-((4-a)+(4-j)+(4-x))
        for da in range(min(4-a,k_reply)+1):
            for dj in range(min(4-j,k_reply-da)+1):
                for dx in range(min(4-x,k_reply-da-dj)+1):
                    do=k_reply-da-dj-dx
                    ways=(choose(4-a,da)*choose(4-j,dj)*
                          choose(4-x,dx)*choose(base_others,do))
                    if not ways:
                        continue
                    total+=Fraction(ways,comb(available,k_reply))*terminal(
                        a+da,j+dj,x+dx,spent,knows
                    )
        return total

    base=optimal=forced=thin_only=Fraction()
    chosen_search=eligible_mass=Fraction()
    pure_k1_gain=Fraction()
    for (a,j,x,eligible),mass in initial_prelock_masses(k_pre).items():
        no=continuation(a,j,x,False,False)
        base+=mass*no
        if not eligible:
            optimal+=mass*no
            forced+=mass*no
            thin_only+=mass*no
            continue
        eligible_mass+=mass
        paid_blind=continuation(a,j,x,True,False)
        paid_k1=continuation(a,j,x,True,True)
        assert paid_k1>=paid_blind>=no
        pure_k1_gain+=mass*(paid_k1-paid_blind)
        thin_only+=mass*paid_blind
        forced+=mass*(paid_k1-tau)
        if paid_k1-tau>no:
            optimal+=mass*(paid_k1-tau)
            chosen_search+=mass
        else:
            optimal+=mass*no

    assert optimal>=base
    assert chosen_search<=eligible_mass
    return {
        "eligible_prelock_search":eligible_mass,
        "baseline_no_search_utility":base,
        "forced_paid_search_utility":forced,
        "optimal_with_optional_search_utility":optimal,
        "early_search_chosen_mass":chosen_search,
        "gain_over_no_search":optimal-base,
        "paid_thinning_alone_gain_if_all_payable_played":thin_only-base,
        "paid_K1_information_gain_if_all_payable_played":pure_k1_gain
    }
