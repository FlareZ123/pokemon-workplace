"""Basic Energy hand/deck/discard frontier for Aichi Rod+Crispin recovery.

This counts distinct *type compositions*, not game frequencies.
Both types are held before one is attached and Trifrost discards it.
Super Rod can return up to 3 Basic cards and Crispin can attach one
from a two-type search; one hand DDE pays the manual attachment.
No other discard outlet, opponent response or search is modeled.
"""
from __future__ import annotations

import json
from collections import Counter
from typing import Any

from tools.energy_discard_solver import attack_cost_ready

DDE_TYPES = ["Grass","Fire","Water","Lightning","Psychic",
             "Fighting","Darkness","Metal","Fairy","Colorless"]


def partitions(count: int):
    """Every physically possible (hand, deck, discard) split with hand >=1."""
    for held in range(1, count+1):
        for in_deck in range(count-held+1):
            yield (held, in_deck, count-held-in_deck)


def theorem(grass: tuple[int,int,int],fire: tuple[int,int,int],chosen: str) -> bool:
    """Both Basic types must remain accessible from deck/discard after payment."""
    if chosen not in ("Grass","Fire"):
        raise ValueError("Unknown payment")
    return (grass[1]+grass[2]+int(chosen=="Grass")>0 and
            fire[1]+fire[2]+int(chosen=="Fire")>0)


def independent_oracle(grass: tuple[int,int,int],fire: tuple[int,int,int],chosen: str) -> bool:
    """Exhaust Super Rod Basic returns and Crispin possible attachment roles."""
    held={"Grass":grass[0],"Fire":fire[0]}
    deck={"Grass":grass[1],"Fire":fire[1]}
    discarded={"Grass":grass[2],"Fire":fire[2]}
    if held[chosen] < 1:
        raise ValueError("Unavailable Basic")
    held[chosen] -= 1
    discarded[chosen] += 1
    for rg in range(discarded["Grass"]+1):
        for rf in range(discarded["Fire"]+1):
            if rg+rf>3:
                continue
            if deck["Grass"]+rg == 0 or deck["Fire"]+rf == 0:
                continue
            for crispin_attached in ("Grass","Fire"):
                if attack_cost_ready([
                    {"types":[crispin_attached],"units":1},
                    {"types":DDE_TYPES,"units":2}],
                    ["Grass","Grass","Fire"]):
                    return True
    return False


def analytic_counts(grass_total: int,fire_total: int) -> dict[str,int]:
    if min(grass_total,fire_total)<1:
        raise ValueError("Require at least one held Basic of each type")
    a=grass_total*(grass_total+1)//2
    b=fire_total*(fire_total+1)//2
    return {"both":(a-1)*(b-1),"fire_only":a-1,
            "grass_only":b-1,"neither":1}


def classify(g: tuple[int,int,int],f: tuple[int,int,int]) -> str:
    grass=theorem(g,f,"Grass")
    fire=theorem(g,f,"Fire")
    return "both" if grass and fire else "grass_only" if grass else "fire_only" if fire else "neither"


def build() -> dict[str,Any]:
    counts=Counter()
    witnesses={}
    checks=0
    for g in partitions(4):
        for f in partitions(2):
            for selected in ("Grass","Fire"):
                assert theorem(g,f,selected)==independent_oracle(g,f,selected)
                checks+=1
            label=classify(g,f)
            counts[label]+=1
            witnesses.setdefault(label,{"grass_hand_deck_discard":g,
                                         "fire_hand_deck_discard":f})
    assert checks==60
    assert counts==Counter({"both":18,"fire_only":9,"grass_only":2,"neither":1})
    assert counts==Counter(analytic_counts(4,2))
    for cg in range(1,7):
        for cf in range(1,7):
            distribution=Counter(classify(g,f) for g in partitions(cg) for f in partitions(cf))
            assert distribution==Counter(analytic_counts(cg,cf))
    return {"source_basic_counts":{"Grass":4,"Fire":2},
            "distinct_type_zone_allocations":30,
            "branch_checks_with_independent_oracle":checks,
            "classification":dict(counts),
            "representative_states":witnesses,
            "general_closed_form_verified_on":36,
            "scope":"Unweighted symbolic hand/deck/discard partitions; no gameplay frequency"}


if __name__=="__main__":
    print(json.dumps(build(),indent=2))
