"""Independent physical openings, disjoint prizes, natural draws and followups."""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from multi_action_information_envelope import action_information_envelope
from physical_supporter_menu import (
    opening_hand_distribution, k_prior, physical_supporter_information,
)
from supporter_opponent_tradeoff_frontier import opponent_next_draw_readiness


def brute_hit(pool:tuple[int,...],target:set[int], draw:int) -> Fraction:
    choices=list(combinations(pool,min(draw,len(pool))))
    return Fraction(sum(bool(target.intersection(c)) for c in choices),len(choices))


def brute_joint(counts:tuple[int,...],opening_size:int,prize_count:int):
    identities=tuple(range(sum(counts)))
    classes={}
    pos=0
    for cat,n in enumerate(counts):
        for card in identities[pos:pos+n]:classes[card]=cat
        pos+=n
    open_valid=[o for o in combinations(identities,opening_size)
                if any(classes[c]==0 for c in o)]
    assert open_valid
    denominator=len(open_valid)*comb(len(identities)-opening_size,prize_count)*(
        len(identities)-opening_size-prize_count)
    counted=defaultdict(int)
    for opened in open_valid:
        active=next(c for c in opened if classes[c]==0)
        residual=tuple(c for c in identities if c not in opened)
        for prizes in combinations(residual,prize_count):
            for drawn in residual:
                if drawn in prizes: continue
                hand=tuple(c for c in opened if c!=active)+(drawn,)
                ct=tuple(sum(classes[c]==j for c in hand) for j in range(6))
                deck=tuple(c for c in residual if c not in prizes and c!=drawn)
                k=sum(classes[c]==4 for c in deck)
                counted[(ct,k)]+=1
    return {a:Fraction(v,denominator) for a,v in counted.items()},classes


def test_physical_priors():
    cases=((2,1,1,1,2,3),(3,2,1,1,2,2),(2,1,2,1,1,2),
           (1,1,1,1,1,3),(2,1,1,1,2,4))
    tested=0
    for counts in cases:
        for opening,prizes in ((3,1),(3,2)):
            accepted,hands=opening_hand_distribution(counts,opening_size=opening,prize_count=prizes)
            observed,cl=brute_joint(counts,opening,prizes)
            assert sum(observed.values(),Fraction())==1
            deck_size=sum(counts)-opening-prizes-1
            analytic={}
            for h,p in hands.items():
                for k,prior in k_prior(deck_size=deck_size,
                                     prize_count=prizes,unknown_outs=counts[4]-h[4]):
                    analytic[(h,k)]=p*prior
            assert analytic==observed,(counts,opening,prizes,
                                      [(k,analytic.get(k),observed.get(k)) for k in analytic if analytic.get(k)!=observed.get(k)][:5])
            tested+=1
    return tested


def independent_physical_envelope(counts, opening, prizes, opp,weight):
    """Iterate physical cards, then compute actual followup draw subsets."""
    identities=tuple(range(sum(counts)))
    classes={}
    i=0
    for idx,n in enumerate(counts):
        for card in range(i,i+n):classes[card]=idx
        i+=n
    valid=[a for a in combinations(identities,opening)
           if any(classes[c]==0 for c in a)]
    source=defaultdict(lambda:defaultdict(lambda:Fraction()))
    n_cases=len(valid)*comb(sum(counts)-opening,prizes)*(
        sum(counts)-opening-prizes)
    mass=Fraction(1,n_cases)
    for op in valid:
        active=next(c for c in op if classes[c]==0)
        remainder=tuple(c for c in identities if c not in op)
        for p in combinations(remainder,prizes):
            for draw in remainder:
                if draw in p:continue
                hand=tuple(c for c in op if c!=active)+(draw,)
                hc=tuple(sum(classes[x]==i for x in hand) for i in range(6))
                deck=tuple(c for c in remainder if c not in p and c!=draw)
                k=sum(classes[c]==4 for c in deck)
                outs={c for c in identities if classes[c]==4}
                if (hc,k) not in source:
                    source[(hc,k)]["_mass"]=Fraction()
                    opts={"Pass":Fraction(int(bool(outs.intersection(hand))))-weight*opp[3]}
                    for cat,name,qi in ((1,"Iono",0),(2,"N",1),(3,"Professor's Research",2)):
                        if hc[cat]==0: continue
                        supporter=next(c for c in hand if classes[c]==cat)
                        old_hand=tuple(c for c in hand if c!=supporter)
                        if name=="Iono":
                            if prizes<=len(deck):
                                hit=brute_hit(deck,outs,prizes)
                            elif outs.intersection(deck):
                                hit=Fraction(1)
                            else:
                                hit=brute_hit(old_hand,outs,prizes-len(deck))
                        elif name=="N":
                            hit=brute_hit(deck+old_hand,outs,prizes)
                        else:
                            hit=brute_hit(deck,outs,7)
                        opts[name]=hit-weight*opp[qi]
                    source[(hc,k)].update(opts)
                source[(hc,k)]["_mass"]+=mass
    grouped=defaultdict(list)
    for (hand,k),opts in source.items():
        w=opts["_mass"]
        grouped[hand].append((w,{a:p for a,p in opts.items() if a!="_mass"}))
    fixed=informed=Fraction()
    for hand,states in grouped.items():
        pmass=sum((w for w,_ in states),Fraction())
        result=action_information_envelope((w/pmass,a) for w,a in states)
        fixed+=pmass*result.best_fixed_value
        informed+=pmass*result.observed_value
    return fixed,informed


def test_physical_policy():
    opp=(Fraction(1,5),Fraction(1,2),Fraction(1),Fraction(1))
    checks=0
    for counts in ((2,1,1,1,2,3),(2,1,2,1,1,2),(3,2,1,1,2,2)):
        for prize in (1,2):
            for weight in (Fraction(0),Fraction(1,2),Fraction(2)):
                a=physical_supporter_information(counts,opening_size=3,
                    prize_count=prize,opponent_penalties=opp,weight=weight)
                fixed,informed=independent_physical_envelope(counts,3,prize,opp,weight)
                assert (a.fixed_policy_value,a.observed_policy_value)==(fixed,informed),(
                    counts,prize,weight,float(a.fixed_policy_value-fixed),float(a.observed_policy_value-informed))
                checks+=1
    return checks


def witness():
    q=opponent_next_draw_readiness(deck_size=46,prizes_hidden=6,
                                  unknown_outs=4,hand_size=5,hand_outs=1)
    opp=q.as_tuple()+(q.research,)
    defaults=(12,4,4,4,4,32)
    a=physical_supporter_information(defaults,opponent_penalties=opp,weight=Fraction(1,10))
    assert len(a.hand_distribution)==708
    assert round(float(a.accepted_opening),12)==0.809353307289
    assert round(float(a.any_supporter),12)==0.838438008980
    assert round(float(a.multiple_supporter),12)==0.477077065343
    assert round(float(a.target_held),12)==0.427388244289
    assert round(float(a.k1_information_gain*100),12)==0.006666181713
    assert a.observed_policy_value-a.fixed_policy_value==a.k1_information_gain
    assert sum((v for _,v in a.contribution_by_hand),Fraction())==a.k1_information_gain
    z=physical_supporter_information(defaults,opponent_penalties=opp,weight=Fraction(0))
    assert z.k1_information_gain==0
    for weight in (Fraction(1,4),Fraction(1,2),Fraction(1)):
        assert physical_supporter_information(defaults,opponent_penalties=opp,
            weight=weight).k1_information_gain==0
    b=physical_supporter_information(defaults,opponent_penalties=opp,weight=2)
    assert round(float(b.k1_information_gain*100),12)==0.000072562303
    print("Basic-valid opening",float(a.accepted_opening))
    print("P(any physically held Supporter | valid opening)",float(a.any_supporter))
    print("P(two-plus Supporter cards)",float(a.multiple_supporter))
    print("P(useful target held)",float(a.target_held))
    print("Distinct final hands",len(a.hand_distribution))
    print("lambda 0.1 exact K1 value",a.k1_information_gain,
          "in percentage points",float(a.k1_information_gain*100))
    print("lambda 2 exact K1 value",b.k1_information_gain,
          "in percentage points",float(b.k1_information_gain*100))


if __name__=="__main__":
    print("Independent physical joint-opening Prize deck-outs priors:",test_physical_priors())
    print("Independent physical policy payoff comparisons:",test_physical_policy())
    witness()
