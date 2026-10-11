"""Exact optional, physically payable zero-output Quick Ball Prize inspection.

B/I/N/R/T/F/Q mutually exclusive card classes; Q is legal Quick Ball.
A search consumes one held Q and one held disposable F, sees the deck, and
selects zero Basic Pokemon before shuffling. This is a narrow tactical policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb

from hand_return_payment_frontier import hit_probability
from multi_action_information_envelope import action_information_envelope
from physical_supporter_menu import k_prior


@dataclass(frozen=True)
class PhysicalSearchResult:
    opening_valid_probability: Fraction
    initial_hand_compositions: int
    search_payable_probability: Fraction
    searched_probability: Fraction
    expected_gross_information_after_payment: Fraction
    expected_material_effect_if_searched: Fraction
    optimal_net_improvement: Fraction
    no_search_baseline: Fraction
    optional_search_value: Fraction
    free_information_premium: Fraction


def physical_hands_with_quick_ball(
    counts:tuple[int,...]=(12,4,4,4,4,28,4),
    *, opening_size:int=7, prize_count:int=6,
)->tuple[Fraction,dict[tuple[int,...],Fraction]]:
    """Exact opening composition conditional on one chosen Basic Active."""
    if (len(counts)!=7 or any(type(n) is not int or n<0 for n in counts)
        or type(opening_size) is not int or type(prize_count) is not int):
        raise ValueError('7 integer card classes required')
    total=sum(counts)
    if not 0<opening_size<total-prize_count or not counts[0]:
        raise ValueError('infeasible Basic opening/Prize configuration')
    den=comb(total,opening_size)
    accepted=Fraction(den-comb(total-counts[0],opening_size),den)
    hands={}
    for opened in product(*(range(min(c,opening_size)+1) for c in counts)):
        if not opened[0] or sum(opened)!=opening_size:continue
        p=Fraction(1,den)
        for n,c in zip(counts,opened):p*=comb(n,c)
        for j in range(len(counts)):
            rest=counts[j]-opened[j]
            if not rest:continue
            hand=list(opened)
            hand[0]-=1
            hand[j]+=1
            hand=tuple(hand)
            hands[hand]=hands.get(hand,Fraction())+p*Fraction(rest,total-opening_size)/accepted
    assert sum(hands.values(),Fraction())==1
    return accepted,hands


def action_rows(
    *,hand:tuple[int,...],deck_size:int,prizes:int,unknown_outs:int,
    source_paid:bool,opponent_penalties:tuple[Fraction,...],weight:Fraction,
):
    """Action menu and payload after an optional Q+F source payment."""
    b,i,n,r,t,f,q=hand
    if source_paid:
        assert q>=1 and f>=1
    hand_size=sum(hand)-(2 if source_paid else 0)
    names=('Iono','N',"Professor's Research",'Pass')
    available=tuple(name for idx,name in enumerate(names[:3]) if hand[idx+1]) + ('Pass',)
    rows=[]
    for k,p in k_prior(deck_size=deck_size,prize_count=prizes,unknown_outs=unknown_outs):
        own=(hit_probability(deck_size,k,prizes),
             hit_probability(deck_size+hand_size-1,k+t,prizes),
             hit_probability(deck_size,k,7),Fraction(int(t>0)))
        rows.append((p,{name:own[idx]-weight*opponent_penalties[idx]
                         for idx,name in enumerate(names) if name in available}))
    return tuple(rows)


def physical_quick_ball_option(
    *,counts:tuple[int,...]=(12,4,4,4,4,28,4),opening_size:int=7,
    prize_count:int=6,opponent_penalties:tuple[Fraction,...],weight:Fraction,
) -> PhysicalSearchResult:
    """Compare never-search K0 against optimal state-dependent use of Quick Ball.

    The decision whether to use Quick Ball is made from the observed hand
    *before* seeing K. If the physically held Q+F source is paid, then K1
    deck knowledge permits optimizing the subsequent available Supporter.
    Taking zero Basic output never changes deck/hand class composition.
    """
    weight=Fraction(weight)
    q=tuple(Fraction(x) for x in opponent_penalties)
    if weight<0 or len(q)!=4 or any(not 0<=x<=1 for x in q):
        raise ValueError('invalid opponent penalties or weight')
    accepted,hands=physical_hands_with_quick_ball(counts,opening_size=opening_size,
                                                  prize_count=prize_count)
    d=sum(counts)-opening_size-prize_count-1
    if d<1:raise ValueError('old deck must be nonempty')
    baseline=optional=free=paid_mass=search_mass=gross_info=material=Fraction()
    for hand,mass in hands.items():
        unknown=counts[4]-hand[4]
        before=action_information_envelope(action_rows(hand=hand,deck_size=d,prizes=prize_count,
            unknown_outs=unknown,source_paid=False,opponent_penalties=q,weight=weight))
        baseline+=mass*before.best_fixed_value
        free+=mass*before.information_value
        best=before.best_fixed_value
        if hand[5] and hand[6]:
            paid_mass+=mass
            after=action_information_envelope(action_rows(hand=hand,deck_size=d,prizes=prize_count,
                unknown_outs=unknown,source_paid=True,opponent_penalties=q,weight=weight))
            improvement=after.observed_value-before.best_fixed_value
            if improvement>0:
                best=after.observed_value
                search_mass+=mass
                gross_info+=mass*after.information_value
                material+=mass*(after.best_fixed_value-before.best_fixed_value)
                assert improvement==after.information_value+after.best_fixed_value-before.best_fixed_value
        optional+=mass*best
    assert optional>=baseline
    assert optional-baseline==material+gross_info
    return PhysicalSearchResult(accepted,len(hands),paid_mass,search_mass,
        gross_info,material,optional-baseline,baseline,optional,free)
