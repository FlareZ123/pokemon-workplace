"""Independent physical projection oracle for both five-Prize Item tails.

For two physically forced sets of five non-TM Tool/Artazon Prizes,
sample each sixth non-forbidden Prize uniformly, shuffle the other 54
individual card IDs, and accept Basic-valid seven-card starts.

Compare the grouped exact model's baseline/15/14 Boolean results against
the original _raw_state/_state_succeeds on the *same physical permutation*.
Jirachi uses the actually seen top five rather than an inferred distribution.
"""
from collections import Counter
from pathlib import Path
import random
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parents[1]/"tools"))

from aichi_vileplume_secret_box import (
    BASE_DECK, SECRET_BOX_DECK, _raw_state, _state_succeeds,
)
from aichi_secret_box_output_dependencies import _state_succeeds_with_mask
from aichi_vileplume_als import BASICS
from five_prize_item_frontier import (
    FULL,TOOL,STADIUM,GNH,TAG,TM,JET,ACE,BUN,FAN,JIR,BASIC,
    SUPPORT,TAG_OTHER,SPECIAL_OTHER,FILLER,
    mkstate,
)
from complete_five_prize_item_frontier import (
    top_masks,outcomes_for_stellar,convert_baseline,
)
from aichi_vileplume_secret_box import _core_possible

GROUPS={
    "Guzma & Hala":GNH,
    "Tag Call":TAG,
    "Technical Machine: Evolution":TM,
    "Jet Energy":JET,
    "Grand Tree":ACE,
    "Secret Box":ACE,
    "Bunnelby":BUN,
    "Fan Rotom":FAN,
    "Jirachi":JIR,
    "Bellelba & Brycen-Man":TAG_OTHER,
    "Artazon":STADIUM,
    "Stealthy Hood":TOOL,
    "Counter Gain":TOOL,
    "Capture Energy":SPECIAL_OTHER,
    "Memory Energy":SPECIAL_OTHER,
    **{n:SUPPORT for n in (
        "Guzma","Cassius","Karen","Plumeria","Gladion",
        "Faba","Lusamine","Peonia","Team Yell's Cheer"
    )},
}
STELLAR_BIT={
    "Guzma & Hala":1,"Tag Call":2,"Technical Machine: Evolution":4,
    "Artazon":8,"Secret Box":16,
}

def role(name):
    if name in GROUPS:
        return GROUPS[name]
    return BASIC if name in BASICS else FILLER

def physical_order(rng,fixed,forbidden):
    free=set(range(60))-set(fixed)
    options=sorted(free-set(forbidden))
    sixth=rng.choice(options)
    prize=list(fixed)+[sixth]
    pool=sorted(set(range(60))-set(prize))
    while True:
        rng.shuffle(pool)
        if any(BASE_DECK[i] in BASICS for i in pool[:7]):
            break
    rng.shuffle(prize)
    return tuple(pool[:7]+prize+pool[7:])

def main(trials_per_family=14_000):
    rng=random.Random(20261010)
    tool_ids=[i for i,n in enumerate(BASE_DECK)
              if n in ("Stealthy Hood","Counter Gain")]
    art_ids=[i for i,n in enumerate(BASE_DECK) if n=="Artazon"]
    assert len(tool_ids)==4 and len(art_ids)==2
    families=(
        ("one_artazon",(*tool_ids,art_ids[0]),(art_ids[1],)),
        ("one_other_tool",(*tool_ids[:3],*art_ids),(tool_ids[3],)),
    )
    for label,fixed,forbidden in families:
        hits=0
        jirachi_stellar=0
        for i in range(trials_per_family):
            order=physical_order(rng,fixed,forbidden)
            original_base=_raw_state(BASE_DECK,order)
            original_box=_raw_state(SECRET_BOX_DECK,order)
            assert original_base is not None and original_box is not None
            prized=tuple(Counter(role(BASE_DECK[x]) for x in order[7:13])[j]
                         for j in range(15))
            pool=tuple(a-b for a,b in zip(FULL,prized))
            opening=tuple(Counter(role(BASE_DECK[x]) for x in order[:7])[j]
                          for j in range(15))
            draw=role(BASE_DECK[order[13]])
            active=original_box[2]
            grouped_active=("jirachi" if active=="Jirachi"
                            else "fan" if active=="Fan Rotom"
                            else "bunnelby" if active=="Bunnelby"
                            else "basic")
            full=_state_succeeds_with_mask(original_box,15)
            without=_state_succeeds_with_mask(original_box,14)
            base=_state_succeeds(original_base)
            if grouped_active=="jirachi":
                topmask=0
                for ix in order[14:19]:
                    topmask |= STELLAR_BIT.get(SECRET_BOX_DECK[ix],0)
                full_only,incremental,held=outcomes_for_stellar(
                    pool,opening,draw,topmask
                )
                assert full_only==(full and not without),(
                    label,i,opening,draw,topmask,full_only,full,without
                )
                assert incremental==(full and not without and not base)
                jirachi_stellar+=int(not held and bool(topmask&16))
            else:
                s=mkstate(pool,opening,draw,grouped_active)
                assert _core_possible(s,15)==full,(label,i,"full")
                assert _core_possible(s,14)==without,(label,i,"no_item")
                assert _core_possible(convert_baseline(s),15)==base,(
                    label,i,"baseline"
                )
            hits+=int(full and not without and not base)
            if i%5000==0:
                print(label,"verified",i,"hits",hits,flush=True)
        print(label,"validated",trials_per_family,
              "physical permutations, positive hits",hits,
              "Jirachi ACE top-five observations",jirachi_stellar)
    print("Both physical five-Prize projection oracles passed.")

if __name__=="__main__":
    main()
