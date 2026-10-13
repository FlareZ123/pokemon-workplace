"""Multi-objective Mew Wally access / late Special Red Card acquisition.

Compare published Mew W1L0R2, experimental W1L1R1, W2L1R0.
The two endpoints are incomparable tactical proxies, not win percentages.
"""
from __future__ import annotations
import json
import sys
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from results.tests.mew_wally_slot_frontier.heavy_ball_joint_policy import (
    EXPECTED,exact,pool
)

# Mew, Gene, VMAX, Wally, DCE, VIP, Quick, Ultra, Lele, Heavy, other.
ORIGINAL=(4,4,3,1,4,3,4,4,0,1,32)
SOURCE_EARLY={
 "baseline":Fraction(167155400140607,11575496365633200),
 "heavy_genesect":Fraction(5732582827171,34726489096899600)
}
RED_EXPECTED={
 (11,2,6):Fraction(4750883403,12540064576),
 (11,2,10):Fraction(6033468277,12540064576),
 (12,1,6):Fraction(105712195,502018968),
 (12,1,10):Fraction(139440431,502018968),
 (12,0,6):Fraction(0),
 (12,0,10):Fraction(0)
}

def natural_red_access(n,basic,red,hand,draws):
    """P(>=1 Red in opener + draws | >=1 Basic in opener).

    Prizes are set between opener and subsequent draws. Sampling the next
    cards uniformly from the non-Prized deck gives the same marginal formula.
    This does not assert Red is playable when acquired.
    """
    valid=Fraction(comb(n,hand)-comb(n-basic,hand),comb(n,hand))
    no_red_valid=(
        Fraction(comb(n-red,hand)-comb(n-red-basic,hand),comb(n,hand))
        *Fraction(comb(n-red-hand,draws),comb(n-hand,draws))
    )
    return 1-no_red_valid/valid

def physical_oracle(n,basic,red,hand,prizes,draws):
    cards=(0,)*basic+(1,)*red+(2,)*(n-basic-red)
    valid=0;hit=0
    for starter in combinations(range(n),hand):
        opener=set(starter)
        others=set(range(n))-opener
        for prized in combinations(sorted(others),prizes):
            remains=others-set(prized)
            for chosen in combinations(sorted(remains),draws):
                observed=opener|set(chosen)
                if not any(cards[i]==0 for i in opener):continue
                valid+=1
                if any(cards[i]==1 for i in observed):hit+=1
    return Fraction(hit,valid)

def verify_red_card():
    path=ROOT/"resources/cards/en/me4.json"
    source=json.loads(path.read_text(encoding="utf-8"))
    red=next(x for x in source if x["id"]=="me4-82")
    rules=" ".join(red["rules"])
    assert "3 or fewer Prize cards remaining" in rules
    assert "bottom of their deck" in rules
    assert "draw 3 cards" in rules

def main():
    verify_red_card()
    toys=(
      (12,3,2,3,2,2),
      (12,5,1,3,2,2),
      (13,4,2,4,2,2)
    )
    for n,b,r,h,p,d in toys:
        a=natural_red_access(n,b,r,h,d)
        z=physical_oracle(n,b,r,h,p,d)
        assert a==z,(n,b,r,a,z)
        print(f"Independent physical Red/Basic oracle PASSED N={n}: {a}")

    source=exact(ORIGINAL,7,6)
    assert source==SOURCE_EARLY,(source,SOURCE_EARLY)
    for (basics,red,draws),expected in RED_EXPECTED.items():
        observed=natural_red_access(60,basics,red,7,draws)
        assert observed==expected,(basics,red,draws,observed,expected)
    options=(
      ("published W1L0R2",11,2,sum(source.values(),Fraction(0))),
      ("one Wally, one Lele, one Red",12,1,sum(EXPECTED[1],Fraction(0))),
      ("two Wally, one Lele, zero Red",12,0,sum(EXPECTED[2],Fraction(0)))
    )
    for label,basics,red,first_turn in options:
        d6=natural_red_access(60,basics,red,7,6)
        d10=natural_red_access(60,basics,red,7,10)
        print(
            f"{label}: restricted Wally attack={float(first_turn):.12%}; "
            f"Red observed D6={float(d6):.12%}; D10={float(d10):.12%}"
        )
    assert options[2][3]>options[1][3]>options[0][3]
    print("CAUTION: early access and late Red acquisition have different payoffs.")

if __name__=="__main__":main()
