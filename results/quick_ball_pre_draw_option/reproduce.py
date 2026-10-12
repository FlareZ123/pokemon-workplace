"""SFT: independent labeled-card oracle for pre-draw Quick Ball."""
from itertools import combinations
from math import isclose
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from quick_ball_pre_draw_option import opening_option_probability


def oracle(n, p, h, *, s, a, c, g, q, d):
    labels = "C"*c + "G"*g + "L" + "A"*a + "Q"*q + "D"*d + "S"*s
    labels += "F"*(n-len(labels))
    total = wait = eager_a = eager_g = 0.0
    for opening in combinations(range(n), h):
        held = set(opening)
        has = lambda x, cards: any(labels[i] == x for i in cards)
        if not any(labels[i] in "LAS" for i in held):
            continue
        for prize in combinations(sorted(set(range(n))-held), p):
            if not has("C", prize):
                continue
            total += 1
            remaining = set(range(n))-held-set(prize)
            preserved = has("L", held) and (has("A", held) or has("S", held))
            missing_a = not has("A", held)
            missing_g = not has("G", held) and not preserved and not has("L", held)
            payable = has("Q", held) and has("D", held)

            def evaluate(target):
                hand, deck = set(held), set(remaining)
                made_a, made_g = has("A", held), has("G", held)
                if target:
                    hand.remove(next(i for i in hand if labels[i] == "Q"))
                    hand.remove(next(i for i in hand if labels[i] == "D"))
                    matches = sorted(i for i in deck if labels[i] == target)
                    if matches:
                        deck.remove(matches[0])
                        if target == "A":
                            made_a = True
                        else:
                            outs = sorted(i for i in deck if labels[i] == "G")
                            if outs:
                                deck.remove(outs[0])
                                made_g = True
                wins = 0
                for draw in deck:
                    rest = deck-{draw}
                    aa = made_a or labels[draw] == "A"
                    gg = made_g or labels[draw] == "G" or (
                        (preserved or labels[draw] == "L") and has("G", rest)
                    )
                    available_q = sum(labels[i] == "Q" for i in hand) + int(labels[draw] == "Q")
                    available_d = sum(labels[i] == "D" for i in hand) + int(labels[draw] == "D")
                    if min(available_q, available_d) < int(not aa)+int(not gg):
                        continue
                    if not aa and not has("A", rest):
                        continue
                    if not gg and not (has("L", rest) and has("G", rest)):
                        continue
                    wins += 1
                return wins/len(deck)
            wait += evaluate(None)
            eager_a += evaluate(("A" if missing_a else "L" if missing_g else None) if payable else None)
            eager_g += evaluate(("L" if missing_g else "A" if missing_a else None) if payable else None)
    return wait/total, eager_a/total, eager_g/total


def main():
    toys = (
        dict(n=11,p=2,h=4,s=1,a=1,c=2,g=1,q=2,d=2),
        dict(n=12,p=2,h=4,s=2,a=1,c=2,g=2,q=2,d=1),
    )
    for toy in toys:
        exact = opening_option_probability(
            toy["n"], toy["p"], opening_hand_size=toy["h"],
            other_starters=toy["s"], attacker_starter_copies=toy["a"],
            critical_nonstarter=toy["c"], rescue_nonstarter=toy["g"],
            quick_ball_copies=toy["q"], disposable_nonstarter=toy["d"],
        )
        brute = oracle(**toy)
        computed = (
            exact.wait_joint, exact.eager_attacker_joint, exact.eager_rescue_joint
        )
        assert all(isclose(x, y, abs_tol=5e-12) for x,y in zip(computed,brute))
        print("physical oracle passed", toy, brute)

    for d in (4,8,12,16,20,24):
        r = opening_option_probability(
            60,6,other_starters=10,attacker_starter_copies=1,
            critical_nonstarter=4,rescue_nonstarter=2,
            quick_ball_copies=4,disposable_nonstarter=d
        )
        assert r.wait_joint + 1e-12 >= max(
            r.eager_attacker_joint, r.eager_rescue_joint
        )
        if d == 12:
            assert abs(r.wait_joint-0.1775536858681557)<1e-12
        print(d, r)


if __name__ == "__main__":
    main()
