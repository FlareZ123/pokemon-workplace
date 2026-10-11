"""Independent physical Prize, Quick Ball discard and redraw-subset enumerator."""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from physical_quick_ball_search_option import physical_quick_ball_option
from multi_action_information_envelope import action_information_envelope
from supporter_opponent_tradeoff_frontier import opponent_next_draw_readiness


def brute_draw(pool:tuple[int,...],targets:set[int],n:int)->Fraction:
    options=list(combinations(pool,min(n,len(pool))))
    return Fraction(sum(bool(targets.intersection(choice)) for choice in options),len(options))


def exact_small_physical(counts:tuple[int,...],opening:int,prizes:int,
                         q:tuple[Fraction,...],weight:Fraction):
    """Enumerate distinct physical cards through initial, Prize and draw.

    For each fixed opening-hand category vector, take a fresh posterior over
    physically dealt unseen Prizes. Source Q and payment F are exact physical
    card IDs, and direct redraw effects enumerate subsets independently.
    """
    ids=tuple(range(sum(counts)))
    category={}
    offset=0
    for j,n in enumerate(counts):
        for card in range(offset,offset+n):category[card]=j
        offset+=n
    valid=tuple(h for h in combinations(ids,opening) if any(category[c]==0 for c in h))
    cardinality=len(valid)*comb(len(ids)-opening,prizes)*(len(ids)-opening-prizes)
    case_mass=Fraction(1,cardinality)
    samples=defaultdict(lambda:defaultdict(lambda:{'mass':Fraction()}))
    for open_cards in valid:
        active=next(c for c in open_cards if category[c]==0)
        unseen=tuple(c for c in ids if c not in open_cards)
        for prize in combinations(unseen,prizes):
            for natural in unseen:
                if natural in prize:continue
                hand=tuple(c for c in open_cards if c!=active)+(natural,)
                hc=tuple(sum(category[c]==j for c in hand) for j in range(7))
                deck=tuple(c for c in unseen if c not in prize and c!=natural)
                k=sum(category[c]==4 for c in deck)
                target={c for c in ids if category[c]==4}
                case=samples[hc][k]
                if case['mass']:
                    case['mass']+=case_mass
                    continue
                case['mass']=case_mass
                for paid in (False,True):
                    if paid and not (hc[5] and hc[6]):continue
                    after_hand=hand
                    if paid:
                        Q=next(c for c in after_hand if category[c]==6)
                        F=next(c for c in after_hand if category[c]==5)
                        after_hand=tuple(c for c in hand if c not in (Q,F))
                    payoffs={'Pass':Fraction(int(any(c in target for c in after_hand)))-weight*q[3]}
                    for j,name,qi in ((1,'Iono',0),(2,'N',1),(3,"Professor's Research",2)):
                        if not any(category[c]==j for c in after_hand): continue
                        source=next(c for c in after_hand if category[c]==j)
                        residual=tuple(c for c in after_hand if c!=source)
                        if name=='Iono':
                            if prizes<=len(deck):
                                hit=brute_draw(deck,target,prizes)
                            elif target.intersection(deck):
                                hit=Fraction(1)
                            else:
                                hit=brute_draw(residual,target,prizes-len(deck))
                        elif name=='N':
                            hit=brute_draw(deck+residual,target,prizes)
                        else:
                            hit=brute_draw(deck,target,7)
                        payoffs[name]=hit-weight*q[qi]
                    case[paid]=payoffs
    baseline=optional=free=paid_probability=used=material=gross=Fraction()
    for hand,hidden in samples.items():
        hand_mass=sum((case['mass'] for case in hidden.values()),Fraction())
        pre=action_information_envelope((case['mass']/hand_mass,case[False]) for case in hidden.values())
        baseline+=hand_mass*pre.best_fixed_value
        free+=hand_mass*pre.information_value
        best=pre.best_fixed_value
        if hand[5] and hand[6]:
            paid_probability+=hand_mass
            post=action_information_envelope((case['mass']/hand_mass,case[True]) for case in hidden.values())
            if post.observed_value>best:
                best=post.observed_value
                used+=hand_mass
                material+=hand_mass*(post.best_fixed_value-pre.best_fixed_value)
                gross+=hand_mass*post.information_value
        optional+=hand_mass*best
    return baseline,optional,free,paid_probability,used,material,gross


def test_small():
    q=(Fraction(1,5),Fraction(1,2),Fraction(1),Fraction(1))
    checks=0
    for cards in ((2,1,1,1,1,2,1),(2,1,2,1,2,1,1),
                  (3,1,1,1,1,2,1),(2,1,1,1,2,2,1)):
        for p in (1,2):
            for w in (Fraction(0),Fraction(1,2),Fraction(2)):
                exact=physical_quick_ball_option(counts=cards,opening_size=3,
                    prize_count=p,opponent_penalties=q,weight=w)
                brute=exact_small_physical(cards,3,p,q,w)
                vals=(exact.no_search_baseline,exact.optional_search_value,
                    exact.free_information_premium,exact.search_payable_probability,
                    exact.searched_probability,exact.expected_material_effect_if_searched,
                    exact.expected_gross_information_after_payment)
                assert brute==vals,(cards,p,w,[(i,a,b) for i,(a,b) in enumerate(zip(vals,brute)) if a!=b])
                checks+=1
    return checks


def witness():
    z=opponent_next_draw_readiness(deck_size=46,prizes_hidden=6,
                                   unknown_outs=4,hand_size=5,hand_outs=1)
    q=z.as_tuple()+(z.research,)
    a=physical_quick_ball_option(opponent_penalties=q,weight=0)
    assert round(float(a.search_payable_probability),12)==0.423912352445
    assert round(float(a.searched_probability),12)==0.040155844060
    assert a.free_information_premium==0
    assert a.expected_gross_information_after_payment==0
    assert round(float(a.optimal_net_improvement*100),12)==0.049289939016
    b=physical_quick_ball_option(opponent_penalties=q,weight=Fraction(1,10))
    assert round(float(b.searched_probability),12)==0.107819190102
    assert round(float(b.optimal_net_improvement*100),12)==0.051818963349
    assert round(float(b.expected_material_effect_if_searched*100),12)==0.049289939016
    assert round(float(b.expected_gross_information_after_payment*100),12)==0.002529024333
    assert round(float(b.free_information_premium*100),12)==0.006666181713
    for t in (a,b):
        assert (t.optimal_net_improvement==t.expected_material_effect_if_searched+
                t.expected_gross_information_after_payment)
    c=physical_quick_ball_option(opponent_penalties=q,weight=Fraction(1,5))
    assert c.free_information_premium==0
    assert c.expected_gross_information_after_payment==0
    assert round(float(c.optimal_net_improvement*100),12)==0.082808767845
    print('Physical source payable',float(a.search_payable_probability),'Basic-valid hand fraction')
    print('lambda0 optimal source incidence',float(a.searched_probability),
          'improvement pp',float(a.optimal_net_improvement*100),
          'free K1 value',a.free_information_premium)
    print('lambda0.1 source incidence',float(b.searched_probability),
          'improvement pp',float(b.optimal_net_improvement*100))
    print('lambda0.1 material pp',float(b.expected_material_effect_if_searched*100),
          'postpayment K1 option pp',float(b.expected_gross_information_after_payment*100))
    print('lambda0.2 information-only value',float(c.free_information_premium),
          'source material improvement pp',float(c.optimal_net_improvement*100))


if __name__=='__main__':
    print('Independent physical Quick Ball + filler payment cases:',test_small())
    witness()
