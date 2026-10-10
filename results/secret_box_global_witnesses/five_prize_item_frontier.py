"""Exact five-of-six Tool/Stadium-Prized Item-necessity frontier.

Two adversarial Prize families preserve exactly one non-TM Tool or
Artazon, and place the sixth Prize anywhere except that final remaining
tool/stadium. Across all physical weighted seven-card openers and first
draws WITHOUT Jirachi starting Active, test whether Box with all four
output categories can meet the Aichi core but Box without Item cannot.

The six-Prize complete-exhaustion stratum is deliberately excluded.
This probes the conjecture that at least one alternative search output
can replace Item's discard-payment-financing role in these near-tails.
"""
from fractions import Fraction
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from exact_six_prize_item_necessity import (
    GNH, TAG, TM, JET, ACE, BUN, FAN, JIR, BASIC,
    SUPPORT, TAG_OTHER, SPECIAL_OTHER, FILLER,
    ACTIVE_MULTIPLIER, composition, physical_combinations,
)
from aichi_vileplume_secret_box import HAND_INDEX, DECK_INDEX, _core_possible

TOOL, STADIUM = 13, 14
FULL = (4,4,2,2,1,2,1,1,10,10,1,3,13,4,2)
HAND = {
    GNH:"gnh", TAG:"tag_call", TM:"tm_evolution",
    JET:"jet_energy", ACE:"secret_box", BUN:"bunnelby",
    FAN:"fan_rotom", STADIUM:"artazon",
}
DECK = {
    GNH:"gnh", TAG:"tag_call", TM:"tm_evolution",
    JET:"jet_energy", ACE:"secret_box",
    BUN:"bunnelby", SUPPORT:"supporter_other",
    TAG_OTHER:"tag_team_other",
    SPECIAL_OTHER:"special_energy_other",
    TOOL:"tool_other", STADIUM:"artazon",
}

def starters(opening):
    if opening[JIR]:
        return ()
    n_fan, n_basic = opening[FAN],opening[BASIC]
    if n_fan+n_basic:
        n=n_fan+n_basic
        return tuple(
            (name,ACTIVE_MULTIPLIER*count//n)
            for name,count in (("fan",n_fan),("basic",n_basic)) if count
        )
    return (("bunnelby",ACTIVE_MULTIPLIER),) if opening[BUN] else ()

def mkstate(pool,opening,draw,active):
    hand=[0]*len(HAND_INDEX)
    deck=[0]*len(DECK_INDEX)
    for i,n in enumerate(opening):
        x=n+int(draw==i)
        if x:
            hand[HAND_INDEX[HAND[i] if i in HAND else "other"]]+=x
        leftover=pool[i]-x
        if i in DECK:
            deck[DECK_INDEX[DECK[i]]]=leftover
    if active=="fan":
        hand[HAND_INDEX["fan_rotom"]]-=1
    elif active=="basic":
        hand[HAND_INDEX["other"]]-=1
    else:
        hand[HAND_INDEX["bunnelby"]]-=1
    assert min(hand)>=0 and min(deck)>=0
    return (tuple(hand),tuple(deck),False,False,False,
            active=="bunnelby",active=="fan")

def enumerate_one(fixed_prizes, remaining_kind):
    after5=tuple(full - used for full, used in zip(FULL,fixed_prizes))
    assert sum(after5)==55
    assert after5[remaining_kind]==1
    summaries=[]
    for sixth,stock in enumerate(after5):
        if not stock or sixth==remaining_kind:
            continue
        pool=list(after5)
        pool[sixth]-=1
        pool=tuple(pool)
        assert sum(pool)==54 and pool[remaining_kind]==1
        checked=0
        gains=0
        incremental=0
        example=None
        for opening in composition(7,pool):
            if opening[ACE]+opening[JIR]>1 or opening[JIR]:
                continue
            active_variants=starters(opening)
            if not active_variants:
                continue
            ways=1
            for x,n in zip(opening,pool):
                ways*=comb(n,x)
            for draw,n in enumerate(pool):
                available=n-opening[draw]
                if available<=0 or not (opening[ACE] or draw==ACE):
                    continue
                for active,act_weight in active_variants:
                    s=mkstate(pool,opening,draw,active)
                    w=stock*ways*available*act_weight
                    checked+=w
                    if _core_possible(s,14):
                        continue
                    if _core_possible(s,15):
                        gains += w
                        hand,deck,*flags=s
                        baseline_hand=list(hand)
                        baseline_hand[HAND_INDEX["secret_box"]]-=1
                        baseline_hand[HAND_INDEX["other"]]+=1
                        baseline=(tuple(baseline_hand),deck,*flags)
                        if not _core_possible(baseline):
                            incremental += w
                        if example is None:
                            example=(opening,draw,active)
            if _core_possible.cache_info().currsize>300_000:
                _core_possible.cache_clear()
        summaries.append((sixth,stock,checked,gains,incremental))
        print("sixth",sixth,"multiplicity",stock,
              "weighted_scenarios",checked,
              "full_only_relative_no_item",gains,
              "also_baseline_failure",incremental,
              "first_witness",example,flush=True)
    assert summaries and all(row[3]>=row[4]>=0 for row in summaries)
    return summaries

def main():
    # Four other Tools and one Artazon Prized, one Artazon left.
    tool4_stadium1=(0,)*13+(4,1)
    # Three other Tools and both Artazon Prized, one Tool left.
    tool3_stadium2=(0,)*13+(3,2)
    a=enumerate_one(tool4_stadium1,STADIUM)
    b=enumerate_one(tool3_stadium2,TOOL)
    # Fixed-five physical multiplicities: two Artazon choices in case A,
    # four choices of which three of four other Tools in case B.
    weighted_gains=2*sum(row[3] for row in a)+4*sum(row[3] for row in b)
    weighted_incremental=2*sum(row[4] for row in a)+4*sum(row[4] for row in b)
    A=1-Fraction(comb(46,7),comb(60,7))
    denom=comb(60,6)*comb(54,7)*47*ACTIVE_MULTIPLIER*A
    p_full_only=Fraction(weighted_gains,1)/denom
    p_incremental=Fraction(weighted_incremental,1)/denom
    assert p_full_only >= p_incremental > 0
    assert p_incremental >= Fraction(5,734379410688)
    print("Exact physically weighted near-tail subcases:",len(a)+len(b))
    print("Full output but no Item mask fails:",p_full_only,float(p_full_only))
    print("Incremental vs Grand Tree and Item absent:",p_incremental,
          float(p_incremental))
    print("Exact fixed-five-Prize, no-Jirachi incidence passed.")

if __name__=="__main__":
    main()
