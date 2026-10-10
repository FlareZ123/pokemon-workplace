"""Exact constructive two-key-Prize Item indispensability family.

Price exactly two of six alternative non-TM Tools/Artazon, one of two
TM: Evolution, and three of the 26 nonBasic generic filler identities.

Open Oddish Active, ACE Box, Bunnelby, surviving TM, and three of the four
unprized alternative Tools/Stadiums. The remaining alternative is the
natural first draw. All alternative searches are now either Prized or
already held; three such cards pay Box and one remains as later fodder.
Only Item -> Tag Call produces the second safe G&H payment card.

Every possible alternative Prize pair, TM Prize index, oddish/Bunnelby
copies, and first-draw alternative is tested against representative
deck-compression classes for the three extra generic Prizes.
"""
from fractions import Fraction
from itertools import combinations,product
from math import comb
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from aichi_vileplume_secret_box import (
    BASE_DECK,SECRET_BOX_DECK,_raw_state,_state_succeeds,
)
from aichi_secret_box_output_dependencies import _state_succeeds_with_mask
from one_artazon_item_family import (
    GENERIC,CLASSES,TOOLS,ARTAZON,TM,ODDISH,ACE,class_triplets,
)

BUN=tuple(i for i,name in enumerate(BASE_DECK) if name=="Bunnelby")
ALT=tuple((*TOOLS,*ARTAZON))
assert len(BUN)==2 and len(ALT)==6 and len(GENERIC)==26

def replay(prize,oddish,bunnelby,tm,alternatives,first_draw):
    opening=(oddish,ACE[0],bunnelby,tm,*alternatives)
    assert len(opening)==7
    all_selected=(*opening,*prize,first_draw)
    assert len(all_selected)==len(set(all_selected))==14
    order=list(all_selected)+sorted(set(range(60))-set(all_selected))
    assert len(order)==len(set(order))==60
    base=_raw_state(BASE_DECK,order)
    full=_raw_state(SECRET_BOX_DECK,order)
    assert base is not None and full is not None
    assert base[2]==full[2]=="Oddish"
    assert not _state_succeeds(base)
    assert _state_succeeds_with_mask(full,15)
    assert not _state_succeeds_with_mask(full,14)
    assert _state_succeeds_with_mask(full,1)

def main():
    cases=0
    physical_weight=0
    prize_patterns=0
    for priced_alts in combinations(ALT,2):
        remainder=tuple(i for i in ALT if i not in priced_alts)
        assert len(remainder)==4
        for priced_tm in TM:
            remaining_tm=next(i for i in TM if i!=priced_tm)
            allowed=set(GENERIC)
            generic_profiles=class_triplets(allowed)
            assert generic_profiles
            prize_patterns+=1
            for fillers in generic_profiles:
                prize=tuple((*priced_alts,priced_tm,*fillers))
                assert len(prize)==6
                for oddish,bunnelby,draw in product(ODDISH,BUN,remainder):
                    opening_alts=tuple(i for i in remainder if i!=draw)
                    replay(prize,oddish,bunnelby,remaining_tm,
                           opening_alts,draw)
                    cases+=1
            physical_weight+=comb(26,3)*len(ODDISH)*len(BUN)*len(remainder)

    assert prize_patterns==30
    assert physical_weight==1_248_000
    A=1-Fraction(comb(46,7),comb(60,7))
    p=Fraction(
        physical_weight,comb(60,6)*comb(54,7)*47
    )/A
    assert p==Fraction(5,1438159679264)
    print("Two-key-Prize paired alternatives:",prize_patterns)
    print("Physical source-planner regression outcomes:",cases)
    print("Exact physical counted events:",physical_weight)
    print("Exact accepted-opening Item-only family:",p,float(p))
    print("Two-key-Prize family passed.")

if __name__=="__main__":
    main()
