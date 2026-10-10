"""Physical-shuffle comparison of one random Prize pickup and one extra deck draw."""
import json
from fractions import Fraction
from math import sqrt
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES
from beheeyem_prize_packet import second_draw_success
from beheeyem_prize_vs_draw import compare_known_prizes


def packet_possible(hand: list[str], mode: str) -> bool:
    target, payment = MODES[mode]
    b, t = "B" in hand, "T" in hand
    if b and t:
        return True
    if "C" not in hand or hand.count("F") < payment:
        return False
    return (
        (not b and t and target in ("pokemon","either")) or
        (b and not t and target in ("energy","either"))
    )


def simulate(B: int, T: int, d: int, mode: str, trials: int, seed: int):
    target, payment = MODES[mode]
    rng = Random(seed)
    pool = ["B"]*B + ["T"]*T + ["C"] + ["F"]*(56-B-T)
    first = prize_wins = draw_wins = k1_prize_better = 0

    for _ in range(trials):
        rng.shuffle(pool)
        hand = list(pool[:6])
        prizes = list(pool[6:12])
        deck = list(pool[12:])
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
        snapshot = {
            card:hand.count(card) for card in ("B","T","C","F")
        }
        counts = {card:deck.count(card) for card in ("B","T","C")}
        counts["F"] = len(deck)-sum(counts.values())
        prize_counts = tuple(prizes.count(card) for card in ("B","T","C","F"))
        h = tuple(snapshot[card] for card in ("B","T","C","F"))
        z = tuple(counts[card] for card in ("B","T","C","F"))
        prize_q = Fraction()
        for i, copies in enumerate(prize_counts):
            if copies:
                hplus = list(h)
                hplus[i] += 1
                prize_q += Fraction(copies,6)*second_draw_success(*hplus,*z,d,mode)
        deck_q = second_draw_success(*h,*z,d+1,mode)
        k1_prize_better += int(prize_q > deck_q)

        rng.shuffle(prizes)
        rng.shuffle(deck)
        prize_hand = hand + prizes[:1] + deck[:d]
        draw_hand = hand + deck[:d+1]
        prize_wins += int(packet_possible(prize_hand,mode))
        draw_wins += int(packet_possible(draw_hand,mode))

    observed = [v / trials for v in (first,prize_wins,draw_wins,k1_prize_better)]
    exact = compare_known_prizes(B,T,d,mode)
    expected = [exact[0],exact[1],exact[2],exact[3]]
    for o,p in zip(observed,expected):
        pv = float(p)
        sigma = sqrt(max(pv*(1-pv),1/trials)/trials)
        assert abs(o-pv) < 6*sigma + 1/trials, (B,T,d,mode,o,pv,sigma)
    return {
        "B":B,"TAE":T,"T3_base_draws":d,"tutor":mode,
        "trials":trials,"seed":seed,
        "rates":["first","Prize_win","extra_draw_win","K1_Prize_better"],
        "observed_percent":[round(x*100,6) for x in observed],
        "exact_percent":[round(float(p)*100,6) for p in expected],
    }


if __name__ == "__main__":
    cases = (
        (4,4,1,"computer_search",20261010),
        (4,4,2,"ultra_ball",20261011),
        (1,4,1,"mysterious_treasure",20261012),
        (1,1,1,"computer_search",20261013),
    )
    print(json.dumps([
        simulate(B,T,d,mode,200_000,seed)
        for B,T,d,mode,seed in cases
    ],indent=2))
