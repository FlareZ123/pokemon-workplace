"""Independent material conservation and dynamic-policy envelope regression."""
from __future__ import annotations

from fractions import Fraction
from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from bench_draw_zone_policy import all_policies, evaluate, optimize, closed_optimal_value


def physical_eval(policy, *, earlier: int, prizes: int, deck: int,
                  crobat_draw: int, H: Fraction, G: Fraction, C: Fraction):
    outcomes=[]
    N=earlier+prizes+deck
    for loc in range(N):
        hand=["C","D"]+(["K"] if loc<earlier else [])
        prize_cards=["K" if loc==earlier+i else f"P{i}" for i in range(prizes)]
        deck_cards=["K" if loc==earlier+prizes+i else f"z{i}"
                    for i in range(deck)]
        bench=[]
        discard=[]
        def play_dede():
            hand.remove("D")
            bench.append("D")
            discard.extend(hand)
            hand.clear()
            hand.extend(deck_cards[:6])
            del deck_cards[:6]
        def play_crobat():
            hand.remove("C")
            bench.append("C")
            hand.extend(deck_cards[:crobat_draw])
            del deck_cards[:crobat_draw]
        if "K" in hand:
            if policy.initial_found=="dede":
                play_dede()
        elif policy.initial_missing == "dede":
            play_dede()
        elif policy.initial_missing == "crobat":
            play_crobat()
            if "K" in hand and policy.crobat_found=="dede":
                play_dede()
            elif "K" not in hand and policy.crobat_missing=="dede":
                play_dede()
        assert (hand+prize_cards+deck_cards+bench+discard).count("K")==1
        outcomes.append((int("K" in hand),int("K" in discard),len(bench)))
    masses=tuple(Fraction(sum(x[i] for x in outcomes),N) for i in range(3))
    return masses + (H*masses[0]+G*masses[1]-C*masses[2],)


def validate() -> None:
    num_tests=0
    for earlier, prizes, deck, a in product((0,1,2),(0,2),(8,12),(0,1,2,3)):
        if a+6>deck:
            continue
        for p in all_policies():
            result=evaluate(p,earlier=earlier,prizes=prizes,deck=deck,
                            crobat_draw=a,hand_value=Fraction(2),
                            discard_value=Fraction(3),bench_cost=Fraction(1,4))
            expected=physical_eval(p,earlier=earlier,prizes=prizes,
                                   deck=deck,crobat_draw=a,H=Fraction(2),
                                   G=Fraction(3),C=Fraction(1,4))
            assert (result.hand,result.discarded,result.bench,
                    result.utility)==expected,(earlier,prizes,deck,a,p)
            num_tests+=1
        for H,G,C in product((Fraction(0),Fraction(1),Fraction(2)),
                              (Fraction(0),Fraction(1),Fraction(2)),
                              (Fraction(0),Fraction(1,100),Fraction(1,25),
                               Fraction(1,10),Fraction(1,2))):
            result=optimize(earlier=earlier,prizes=prizes,deck=deck,
                            crobat_draw=a,hand_value=H,discard_value=G,
                            bench_cost=C)
            analytical=closed_optimal_value(earlier=earlier,prizes=prizes,
                                           deck=deck,crobat_draw=a,
                                           hand_value=H,discard_value=G,
                                           bench_cost=C)
            assert result.utility==analytical,(earlier,prizes,deck,a,H,G,C)
            num_tests+=1
    hand=optimize()
    assert (hand.hand,hand.discarded,hand.bench)==(
        Fraction(9,53),Fraction(0),Fraction(102,53))
    discard=optimize(discard_value=Fraction(2))
    assert (discard.hand,discard.discarded,discard.bench)==(
        Fraction(6,53),Fraction(3,53),Fraction(105,53))
    expensive=optimize(discard_value=Fraction(2),bench_cost=Fraction(1,10))
    assert (expensive.hand,expensive.discarded,expensive.bench)==(
        Fraction(6,53),Fraction(1,53),Fraction(1))
    crossover=optimize(bench_cost=Fraction(1,25))
    assert crossover.policy.initial_missing=="dede"
    print("Independent physical zone conservation and belief-policy envelope passed:",
          num_tests,"cases")
    for label,kws in [
            ("Value only K in hand",{}),
            ("Discard worth double hand",{"discard_value":Fraction(2)}),
            ("Discard double and Bench cost 4%",{"discard_value":Fraction(2),
                                                 "bench_cost":Fraction(1,25)}),
            ("Discard double and Bench cost 10%",{"discard_value":Fraction(2),
                                                  "bench_cost":Fraction(1,10)}),
            ("Hand only and Bench cost 4%",{"bench_cost":Fraction(1,25)})]:
        x=optimize(**kws)
        print(label,":",x)


if __name__ == "__main__":
    validate()
