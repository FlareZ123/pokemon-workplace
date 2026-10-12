"""SFT: independent physical ID Item DFS including one-use VSTAR tutoring."""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import combinations

from tools.regidrago_joint_launch import Build,analyze as prior_item
from tools.regidrago_vstar_tutoring_joint import analyze


@lru_cache(maxsize=None)
def physical(
    hand: frozenset[str], deck: frozenset[str],
    reg: bool,vstar: bool,loaded: bool,
) -> bool:
    if reg and vstar and loaded:
        return True
    for item in hand:
        kind=item.split(":")[0]
        if kind=="Compressor":
            for target in deck:
                if target.startswith("Dragapult:") and physical(
                    hand-{item},deck-{target},reg,vstar,True):
                    return True
        elif kind=="VIP":
            for target in deck:
                if target.startswith("Regidrago:") and physical(
                    hand-{item},deck-{target},True,vstar,loaded):
                    return True
        elif kind in ("Quick Ball","Mysterious Treasure"):
            for discard in hand-{item}:
                if not discard.startswith("Dragapult:"):
                    continue
                paid=hand-{item,discard}
                if physical(paid,deck,reg,vstar,True):
                    return True
                for target in deck:
                    if target.startswith("Regidrago:") and physical(
                        paid,deck-{target},True,vstar,True):
                        return True
                    if kind=="Mysterious Treasure":
                        if target.startswith("VSTAR:") and physical(
                            paid|{target},deck-{target},reg,True,True):
                            return True
                        if target.startswith("Dragapult:") and physical(
                            paid|{target},deck-{target},reg,vstar,True):
                            return True
    return False


def brute(build: Build,vstar: int,opener: int,prizes: int) -> Fraction:
    groups=(
        ("Regidrago",build.regidrago_v),
        ("Other Basic",build.other_basics),
        ("VSTAR",vstar),
        ("Dragapult",build.dragapult),
        ("VIP",build.vip),
        ("Quick Ball",build.quick_ball),
        ("Mysterious Treasure",build.treasure),
        ("Compressor",build.compressor),
    )
    cards=tuple(f"{name}:{i}" for name,n in groups for i in range(n))
    cards+=tuple(f"Filler:{i}" for i in range(build.total-len(cards)))
    win=valid=0
    for open_cards in combinations(cards,opener):
        if not any(c.startswith(("Regidrago:","Other Basic:"))
                   for c in open_cards):
            continue
        rest=tuple(c for c in cards if c not in open_cards)
        for draw in rest:
            hand=frozenset(open_cards+(draw,))
            remaining=tuple(c for c in rest if c!=draw)
            for prize in combinations(remaining,prizes):
                deck=frozenset(c for c in remaining if c not in prize)
                valid+=1
                win+=int(physical(
                    hand,deck,
                    any(c.startswith("Regidrago:") for c in hand),
                    any(c.startswith("VSTAR:") for c in hand),
                    False,
                ))
    return Fraction(win,valid)


def main() -> None:
    configs=(
        (Build(regidrago_v=2,other_basics=1,dragapult=1,
               vip=1,quick_ball=1,treasure=1,compressor=1,total=10),1,2,1),
        (Build(regidrago_v=2,other_basics=1,dragapult=2,
               vip=0,quick_ball=1,treasure=1,compressor=1,total=10),1,2,1),
        (Build(regidrago_v=2,other_basics=1,dragapult=1,
               vip=2,quick_ball=1,treasure=2,compressor=1,total=12),2,3,2),
        (Build(regidrago_v=2,other_basics=1,dragapult=2,
               vip=1,quick_ball=1,treasure=2,compressor=1,total=12),2,3,2),
    )
    for build,vstar,opener,prizes in configs:
        computed=analyze(build,vstar,opener=opener,prizes=prizes)
        actual=brute(build,vstar,opener,prizes)
        assert computed.reg_discard_and_vstar==actual,(build,computed,actual)
        assert computed.reg_and_discard==prior_item(
            build,opener=opener,prizes=prizes)["joint_any"]
        assert computed.reg_discard_and_vstar<=computed.reg_and_discard
    print("PASS: 4 independent full physical Item/VSTAR search-oracle populations")

    original=analyze(Build(),3)
    variant=analyze(Build(dragapult=2,vip=2),3)
    assert original.reg_discard_and_vstar==Fraction(
        43216789535971,782453592320400)
    assert variant.reg_discard_and_vstar==Fraction(
        31913922580498969,367753188390588000)
    assert variant.reg_discard_and_vstar>original.reg_discard_and_vstar
    print("PASS: printed 60-source Regidrago VSTAR + Dragon first-turn tutoring rates")
    print("Published:",original.reg_discard_and_vstar)
    print("Experimental:",variant.reg_discard_and_vstar)
    print("LIMIT: no Energy, turn-two evolution, opponent or complete match policy")


if __name__=="__main__":
    main()
