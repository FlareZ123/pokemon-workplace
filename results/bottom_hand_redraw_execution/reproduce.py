"""Exhaustive physical conservation and card-text witnesses for bottom redraws."""
from __future__ import annotations
from collections import Counter
from itertools import permutations
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from bottom_hand_redraw_execution import PlayerZones, execute_bottom_hand_redraw as run


def check():
    number = 0
    for hp in range(4):
        for hq in range(4):
            for dp in range(4):
                for dq in range(3):
                    p = PlayerZones(tuple(f"p{i}" for i in range(dp)),tuple(f"P{i}" for i in range(hp)),6)
                    q = PlayerZones(tuple(f"q{i}" for i in range(dq)),tuple(f"Q{i}" for i in range(hq)),3)
                    for po in permutations(p.hand):
                        for qo in permutations(q.hand):
                            for effect in ("Iono","Marnie","Lucian","Thievul"):
                                coins = [(True,False),(False,True)] if effect == "Lucian" else [None]
                                for flip in coins:
                                    z = run(effect,p,q,player_bottom=po,opponent_bottom=qo,lucian_heads=flip)
                                    assert Counter(z.player.deck+z.player.hand)==Counter(p.deck+p.hand)
                                    assert Counter(z.opponent.deck+z.opponent.hand)==Counter(q.deck+q.hand)
                                    assert z.moved==(hp,hq)
                                    if hp==hq==0: assert z.drawn==(0,0)
                                    else:
                                        request = {"Iono":(6,3),"Marnie":(5,4),"Thievul":(4,4)}.get(effect)
                                        if effect=="Lucian": request=(6 if flip[0] else 3,6 if flip[1] else 3)
                                        assert z.drawn==(min(request[0],dp+hp),min(request[1],dq+hq))
                                    number+=1
                            for chosen in ("player","opponent"):
                                z=run("Kingdra",p,q,player_bottom=po if chosen=="player" else (),
                                      opponent_bottom=qo if chosen=="opponent" else (),chosen=chosen)
                                assert Counter(z.player.deck+z.player.hand)==Counter(p.deck+p.hand)
                                assert Counter(z.opponent.deck+z.opponent.hand)==Counter(q.deck+q.hand)
                                assert z.drawn==(min(4,dp+hp) if chosen=="player" and hp else 0,
                                                 min(4,dq+hq) if chosen=="opponent" and hq else 0)
                                number+=1
                            z=run("Skwovet",p,q,player_bottom=po)
                            assert Counter(z.player.deck+z.player.hand)==Counter(p.deck+p.hand)
                            assert z.opponent==q
                            assert z.drawn==(min(1,dp+hp) if hp else 0,0)
                            number+=1
    # Empty-hand player can draw if other player returned at least one card.
    a=PlayerZones(("a","b"),(),2)
    b=PlayerZones(("c",),("d",),6)
    z=run("Iono",a,b,opponent_bottom=("d",))
    assert z.drawn==(2,2) and z.player.hand==("a","b") and z.opponent.hand==("c","d")
    # Short decks can draw from randomized bottom-returned old hand.
    a=PlayerZones(("a","b"),("x","y","z"),6)
    z=run("Marnie",a,b,player_bottom=("z","x","y"),opponent_bottom=("d",))
    assert z.player.hand==("a","b","z","x","y")
    # A zero-card return makes the conditional draw gate false.
    z=run("Thievul",PlayerZones(("a",),(),1),PlayerZones(("b",),(),1))
    assert z.drawn==(0,0)
    try:
        run("Skwovet",a,b,player_bottom=("x","x","y"))
        assert False
    except ValueError: pass
    try:
        run("Lucian",a,b,player_bottom=("x","y","z"),opponent_bottom=("d",),lucian_heads=(1,False))
        assert False
    except ValueError: pass
    print("Physical-zone/card-text cases:", number, "passed")


if __name__ == "__main__":
    check()
