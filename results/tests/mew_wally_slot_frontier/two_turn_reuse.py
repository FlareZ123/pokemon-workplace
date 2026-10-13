"""Two-turn Mew VMAX reattack witness following T1 copied Techno Blast.

Strict natural-card route only: initial Active Mew, Genesect in hand,
Wally and DCE in eight naturally visible cards, searched VMAX in deck,
then next-turn free retreat into Genesect and Escape Rope/Guzma back.
Opponent is assumed to leave Mew alive and to permit the card effects.
"""
from __future__ import annotations
import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from results.tests.mew_wally_first_attack.reproduce import opening_counts, probability_all_prized

# Mew V, Genesect V, Mew VMAX, Wally, DCE, Escape Rope, Guzma, other.
EXPECTED={
 (1,False):Fraction(1150957100242,2078047884787875),
 (1,True):Fraction(55960120859,36456980434875),
 (2,False):Fraction(34302424756,31969967458275),
 (2,True):Fraction(26733227888,8995878289125),
}

def population(wally):
    data=(4,4,3,wally,4,1,2,42-wally)
    assert sum(data)==60
    return data

def exact(pool,hand,prizes,opponent_bench):
    n=sum(pool)
    assert hand+prizes+2<n
    denom=comb(n,hand)*(n-hand)
    out=Counter()
    for initial,ways in opening_counts(pool,hand):
        if not initial[0]:continue
        for drawn,copies in enumerate(pool):
            available=copies-initial[drawn]
            if not available:continue
            held=list(initial);held[drawn]+=1
            if not (held[1] and held[3] and held[4]):continue
            v=pool[2]-held[2]
            if v<1:continue
            weight=Fraction(ways*available,denom)
            unseen=n-hand-1
            mobility_held=held[5] or (opponent_bench and held[6])
            if mobility_held:
                probability=1-probability_all_prized(unseen,prizes,v)
                out["held_switch"]+=weight*probability
                continue
            mobile=pool[5]-held[5]
            if opponent_bench:mobile+=pool[6]-held[6]
            if not mobile:continue
            chance=Fraction(0)
            for vmax_prized in range(min(v,prizes)+1):
                if vmax_prized==v:continue
                for switch_prized in range(min(mobile,prizes-vmax_prized)+1):
                    other_prized=prizes-vmax_prized-switch_prized
                    if other_prized>unseen-v-mobile:continue
                    prize_mass=Fraction(
                        comb(v,vmax_prized)*comb(mobile,switch_prized)*
                        comb(unseen-v-mobile,other_prized),
                        comb(unseen,prizes))
                    # One VMAX is removed by Wally, so the next natural draw
                    # comes from a deck of this length after that search.
                    chance+=prize_mass*Fraction(
                        mobile-switch_prized,unseen-prizes-1)
            out["turn2_draw_switch"]+=weight*chance
    return dict(out)

def physical_oracle(pool,hand,prizes,opponent_bench):
    cards=tuple(kind for kind,copies in enumerate(pool) for _ in range(copies))
    n=len(cards)
    den=comb(n,hand)*comb(n-hand,prizes)*(n-hand-prizes)*(n-hand-prizes-2)
    out=Counter()
    for chosen in combinations(range(n),hand):
        opening=set(chosen)
        if not any(cards[i]==0 for i in opening):continue
        remaining=set(range(n))-opening
        for prize in combinations(sorted(remaining),prizes):
            hidden=set(prize)
            for first_draw in remaining-hidden:
                hand_cards=Counter(cards[i] for i in opening|{first_draw})
                if not (hand_cards[1] and hand_cards[3] and hand_cards[4]):
                    continue
                deck=remaining-hidden-{first_draw}
                vmax_ids=sorted(i for i in deck if cards[i]==2)
                if not vmax_ids:continue
                # Wally selects a physical VMAX from deck. Its identical
                # copies are exchangeable; remove one before T2 deck draw.
                after_wally=deck-{vmax_ids[0]}
                held=bool(hand_cards[5] or (opponent_bench and hand_cards[6]))
                for turn2_draw in after_wally:
                    if held:
                        out["held_switch"]+=1
                    elif cards[turn2_draw]==5 or (
                        opponent_bench and cards[turn2_draw]==6):
                        out["turn2_draw_switch"]+=1
    return {k:Fraction(v,den) for k,v in out.items()}

def verify_cards():
    def card(print_id):
        set_id=print_id.rsplit("-",1)[0]
        path=ROOT/"resources/cards/en"/(set_id+".json")
        return next(x for x in json.loads(path.read_text(encoding="utf-8"))
                    if x["id"]==print_id)
    mew=card("swsh8-114")
    gene=card("swsh8-185")
    wally=card("xy6-94")
    rope=card("swsh5-125")
    guzma=card("sm3-115")
    assert not mew.get("retreatCost")
    assert any(a["name"]=="Cross Fusion Strike" and
               "Benched Fusion Strike" in a["text"] for a in mew["attacks"])
    assert any(a["name"]=="Techno Blast" and a["damage"]=="210" and
               "next turn" in a["text"] for a in gene["attacks"])
    assert "first turn" in " ".join(wally["rules"])
    assert "opponent switches first" in " ".join(rope["rules"]).lower()
    assert "If you do, switch your Active" in " ".join(guzma["rules"])
    assert gene.get("retreatCost")==["Colorless","Colorless"]

def main():
    verify_cards()
    fixtures=(
        ((1,1,1,1,1,1,1,4),3,2),
        ((2,1,2,2,1,1,2,2),4,2),
        ((1,2,2,2,2,1,1,2),4,2),
    )
    for pop,h,p in fixtures:
        for bench in (False,True):
            a=exact(pop,h,p,bench)
            b=physical_oracle(pop,h,p,bench)
            assert a==b,(pop,bench,a,b)
        print(f"Independent two-turn physical deal oracle PASSED N={sum(pop)}")
    for (w,bench),expected in EXPECTED.items():
        observed=exact(population(w),7,6,bench)
        total=sum(observed.values(),Fraction(0))
        assert total==expected,(w,bench,total,expected)
        print(f"Wally={w} opponent bench={bench}, strict T2 reattack: "+
              f"{float(total):.12%}; exact={total}")
    print("NOTE: conditional Mew survival, playable switch effects, no other draws/lines.")

if __name__=="__main__":main()
