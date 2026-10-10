"""Independent exhaustive physical labeled opening, Prize, draw verifier."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from bench_draw_energy_tool_bootstrap import analyze  # noqa: E402


def brute(*, deck_size: int = 20, opening_size: int = 7,
          prize_count: int = 2, other_basics: int = 2,
          quick_balls: int = 2, discardable: int = 2,
          energies: int = 2, tools: int = 2):
    counts = [("D",1),("C",1),("K",1),("Q",quick_balls),("F",discardable),
              ("O",other_basics),("E",energies),("T",tools)]
    cards = [(kind,i) for kind,n in counts for i in range(n)]
    cards += [("X",i) for i in range(deck_size-len(cards))]
    all_open = comb(deck_size, opening_size)
    valid = all_open-comb(deck_size-(2+other_basics),opening_size)
    per_open = comb(deck_size-opening_size,prize_count)*(
        deck_size-opening_size-prize_count)
    event_count=0
    d_hit_mass=Fraction(0)
    staged_hit_mass=Fraction(0)
    for op in combinations(cards,opening_size):
        names = [c[0] for c in op]
        if not ("D" in names and "Q" in names and "F" in names
                and "O" in names and "K" not in names and "C" not in names):
            continue
        remain = [c for c in cards if c not in op]
        for prizes in combinations(remain,prize_count):
            if ("C",0) in prizes or ("K",0) in prizes:
                continue
            after_prizes=[c for c in remain if c not in prizes]
            for draw in after_prizes:
                if draw in (("C",0),("K",0)):
                    continue
                final_names = names+[draw[0]]
                if "E" not in final_names or "T" not in final_names:
                    continue
                event_count += 1
                deck_after = [x for x in after_prizes if x != draw]
                # Exhaust every possible rank of K in each shuffled deck.
                d_success = sum(i < 6 for i in range(len(deck_after)))
                d_hit_mass += Fraction(d_success,len(deck_after))
                deck_without_c = [x for x in deck_after if x!=("C",0)]
                a = max(0,8-(opening_size-2))
                s_success = sum(i < a+6 for i in range(len(deck_without_c)))
                staged_hit_mass += Fraction(s_success,len(deck_without_c))
    denominator = valid * per_open
    return (Fraction(valid,all_open),Fraction(event_count,denominator),
            (staged_hit_mass-d_hit_mass)/denominator)


def validate() -> None:
    cases = (
        dict(deck_size=20,opening_size=7,prize_count=2,
             other_basics=2,quick_balls=2,discardable=2,energies=2,tools=2),
        dict(deck_size=21,opening_size=7,prize_count=2,
             other_basics=2,quick_balls=2,discardable=1,energies=2,tools=2),
    )
    for args in cases:
        m=analyze(**args)
        physical=brute(**args)
        assert m.valid_open == physical[0],(args,m,physical)
        assert m.enabling_k_live_given_valid == physical[1],(args,m,physical)
        assert m.bootstrapped_access_gain_given_valid == physical[2],(args,m,physical)
        print("Toy verified",args["deck_size"],"exact event",physical[1],
              "exact improvement",physical[2])

    x=analyze()
    assert x.conditional_k_live_gain == Fraction(8,115)  # 9/45 - 6/46
    print("60-card valid opener",float(x.valid_open))
    print("E+T materials, K+C live conditional on accepted",
          float(x.enabling_k_live_given_valid))
    print("Weighted incremental target access",
          float(x.bootstrapped_access_gain_given_valid))


if __name__ == "__main__":
    validate()
