"""Physical proof-of-existence: Item necessity with only two key
Tool/Artazon cards Prized, provided the second TM Evolution is Prized.

All four unprized non-TM Tool/Stadium sources begin in hand and must
service the Secret Box three-card pre-search payment. One remains, which
cannot fund the separate G&H two-card payment without Item -> Tag Call.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from aichi_vileplume_secret_box import (
    BASE_DECK,SECRET_BOX_DECK,_raw_state,_state_succeeds,
)
from aichi_secret_box_output_dependencies import _state_succeeds_with_mask

def build(prizes,opening,draw):
    remaining=set(range(60))
    def pull(name):
        i=next(x for x in sorted(remaining) if BASE_DECK[x]==name)
        remaining.remove(i)
        return i
    # Choose Prizes first so that a specific scarce TM and both Hood are
    # physically distinct from required held copies.
    p=[pull(n) for n in prizes]
    o=[pull(n) for n in opening]
    d=pull(draw)
    order=o+p+[d]+sorted(remaining)
    assert len(order)==len(set(order))==60
    return order

def main():
    prizes=(
        "Stealthy Hood","Stealthy Hood",
        "Technical Machine: Evolution",
        "Pidgeotto","Gloom","Herdier",
    )
    opening=(
        "Oddish","Grand Tree","Bunnelby",
        "Technical Machine: Evolution","Stealthy Hood",
        "Counter Gain","Artazon",
    )
    draw="Artazon"
    order=build(prizes,opening,draw)
    b=_raw_state(BASE_DECK,order)
    s=_raw_state(SECRET_BOX_DECK,order)
    assert b is not None and s is not None
    assert b[2]==s[2]=="Oddish"
    baseline=_state_succeeds(b)
    full=_state_succeeds_with_mask(s,15)
    disabled=_state_succeeds_with_mask(s,14)
    item_only=_state_succeeds_with_mask(s,1)
    print("prizes",prizes)
    print("opener",opening,"first draw",draw)
    print("Grand Tree",baseline,"full Box",full,
          "Box without Item",disabled,"Item-only Box",item_only)
    assert (baseline,full,disabled,item_only)==(False,True,False,True)
    print("Two-key-Prize Item indispensability established.")

if __name__=="__main__":
    main()
