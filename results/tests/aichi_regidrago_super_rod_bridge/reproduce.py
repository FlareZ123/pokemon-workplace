"""Independent exhaustive Item/Supporter/manual-attachment route enumerator."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from tools.aichi_regidrago_super_rod_bridge import build, execute_route
from tools.energy_discard_solver import attack_cost_ready


def exhaustive(basic: str, *, prior_fire: int=0, extra_item: bool=False) -> bool:
    hand=Counter({"DDE":1,"Grass":1,"Fire":2-prior_fire})
    deck=Counter({"DDE":2,"Grass":3})
    discarded=Counter({"Fire":prior_fire})
    if hand[basic]==0:
        raise ValueError("Basic unavailable")
    # DDE already attached, normal Basic attachment, copied Trifrost.
    hand[basic]-=1
    discarded[basic]+=1
    discarded["DDE"]+=1
    if extra_item:
        hand["Fire"]-=1
        discarded["Fire"]+=1
    # Independently exhaust every legal choice of 0..3 Basic cards for
    # Super Rod, both possible Crispin Energy roles and manual attachments.
    for rg in range(discarded["Grass"]+1):
        for rf in range(discarded["Fire"]+1):
            if rg+rf>3:
                continue
            available=deck.copy()
            available["Grass"]+=rg
            available["Fire"]+=rf
            if not (available["Grass"] and available["Fire"]):
                continue
            for attach_type,hand_type in (("Grass","Fire"),("Fire","Grass")):
                new_hand=hand.copy()
                new_hand[hand_type]+=1
                for manual in ("DDE","Grass","Fire"):
                    if new_hand[manual]==0:
                        continue
                    providers=[{"units":1,"types":[attach_type]}]
                    if manual=="DDE":
                        providers.append({"units":2,"types":[
                            "Grass","Fire","Water","Lightning","Psychic",
                            "Fighting","Darkness","Metal","Fairy","Colorless"]})
                    else:
                        providers.append({"units":1,"types":[manual]})
                    if attack_cost_ready(providers,["Grass","Grass","Fire"]):
                        return True
    return False


def main() -> None:
    samples=(("Grass",0,False,False),("Fire",0,False,True),
             ("Grass",1,False,True),("Fire",1,False,True),
             ("Grass",0,True,True),("Fire",0,True,True))
    for basic, prior, item, expected in samples:
        source=execute_route(basic,prior_fire_discard=prior,
                             extra_fire_item_payment=item)
        oracle=exhaustive(basic,prior_fire=prior,extra_item=item)
        assert source.apex_ready==oracle==expected
    result=build(Path("."))
    assert result["branches"][0]["apex_ready"] is False
    assert result["branches"][1]["apex_ready"] is True
    print("PASS: six exhaustive Rod/Crispin/attachment control states")
    print(result)


if __name__=="__main__":
    main()
