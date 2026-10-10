"""Independently sample both opposing N and Iono plus K1 state comparisons."""
import json
from fractions import Fraction
from functools import lru_cache
from math import comb, sqrt
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES, choose
from beheeyem_prize_packet import second_draw_success
from beheeyem_reset_state_value import exact_state_reset


def available_packet(hand: list[str], mode: str) -> bool:
    target,payment = MODES[mode]
    has_b,has_t = "B" in hand,"T" in hand
    if has_b and has_t:
        return True
    if "C" not in hand or hand.count("F")+hand.count("E") < payment:
        return False
    return (
        (not has_b and has_t and target in ("pokemon","either"))
        or (has_b and not has_t and target in ("energy","either"))
    )


@lru_cache(maxsize=None)
def k1_compare(hand: tuple[int,...],prizes: tuple[int,...],
               deck: tuple[int,...],d: int,r: int,mode: str) -> bool:
    """Whether N supplies the better next-packet probability at known K1 state."""
    effective_draws = 6-r+d
    iono = second_draw_success(0,0,0,0,*deck,effective_draws,mode)
    n = Fraction()
    for xb in range(min(prizes[0],r)+1):
        for xt in range(min(prizes[1],r-xb)+1):
            for xc in range(min(prizes[2],r-xb-xt)+1):
                xf = r-xb-xt-xc
                ways = (choose(prizes[0],xb)*choose(prizes[1],xt)*
                        choose(prizes[2],xc)*choose(prizes[3],xf))
                if not ways:
                    continue
                joined = tuple(
                    x+y+z for x,y,z in zip(deck,hand,(xb,xt,xc,xf))
                )
                n += Fraction(ways,comb(6,r))*second_draw_success(
                    0,0,0,0,*joined,effective_draws,mode)
    return n > iono


def simulate(B: int,T: int,d: int,mode: str,r: int,
             trials: int,seed: int):
    target,payment = MODES[mode]
    rng = Random(seed)
    residual = ["B"]*B+["T"]*T+["C"]+["F"]*(56-B-T)
    first = n_success = iono_success = n_better_mass = 0

    for _ in range(trials):
        rng.shuffle(residual)
        hand = list(residual[:6])
        prizes = list(residual[6:12])
        deck = list(residual[12:])
        if not ("B" in hand and "T" in hand) and (
            "C" in hand and hand.count("F") >= payment
        ):
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
        p = tuple(prizes.count(card) for card in ("B","T","C","F"))
        z = (deck.count("B"),deck.count("T"),deck.count("C"),
             len(deck)-deck.count("B")-deck.count("T")-deck.count("C"))
        n_better_mass += int(k1_compare(h,p,z,d,r,mode))

        rng.shuffle(prizes)
        hand.extend(prizes[:r])
        effective_draws = 6-r+d

        iono_deck = list(deck)
        rng.shuffle(iono_deck)
        rng.shuffle(hand)
        iono_deck.extend(hand)  # old hand remains at bottom
        iono_success += int(available_packet(iono_deck[:effective_draws],mode))

        n_deck = list(deck)
        n_deck.extend(hand)
        rng.shuffle(n_deck)  # old hand joins full randomized deck
        n_success += int(available_packet(n_deck[:effective_draws],mode))

    observed = [
        first/trials,n_success/trials,iono_success/trials,n_better_mass/trials
    ]
    exact = exact_state_reset(B,T,d,mode,r)
    expected = [exact[0],exact[1],exact[2],exact[3]]
    for x,p in zip(observed,expected):
        pv = float(p)
        sigma = sqrt(max(pv*(1-pv),1/trials)/trials)
        assert abs(x-pv) < 6*sigma+1/trials, (
            B,T,d,mode,r,x,pv,sigma
        )
    return {
        "B":B,"TAE":T,"draws":d,"tutor":mode,"Prizes_taken":r,
        "trials":trials,"seed":seed,
        "observed_percent":[round(x*100,6) for x in observed],
        "exact_percent":[round(float(x)*100,6) for x in expected]
    }


if __name__ == "__main__":
    cases = (
        (4,4,1,"computer_search",0,20261010),
        (4,4,1,"computer_search",1,20261011),
        (4,4,1,"computer_search",2,20261012),
        (1,4,1,"mysterious_treasure",1,20261013),
    )
    print(json.dumps([
        simulate(B,T,d,mode,r,200_000,seed)
        for B,T,d,mode,r,seed in cases
    ],indent=2))
