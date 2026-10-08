"""Independent labeled physical-card audit: Nest Ball creates a second Tool holder."""
from __future__ import annotations

from itertools import combinations, product
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))

from secret_box_gnh_tool_pipeline import KINDS, counts
from secret_box_nest_ball_bootstrap import (
    nest_ball_tool_bootstrap,minimum_starting_disposables,
)


def literal_oracle(hand_counts, deck_counts, *, holders, basic_count, can_support=True):
    hand = tuple((k,n,"h") for k,v in zip(KINDS,hand_counts) for n in range(v))
    deck = tuple((k,n,"d") for k,v in zip(KINDS,deck_counts) for n in range(v))
    basics = tuple(("Basic",n,"d") for n in range(basic_count))
    goal = {"A","B","S","E"}

    def good(cards,holder_count):
        return holder_count>=2 and goal.issubset({c[0] for c in cards})

    def search(pool,categories):
        possibilities = [(None,) + tuple(c for c in pool if c[0] in cat)
                         for cat in categories]
        for choices in product(*possibilities):
            chosen = tuple(c for c in choices if c is not None)
            if len(chosen)!=len(set(chosen)):
                continue
            used=set(chosen)
            yield chosen,tuple(c for c in pool if c not in used)

    for pay in combinations((c for c in hand if c[0]!="P"),3):
        spent=set(pay)
        held=tuple(c for c in hand if c not in spent)
        for box,remaining in search(deck,({"I"},{"A","B"},{"G"},{"S"})):
            acquired=held+box
            branches=[(acquired,holders)]
            if holders<2 and basics:
                for item in (c for c in acquired if c[0]=="I"):
                    branches.append((tuple(c for c in acquired if c!=item),holders+1))
            for prepared,n_holders in branches:
                if good(prepared,n_holders):
                    return True
                if not can_support:
                    continue
                for supporter in (c for c in prepared if c[0]=="G"):
                    after_g=tuple(c for c in prepared if c!=supporter)
                    for new,_ in search(remaining,({"S"},)):
                        if good(after_g+new,n_holders):
                            return True
                    for pay2 in combinations((c for c in after_g if c[0]!="P"),2):
                        paid=set(pay2)
                        leftovers=tuple(c for c in after_g if c not in paid)
                        for new,_ in search(remaining,({"S"},{"A","B"},{"E"})):
                            if good(leftovers+new,n_holders):
                                return True
    return False


def main():
    frontiers = {
        (2,True,1,1):4,
        (1,True,1,1):5,
        (2,True,2,1):3,
        (1,True,2,0):4,
        (2,False,2,0):4,
        (2,True,1,0):None,
        (2,False,1,1):None,
        (0,True,1,1):None,
    }
    for args,expected in frontiers.items():
        got=minimum_starting_disposables(
            stadiums=args[0],item_available=args[1],
            holders=args[2],searchable_basics=args[3])
        assert got==expected,(args,got,expected)
        print("canonical threshold",args,got)

    checked=0
    for d,i,s,basics,holders,ghand in product(
        (2,3,4), (0,1), (1,2), (0,1), (1,2), (0,1),
    ):
        hand=counts(D=d,G=ghand,P=1)
        deck=counts(I=i,A=1,B=1,G=1-ghand,S=s,E=1)
        for supporter in (False,True):
            predicted=nest_ball_tool_bootstrap(
                hand,deck,initial_holders=holders,
                searchable_basics=basics,
                supporter_available=supporter,
            )
            literal=literal_oracle(
                hand,deck,holders=holders,
                basic_count=basics,can_support=supporter,
            )
            assert predicted==literal,(
                d,i,s,basics,holders,ghand,supporter,predicted,literal
            )
            checked+=1
    assert checked==192
    print("Independent physical labeled Nest Ball oracle:",checked,"PASS")
    print("ALL TESTS PASSED")


if __name__=="__main__":
    main()
