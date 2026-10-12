"""SFT: independent physical-card search oracle plus a pre-search natural draw."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb

from tools.regidrago_joint_energy_gate import analyze
from tools.regidrago_joint_launch import Build, analyze as item_analyze
from tools.regidrago_two_turn_natural_energy import calculate as energy_analyze


@lru_cache(maxsize=None)
def physical_joint(hand: frozenset[str], deck: frozenset[str],
                   placed: bool, loaded: bool) -> bool:
    """Actual labeled Item choices with explicitly consumed physical IDs."""
    if placed and loaded:
        return True

    for item in hand:
        name=item.split(":")[0]
        if name=="Compressor":
            for target in deck:
                if target.startswith("Dragapult:") and physical_joint(
                    hand-{item},deck-{target},placed,True):
                    return True
        elif name=="VIP":
            for target in deck:
                if target.startswith("Regidrago:") and physical_joint(
                    hand-{item},deck-{target},True,loaded):
                    return True
        elif name in ("Quick Ball","Mysterious Treasure"):
            for payment in hand-{item}:
                if not payment.startswith("Dragapult:"):
                    continue
                paid=hand-{item,payment}
                if physical_joint(paid,deck,placed,True):
                    return True
                for target in deck:
                    if target.startswith("Regidrago:") and physical_joint(
                        paid,deck-{target},True,True):
                        return True
    return False


def oracle(build: Build, dde: int, basic_energy: int,
           opener: int, prizes: int) -> tuple[Fraction,Fraction,Fraction]:
    raw = (
        ("Regidrago",build.regidrago_v),
        ("Other Basic",build.other_basics),
        ("Dragapult",build.dragapult),
        ("VIP",build.vip),
        ("Quick Ball",build.quick_ball),
        ("Mysterious Treasure",build.treasure),
        ("Compressor",build.compressor),
        ("DDE",dde),
        ("Basic Energy",basic_energy),
    )
    count=sum(v for _,v in raw)
    cards=tuple(f"{name}:{i}" for name,copies in raw for i in range(copies))
    cards+=tuple(f"Filler:{i}" for i in range(build.total-count))

    weight_valid=weight_joint=weight_energy=weight_triple=0
    for opening in combinations(cards,opener):
        if not any(c.startswith(("Regidrago:","Other Basic:")) for c in opening):
            continue
        unseen=tuple(c for c in cards if c not in opening)
        for natural in unseen:
            hand=frozenset(opening+(natural,))
            rest=tuple(c for c in unseen if c!=natural)
            for prize in combinations(rest,prizes):
                searchable=frozenset(c for c in rest if c not in prize)
                item=physical_joint(
                    hand,searchable,any(c.startswith("Regidrago:") for c in hand),
                    False,
                )
                for turntwo in searchable:
                    exposed=opening+(natural,turntwo)
                    d=sum(c.startswith("DDE:") for c in exposed)
                    b=sum(c.startswith("Basic Energy:") for c in exposed)
                    energy=d>=1 and d+b>=2
                    weight_valid+=1
                    weight_joint+=int(item)
                    weight_energy+=int(energy)
                    weight_triple+=int(item and energy)
    return (
        Fraction(weight_joint,weight_valid),
        Fraction(weight_energy,weight_valid),
        Fraction(weight_triple,weight_valid),
    )


def main() -> None:
    tested=0
    for build in (
        Build(regidrago_v=2,other_basics=1,dragapult=1,vip=1,
              quick_ball=1,treasure=1,compressor=1,total=10),
        Build(regidrago_v=2,other_basics=1,dragapult=2,vip=0,
              quick_ball=1,treasure=1,compressor=1,total=10),
        Build(regidrago_v=2,other_basics=1,dragapult=1,vip=2,
              quick_ball=1,treasure=1,compressor=1,total=12),
        Build(regidrago_v=2,other_basics=1,dragapult=2,vip=1,
              quick_ball=1,treasure=1,compressor=1,total=12),
    ):
        for (opener,prizes,dde,basic) in ((2,1,1,1),(3,2,1,2)):
            if build.total<12 and opener==3:
                continue
            exact=analyze(build,dde,basic,opener=opener,prizes=prizes)
            literal=oracle(build,dde,basic,opener,prizes)
            assert (exact.item_joint,exact.energy_pair,
                    exact.item_and_natural_energy)==literal, (
                    build,opener,prizes,exact,literal)
            assert exact.item_joint==item_analyze(build,opener=opener,prizes=prizes)["joint_any"]
            assert exact.energy_pair==energy_analyze(
                build.total,opener,build.regidrago_v+build.other_basics,
                dde,basic).ready_given_valid_opening
            tested+=1
    print(f"PASS: {tested} full labeled Item/Prize/turn-draw toy populations")

    standard=analyze(Build(),4,6)
    variant=analyze(Build(dragapult=2,vip=2),4,6)
    assert standard.item_joint==Fraction(0) + item_analyze(Build())["joint_any"]
    assert variant.item_joint==item_analyze(Build(dragapult=2,vip=2))["joint_any"]
    assert standard.energy_pair==variant.energy_pair==Fraction(
        1277933731,3913833495)
    assert standard.item_and_natural_energy==Fraction(
        43802912931679,1337284321420320)
    assert variant.item_and_natural_energy==Fraction(
        408575428938988601,8458323332983524000)
    assert variant.item_and_natural_energy-standard.item_and_natural_energy==Fraction(
        177253375533853,11399357591622000)
    assert standard.naive_independent_product>standard.item_and_natural_energy
    assert variant.naive_independent_product>variant.item_and_natural_energy
    print("PASS: 60-card independent-pair overestimate rejected")
    print("published joint+natural Energy",standard.item_and_natural_energy)
    print("candidate joint+natural Energy",variant.item_and_natural_energy)
    print("candidate paired source gain",variant.item_and_natural_energy-standard.item_and_natural_energy)
    print("LIMIT: pre-search next-draw floor, VSTAR evolution and game outcomes excluded")


if __name__=="__main__":
    main()
