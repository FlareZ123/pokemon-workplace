"""Exact positive-mass Item indispensability with one Artazon unprized.

Aichi Vileplume, first-turn-core planner, six Prizes: all 4 non-TM Tools,
one Artazon, and any *one* of 51 other permitted physical cards.

Open Oddish + ACE + second Artazon + both TM Evolution distributed over
the opening and first draw, plus three generic nonBasic filler cards.
Exactly three fillers pay Box; Artazon must be preserved to Bench Bunnelby
and one TM preserved for the endpoint. Item -> Tag Call produces G&H and
an additional TAG TEAM payment, making Item strictly necessary.

Counts all physical copies and demonstrates action outcomes for representative
class-profile allocations of fillers on every allowable six-Prize layout.
"""
from fractions import Fraction
from itertools import product
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from aichi_vileplume_secret_box import (
    BASE_DECK, SECRET_BOX_DECK, _raw_state, _state_succeeds,
)
from aichi_secret_box_output_dependencies import _state_succeeds_with_mask

OTHER_SUPPORTERS = {
    "Guzma", "Cassius", "Karen", "Plumeria", "Gladion",
    "Faba", "Lusamine", "Peonia", "Team Yell's Cheer",
}
OTHER_NONBASIC = {
    "Pidgeotto", "Pidgeot ex", "Gloom", "Vileplume",
    "Vileplume-GX", "Herdier", "Stoutland", "Grass Energy",
}
OTHER_SPECIAL = {"Capture Energy", "Memory Energy"}
CLASSES = (
    tuple(i for i,name in enumerate(BASE_DECK) if name in OTHER_SUPPORTERS),
    tuple(i for i,name in enumerate(BASE_DECK) if name in OTHER_SPECIAL),
    tuple(i for i,name in enumerate(BASE_DECK) if name in OTHER_NONBASIC),
)
GENERIC = set.union(*(set(x) for x in CLASSES))
assert tuple(map(len, CLASSES)) == (10,3,13)
assert len(GENERIC) == 26

def indices(name):
    return tuple(i for i, card in enumerate(BASE_DECK) if card == name)

TOOLS = indices("Stealthy Hood") + indices("Counter Gain")
ARTAZON = indices("Artazon")
TM = indices("Technical Machine: Evolution")
ODDISH = indices("Oddish")
ACE = indices("Grand Tree")
assert (len(TOOLS),len(ARTAZON),len(TM),len(ODDISH),len(ACE)) == (4,2,2,2,1)

def class_triplets(eligible):
    """Represent every group-valued allocation of two-to-three fillers."""
    result=[]
    for a,b,c in product(range(3),repeat=3):
        selected=[]
        available=set(eligible)
        for which in (a,b,c):
            found=next((i for i in CLASSES[which] if i in available),None)
            if found is None:
                break
            selected.append(found)
            available.remove(found)
        if len(selected)==3:
            result.append(tuple(selected))
    return tuple(dict.fromkeys(result))

def physical_state(prized, oddish, artazon_hand, tm_opening,
                   fillers, first_draw):
    opening=(oddish,ACE[0],artazon_hand,*tm_opening,*fillers)
    assert len(opening)==7
    selected=(*opening,*prized,first_draw)
    assert len(selected)==len(set(selected))==14
    order=list(selected)+sorted(set(range(60))-set(selected))
    assert len(order)==len(set(order))==60
    baseline=_raw_state(BASE_DECK,order)
    secret=_raw_state(SECRET_BOX_DECK,order)
    assert baseline is not None and secret is not None
    assert baseline[2]==secret[2]=="Oddish"
    assert not _state_succeeds(baseline)
    assert _state_succeeds_with_mask(secret,15)
    assert not _state_succeeds_with_mask(secret,14)
    assert _state_succeeds_with_mask(secret,1)

def main():
    counter=0
    physical_weight=0
    used_sixth=set()
    stats={}
    for priced_artazon in ARTAZON:
        held_artazon=next(i for i in ARTAZON if i!=priced_artazon)
        fixed=set(TOOLS)|{priced_artazon}
        assert len(fixed)==5
        excluded=fixed|{held_artazon,*TM,*ACE}
        candidate_sixth=sorted(set(range(60))-excluded)
        assert len(candidate_sixth)==51
        for sixth in candidate_sixth:
            used_sixth.add(BASE_DECK[sixth])
            prizes=fixed|{sixth}
            free=set(range(60))-prizes
            odds=tuple(i for i in ODDISH if i in free)
            filler_stock=GENERIC & free
            m=len(filler_stock)
            expected=len(odds)*(2*comb(m,3)+comb(m,2)*(m-2))
            physical_weight+=expected

            profiles=class_triplets(filler_stock)
            assert profiles
            # Two TM positions: TM1 opens, TM2 draws; or both TM open
            # and the third filler becomes the natural draw.
            for oddish in odds:
                for triple in profiles:
                    for opener_tm,draw_tm in ((TM[0],TM[1]),
                                              (TM[1],TM[0])):
                        physical_state(prizes,oddish,held_artazon,
                                       (opener_tm,),triple,draw_tm)
                        counter+=1
                    physical_state(prizes,oddish,held_artazon,TM,
                                   triple[:2],triple[2])
                    counter+=1
            stats[(priced_artazon,sixth)]=expected

    assert len(stats)==102
    assert physical_weight==2_444_000,physical_weight
    basic_accept=1-Fraction(comb(46,7),comb(60,7))
    exact=Fraction(
        physical_weight,comb(60,6)*comb(54,7)*47
    )/basic_accept
    assert exact==Fraction(5,734379410688)
    prior=Fraction(35905391051,11715529476053936332800)
    total=exact+prior
    assert total==Fraction(115670219051,11715529476053936332800)
    print("Physical Prize layouts:",len(stats))
    print("Sixth Prize card-name variety:",len(used_sixth))
    print("Validated source planner state profiles:",counter)
    print("Exact weighted opening/Prize/draw combinations:",physical_weight)
    print("One Artazon held exact Item-required lower bound:",
          exact,float(exact))
    print("Combined disjoint exact lower bound incl all-six prized:",
          total,float(total))
    print("One-unprized-Artazon Item-required family passed.")

if __name__=="__main__":
    main()
