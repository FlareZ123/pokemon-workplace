"""SFT: independent physical-card four-channel Prize/Item/draw oracle."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from tools.regidrago_joint_launch import Build
from tools.regidrago_vstar_natural_joint import analyze
from results.decks.regidrago_dragapult_2.joint_energy_reproduce import physical_joint


def brute(build: Build, opener: int, prizes: int,
          dde: int, basic: int, vstar: int) -> tuple[Fraction,Fraction,Fraction]:
    groups=(
        ("Regidrago",build.regidrago_v),
        ("Other Basic",build.other_basics),
        ("Dragapult",build.dragapult),
        ("VIP",build.vip),
        ("Quick Ball",build.quick_ball),
        ("Mysterious Treasure",build.treasure),
        ("Compressor",build.compressor),
        ("DDE",dde),
        ("Basic Energy",basic),
        ("VSTAR",vstar),
    )
    cards=tuple(f"{name}:{i}" for name,n in groups for i in range(n))
    cards+=tuple(f"Filler:{i}" for i in range(build.total-len(cards)))

    valid=item_count=mat_count=joint_count=0
    for open_cards in combinations(cards,opener):
        if not any(c.startswith(("Regidrago:","Other Basic:"))
                   for c in open_cards):
            continue
        rest=tuple(c for c in cards if c not in open_cards)
        for first in rest:
            hand=frozenset(open_cards+(first,))
            unseen=tuple(c for c in rest if c!=first)
            for prize in combinations(unseen,prizes):
                deck=frozenset(c for c in unseen if c not in prize)
                reached=physical_joint(
                    hand,deck,
                    any(c.startswith("Regidrago:") for c in hand),
                    False,
                )
                for future in deck:
                    exposed=open_cards+(first,future)
                    d=sum(c.startswith("DDE:") for c in exposed)
                    b=sum(c.startswith("Basic Energy:") for c in exposed)
                    v=any(c.startswith("VSTAR:") for c in exposed)
                    material=d>=1 and d+b>=2 and v
                    valid+=1
                    item_count+=int(reached)
                    mat_count+=int(material)
                    joint_count+=int(reached and material)
    return (
        Fraction(item_count,valid),Fraction(mat_count,valid),
        Fraction(joint_count,valid),
    )


def main() -> None:
    configs=(
        (Build(regidrago_v=2,other_basics=1,dragapult=1,vip=1,
               quick_ball=1,treasure=1,compressor=1,total=11),2,1,1,1,1),
        (Build(regidrago_v=2,other_basics=1,dragapult=2,vip=0,
               quick_ball=1,treasure=1,compressor=1,total=11),2,1,1,1,1),
        (Build(regidrago_v=2,other_basics=1,dragapult=1,vip=2,
               quick_ball=1,treasure=1,compressor=1,total=12),3,2,1,1,1),
        (Build(regidrago_v=2,other_basics=1,dragapult=2,vip=1,
               quick_ball=1,treasure=1,compressor=1,total=12),3,2,1,1,1),
    )
    for build,op,pr,dde,basic,vs in configs:
        actual=brute(build,op,pr,dde,basic,vs)
        result=analyze(build,dde,basic,vs,opener=op,prizes=pr)
        assert actual==(result.item_joint,result.energy_and_vstar,
                        result.item_energy_and_vstar), (build,actual,result)
    print("PASS: four independent fully labeled turn/Prize/Item toy oracles")

    baseline=analyze(Build(),4,6,3)
    variant=analyze(Build(dragapult=2,vip=2),4,6,3)
    assert baseline.energy_and_vstar==variant.energy_and_vstar==Fraction(
        76931827,711606090)
    assert baseline.item_energy_and_vstar==Fraction(
        118984284855181,13877478807192000)
    assert variant.item_energy_and_vstar==Fraction(
        951970917996757,75520744044495750)
    assert variant.item_energy_and_vstar-baseline.item_energy_and_vstar==Fraction(
        68199642392807929,16916646665967048000)
    assert baseline.naive_product>baseline.item_energy_and_vstar
    assert variant.naive_product>variant.item_energy_and_vstar
    print("PASS: VSTAR material and Energy single future draw are mutually exclusive")
    print("Published source event:",baseline.item_energy_and_vstar)
    print("Experimental source event:",variant.item_energy_and_vstar)
    print("Experimental delta:",variant.item_energy_and_vstar-baseline.item_energy_and_vstar)
    print("LIMIT: no Mysterious Treasure fetching VSTAR, no attacks or opponent")


if __name__=="__main__":
    main()
