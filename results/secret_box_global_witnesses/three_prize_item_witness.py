"""Counterexample: Item is necessary with only three alternative Tools Prized.

All three Stealthy Hood are Prized. Counter Gain and *both* Artazon
are initially in the hand and become the only three affordable cards
for Secret Box's mandatory cost. The second discard gate on G&H
then needs Item -> Tag Call as its additional payment source.

This tests the original source planner on a complete physical order.
It is deliberately a constructive witness, not a population estimate.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from aichi_vileplume_secret_box import (
    BASE_DECK, SECRET_BOX_DECK, _raw_state, _state_succeeds,
)
from aichi_secret_box_output_dependencies import _state_succeeds_with_mask

def indices_for(names):
    free=set(range(60))
    result=[]
    for name in names:
        found=next(i for i in sorted(free) if BASE_DECK[i]==name)
        result.append(found)
        free.remove(found)
    return result,free

def main():
    opening_names=(
        "Oddish","Grand Tree","Bunnelby",
        "Technical Machine: Evolution","Technical Machine: Evolution",
        "Counter Gain","Artazon",
    )
    prizes=(
        "Stealthy Hood","Stealthy Hood","Stealthy Hood",
        "Pidgeotto","Gloom","Herdier",
    )
    selected,free=indices_for(opening_names+prizes+("Artazon",))
    opening=selected[:7]
    prize=selected[7:13]
    draw=selected[13]
    order=opening+prize+[draw]+sorted(free)
    assert len(set(order))==len(order)==60
    baseline=_raw_state(BASE_DECK,order)
    box=_raw_state(SECRET_BOX_DECK,order)
    assert baseline is not None and box is not None
    assert baseline[2]==box[2]=="Oddish"
    assert not _state_succeeds(baseline)
    assert _state_succeeds_with_mask(box,15)
    assert not _state_succeeds_with_mask(box,14)
    assert _state_succeeds_with_mask(box,1)
    print("Prizes:",prizes)
    print("Opening:",opening_names)
    print("First natural draw: Artazon")
    print("Grand Tree: false, full Secret Box: true, no-Item: false,")
    print("Item-only: true")
    print("Three-Hood-Prize payment-collision witness passed.")

if __name__=="__main__":
    main()
