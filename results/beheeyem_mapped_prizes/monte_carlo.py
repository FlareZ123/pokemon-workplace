"""Independent physical validation of optimally mapped Prize selection."""
import json
from functools import lru_cache
from math import comb, sqrt
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES, choose
from beheeyem_prize_packet import second_draw_success
from beheeyem_mapped_prizes import exact_mapped_prizes


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
def choose_mapped_prizes(
    hand: tuple[int,...], prizes: tuple[int,...],
    deck: tuple[int,...], d: int, r: int, mode: str
) -> tuple[int,...]:
    best_probability = -1
    best = None
    for xb in range(min(prizes[0],r)+1):
        for xt in range(min(prizes[1],r-xb)+1):
            for xc in range(min(prizes[2],r-xb-xt)+1):
                xf = r-xb-xt-xc
                selected = (xb,xt,xc,xf)
                if any(x>p for x,p in zip(selected,prizes)):
                    continue
                updated = tuple(x+y for x,y in zip(hand,selected))
                q = second_draw_success(*updated,*deck,d,mode)
                if q > best_probability:
                    best_probability = q
                    best = selected
    assert best is not None
    return best


def simulate(B: int,T: int,d: int,mode: str,r: int,
             trials: int,seed: int):
    target,payment = MODES[mode]
    rng = Random(seed)
    residual = ["B"]*B+["T"]*T+["C"]+["F"]*(56-B-T)
    first = blind_wins = mapped_wins = 0

    for _ in range(trials):
        rng.shuffle(residual)
        hand = list(residual[:6])
        prize_cards = list(residual[6:12])
        deck = list(residual[12:])
        direct = "B" in hand and "T" in hand
        if not direct and "C" in hand and hand.count("F") >= payment:
            missing = None
            if "B" not in hand and "T" in hand and target in ("pokemon","either"):
                missing = "B"
            elif "T" not in hand and "B" in hand and target in ("energy","either"):
                missing = "T"
            if missing in deck:
                hand.remove("C")
                for _ in range(payment):
                    hand.remove("F")
                deck.remove(missing)
                hand.append(missing)

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
        selected = choose_mapped_prizes(h,p,z,d,r,mode)

        mapped_picks = []
        for card,count in zip(("B","T","C","F"),selected):
            mapped_picks.extend([card]*count)
        assert len(mapped_picks) == r
        remaining = list(prize_cards)
        for card in mapped_picks:
            remaining.remove(card)

        rng.shuffle(prize_cards)
        blind_picks = prize_cards[:r]
        rng.shuffle(deck)
        blind_hand = hand + blind_picks + deck[:d]
        mapped_hand = hand + mapped_picks + deck[:d]
        blind_wins += int(packet_possible(blind_hand,mode))
        mapped_wins += int(packet_possible(mapped_hand,mode))

    observed = [first/trials,blind_wins/trials,mapped_wins/trials]
    x = exact_mapped_prizes(B,T,d,mode,r)
    expected = [x[0],x[1],x[2]]
    for o,p in zip(observed,expected):
        pv = float(p)
        sigma = sqrt(max(pv*(1-pv),1/trials)/trials)
        assert abs(o-pv) < 6*sigma+1/trials, (
            B,T,d,mode,r,o,pv,sigma
        )
    return {
        "B":B,"TAE":T,"draws":d,"tutor":mode,
        "Prizes_awarded":r,"trials":trials,"seed":seed,
        "observed_percent":[round(o*100,6) for o in observed],
        "exact_percent":[round(float(p)*100,6) for p in expected]
    }


if __name__ == "__main__":
    cases = (
        (4,4,1,"computer_search",1,20261010),
        (4,4,1,"computer_search",2,20261011),
        (1,4,1,"mysterious_treasure",1,20261012),
        (4,4,3,"ultra_ball",2,20261013),
    )
    print(json.dumps([
        simulate(B,T,d,mode,r,200_000,seed)
        for B,T,d,mode,r,seed in cases
    ],indent=2))
