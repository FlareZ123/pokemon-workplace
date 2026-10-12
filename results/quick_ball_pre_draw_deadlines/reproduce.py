"""SFT: labeled-card validation of Quick Ball early deadlines."""
from itertools import combinations
from math import isclose
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from quick_ball_pre_draw_deadlines import deadline_joint_probability
from quick_ball_pre_draw_option import opening_option_probability


def oracle(n, p, h, *, s, a, c, g, q, d):
    labels = "C"*c+"G"*g+"L"+"A"*a+"Q"*q+"D"*d+"S"*s
    labels += "F"*(n-len(labels))
    has = lambda x, cards: any(labels[i] == x for i in cards)
    counts = [0.0,0.0,0.0,0.0]
    for opening in combinations(range(n),h):
        hand = set(opening)
        if not any(labels[i] in "LAS" for i in hand):
            continue
        for prize in combinations(sorted(set(range(n))-hand),p):
            if not has("C",prize):
                continue
            pack = set(range(n))-hand-set(prize)
            counts[0] += 1
            preserved = has("L",hand) and (
                has("A",hand) or has("S",hand)
            )
            payable = has("Q",hand) and has("D",hand)

            def chance(search=None, free_lele=False):
                held, deck = set(hand), set(pack)
                a_done, g_done = has("A",hand),has("G",hand)
                if free_lele:
                    held.remove(next(i for i in held if labels[i]=="L"))
                    found = next(i for i in sorted(deck) if labels[i]=="G")
                    deck.remove(found)
                    g_done=True
                if search:
                    held.remove(next(i for i in held if labels[i]=="Q"))
                    held.remove(next(i for i in held if labels[i]=="D"))
                    target = next((i for i in sorted(deck) if labels[i]==search),None)
                    if target is not None:
                        deck.remove(target)
                        if search=="A":
                            a_done=True
                        else:
                            found=next((i for i in sorted(deck) if labels[i]=="G"),None)
                            if found is not None:
                                deck.remove(found)
                                g_done=True

                good=0
                for drawn in deck:
                    unknown=deck-{drawn}
                    active=a_done or labels[drawn]=="A"
                    rescue=g_done or labels[drawn]=="G" or (
                        (preserved and not free_lele or labels[drawn]=="L")
                        and has("G",unknown)
                    )
                    q_left=sum(labels[i]=="Q" for i in held)+int(labels[drawn]=="Q")
                    d_left=sum(labels[i]=="D" for i in held)+int(labels[drawn]=="D")
                    if min(q_left,d_left)<int(not active)+int(not rescue):
                        continue
                    if not active and not has("A",unknown):
                        continue
                    if not rescue and not (
                        has("L",unknown) and has("G",unknown)
                    ):
                        continue
                    good+=1
                return good/len(deck)

            counts[1]+=chance()
            if has("A",hand):
                counts[2]+=chance()
            elif payable and has("A",pack):
                counts[2]+=chance("A")

            if has("G",hand):
                counts[3]+=chance()
            elif preserved and has("G",pack):
                counts[3]+=chance(free_lele=True)
            elif payable and has("L",pack) and has("G",pack):
                counts[3]+=chance("L")

    return tuple(value/counts[0] for value in counts)


def main():
    for toy in (
        dict(n=11,p=2,h=4,s=1,a=1,c=2,g=1,q=2,d=2),
        dict(n=12,p=2,h=4,s=2,a=1,c=2,g=2,q=2,d=1),
    ):
        exact=deadline_joint_probability(
            toy["n"],toy["p"],opening_hand_size=toy["h"],
            other_starters=toy["s"],attacker_starter_copies=toy["a"],
            critical_nonstarter=toy["c"],rescue_nonstarter=toy["g"],
            quick_ball_copies=toy["q"],disposable_nonstarter=toy["d"]
        )
        labeled=oracle(**toy)
        assert all(isclose(a,b,abs_tol=1e-12) for a,b in
                   zip(exact.__dict__.values(),labeled)),(toy,exact,labeled)
        print("Labeled deadline oracle passed:",toy,labeled)

    for d in (4,8,12,16,20,24):
        options=dict(other_starters=10,attacker_starter_copies=1,
                     critical_nonstarter=4,rescue_nonstarter=2,
                     quick_ball_copies=4,disposable_nonstarter=d)
        exact=deadline_joint_probability(60,6,**options)
        baseline=opening_option_probability(60,6,**options)
        assert abs(exact.both_after_draw-baseline.wait_joint)<1e-12
        assert exact.both_after_draw>=max(
            exact.attacker_before_draw,exact.rescue_before_draw
        )
        if d==12:
            assert abs(exact.attacker_before_draw-0.1563733064026412)<1e-12
            assert abs(exact.rescue_before_draw-0.15876091614115836)<1e-12
        print("Disposable",d,"conditional probabilities",exact)


if __name__=="__main__":
    main()
