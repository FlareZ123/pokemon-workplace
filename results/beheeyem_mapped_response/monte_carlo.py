"""Independent physical Monte Carlo for mapped Prize choice under surprise N."""
import json
from functools import lru_cache
from fractions import Fraction
from math import comb,sqrt
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES, choose
from beheeyem_prize_packet import second_draw_success
from beheeyem_mapped_response import exact_mapping_response


def packet_possible(hand: list[str], mode: str) -> bool:
    target,payment = MODES[mode]
    b,t = "B" in hand,"T" in hand
    if b and t:
        return True
    if "C" not in hand or hand.count("F")+hand.count("E") < payment:
        return False
    return (
        (not b and t and target in ("pokemon","either"))
        or (b and not t and target in ("energy","either"))
    )


@lru_cache(maxsize=None)
def mapped_choices(hand: tuple[int,...],prizes: tuple[int,...],
                   deck: tuple[int,...],d: int,r: int,mode: str):
    candidates = []
    for xb in range(min(prizes[0],r)+1):
        for xt in range(min(prizes[1],r-xb)+1):
            for xc in range(min(prizes[2],r-xb-xt)+1):
                xf = r-xb-xt-xc
                selection = (xb,xt,xc,xf)
                if any(s>p for s,p in zip(selection,prizes)):
                    continue
                next_hand = tuple(x+y for x,y in zip(hand,selection))
                pool = tuple(x+y for x,y in zip(deck,next_hand))
                q0 = second_draw_success(*next_hand,*deck,d,mode)
                qN = second_draw_success(
                    0,0,0,0,*pool,6-r+d,mode)
                candidates.append((selection,q0,qN))

    best_no = max(candidates,key=lambda x:(x[1],x[2]))
    best_N = max(candidates,key=lambda x:x[2])
    return best_no[0],best_N[0],best_N[2]>best_no[2]


def make_picks(selected: tuple[int,...]) -> list[str]:
    return [
        card for card,count in zip(("B","T","C","F"),selected)
        for _ in range(count)
    ]


def simulate(B: int,T: int,d: int,mode: str,r: int,
             trials: int,seed: int):
    target,payment = MODES[mode]
    rng = Random(seed)
    pool = ["B"]*B+["T"]*T+["C"]+["F"]*(56-B-T)
    first = blind = mapped_N = mapped_no_under_N = conflicts = 0

    for _ in range(trials):
        rng.shuffle(pool)
        hand = list(pool[:6])
        prize_cards = list(pool[6:12])
        deck = list(pool[12:])
        if not ("B" in hand and "T" in hand) and (
            "C" in hand and hand.count("F") >= payment
        ):
            target_card = None
            if "B" not in hand and "T" in hand and target in ("pokemon","either"):
                target_card = "B"
            elif "T" not in hand and "B" in hand and target in ("energy","either"):
                target_card = "T"
            if target_card in deck:
                hand.remove("C")
                for _ in range(payment):
                    hand.remove("F")
                deck.remove(target_card)
                hand.append(target_card)
        if "B" not in hand or "T" not in hand:
            continue

        first += 1
        hand.remove("B")
        hand.remove("T")
        deck.extend(("B","T","E"))
        assert len(deck) in (47,48)

        h = tuple(hand.count(card) for card in ("B","T","C","F"))
        p = tuple(prize_cards.count(card) for card in ("B","T","C","F"))
        z = (deck.count("B"),deck.count("T"),deck.count("C"),
             len(deck)-deck.count("B")-deck.count("T")-deck.count("C"))
        no_choice,N_choice,conflict = mapped_choices(h,p,z,d,r,mode)
        conflicts += int(conflict)

        rng.shuffle(prize_cards)
        options = (
            list(prize_cards[:r]),
            make_picks(N_choice),
            make_picks(no_choice)
        )
        results = []
        for pickups in options:
            n_deck = list(deck) + hand + pickups
            rng.shuffle(n_deck)  # physically shuffle full hand into deck
            results.append(packet_possible(n_deck[:6-r+d],mode))
        blind += int(results[0])
        mapped_N += int(results[1])
        mapped_no_under_N += int(results[2])

    observed = [v/trials for v in (
        first,blind,mapped_N,mapped_no_under_N,conflicts
    )]
    x = exact_mapping_response(B,T,d,mode,r)
    expected = [x[0],x[1],x[2],x[5],x[7]]
    for o,p in zip(observed,expected):
        pv = float(p)
        sigma = sqrt(max(pv*(1-pv),1/trials)/trials)
        assert abs(o-pv) < 6*sigma+1/trials, (
            B,T,d,mode,r,o,pv,sigma
        )
    return {
        "B":B,"TAE":T,"draws":d,"tutor":mode,
        "Prizes_awarded":r,"trials":trials,"seed":seed,
        "events":["first","N_blind","N_mapped","N_if_noReply_mapped",
                  "strict_choosing_conflict"],
        "observed_percent":[round(o*100,6) for o in observed],
        "exact_percent":[round(float(p)*100,6) for p in expected]
    }


if __name__ == "__main__":
    cases = (
        (4,4,1,"computer_search",1,20261010),
        (4,4,1,"computer_search",2,20261011),
        (4,4,1,"mysterious_treasure",1,20261012),
        (1,4,1,"mysterious_treasure",2,20261013),
    )
    print(json.dumps([
        simulate(B,T,d,mode,r,200_000,seed)
        for B,T,d,mode,r,seed in cases
    ],indent=2))
