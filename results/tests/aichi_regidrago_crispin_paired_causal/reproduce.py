"""Independent physical opener/Prize/draw test of paired Energy choices."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path

from tools.aichi_regidrago_crispin_paired_causal import after_payment, build, exact_paired_stock


def brute(n: int, rv: int, basic: int, dde: int, grass: int, fire: int) -> Fraction | None:
    cards = (["Regidrago V"]*rv + ["Basic"]*basic + ["DDE"]*dde
             + ["Grass"]*grass + ["Fire"]*fire)
    cards += ["Other"] * (n-len(cards))
    success = cases = 0
    for opening in combinations(range(n),3):
        initial = [cards[i] for i in opening]
        if "Regidrago V" not in initial and "Basic" not in initial:
            continue
        unseen = tuple(i for i in range(n) if i not in opening)
        for prize_ids in combinations(unseen,2):
            leftover = tuple(i for i in unseen if i not in prize_ids)
            prizes = tuple(cards[i] for i in prize_ids)
            for draw in leftover:
                hand = tuple(initial+[cards[draw]])
                if not all(name in hand for name in ("Regidrago V","DDE","Grass","Fire")):
                    continue
                deck = tuple(cards[i] for i in leftover if i!=draw)
                a=after_payment(hand,deck,prizes,"Grass")
                b=after_payment(hand,deck,prizes,"Fire")
                assert a["deck"]==b["deck"] and a["prizes"]==b["prizes"]
                assert a["crispin_two_type_stock"]==b["crispin_two_type_stock"]
                success+=int(a["crispin_two_type_stock"])
                cases+=1
    return Fraction(success,cases) if cases else None


def main() -> None:
    count=0
    for n in range(6,10):
        for rv in range(1,min(n,2)+1):
            for basic in range(min(n-rv,2)+1):
                for dde in range(1,min(n-rv-basic,2)+1):
                    for grass in range(1,min(n-rv-basic-dde,2)+1):
                        for fire in range(1,min(n-rv-basic-dde-grass,2)+1):
                            predicted=exact_paired_stock(total=n,regidrago=rv,
                                other_basic=basic,dde=dde,grass=grass,fire=fire,
                                opening=3,prizes=2)
                            actual=brute(n,rv,basic,dde,grass,fire)
                            assert predicted["after_grass"]==actual==predicted["after_fire"]
                            count+=1
    assert count==137
    result=build(Path("."))
    assert result["outcomes"]["causal_difference"]=="0"
    print("PASS: 137 independent physical hand/Prize/draw configurations")
    print(result)


if __name__=="__main__":
    main()
