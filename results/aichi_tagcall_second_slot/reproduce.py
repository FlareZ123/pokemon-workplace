"""SFT: Bellelba as the second paid Tag Call target in Aichi."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from aichi_tagcall_target_availability import exact_tagcall_target_partition


def toy_counts():
    pool = ["J"] + ["G"]*2 + ["T"]*2 + ["B"] + ["S"]*2 + ["F"]*3
    totals = Counter()
    denominator = 0
    for opener in combinations(range(len(pool)), 4):
        if not any(pool[i] in ("J", "S") for i in opener):
            continue
        rest = [i for i in range(len(pool)) if i not in opener]
        for draw in rest:
            visible = opener + (draw,)
            rest_after_draw = [i for i in rest if i != draw]
            for prizes in combinations(rest_after_draw, 2):
                denominator += 1
                if (0 not in opener or
                    not any(pool[i] == "G" for i in visible) or
                    not any(pool[i] == "T" for i in visible)):
                    continue
                searchable = [i for i in rest_after_draw if i not in prizes]
                g_count = sum(pool[i] == "G" for i in searchable)
                b_count = sum(pool[i] == "B" for i in searchable)
                totals[(g_count,b_count)] += 1
    return {key: Fraction(v,denominator) for key,v in totals.items()}


def main():
    toy = exact_tagcall_target_partition(
        deck_size=11, opener=4, natural_draws=1, prizes=2,
        basics=3, gnh=2, tagcall=2,
    )
    oracle = toy_counts()
    for g,b,p in toy.count_probabilities:
        assert oracle[(g,b)] == p
    print("Independent labeled 11-card target-count census:",oracle,"PASS")

    x = exact_tagcall_target_partition()
    g1_b1 = x.count_probability(gnh_count=1,bellelba_count=1)
    b_only = x.count_probability(gnh_count=0,bellelba_count=1)
    bonus = g1_b1+b_only
    assert g1_b1 == Fraction(66550477,64945117952)
    assert b_only == Fraction(74221,1341841280)
    assert bonus == Fraction(350713867,324725589760)
    assert sum((p for _,_,p in x.count_probabilities),Fraction(0)) == x.natural_triplet_probability
    for g,b,p in x.count_probabilities:
        print("G&H deck copies",g,"Bellelba",b,":",p,f"{float(p*100):.12f}%")
    print("\nBellelba extends 2-card Tag Call stock",bonus,
          f"{float(bonus*100):.12f}% accepted")
    print("Second-card only (exactly 1 G&H left)",g1_b1,
          f"{float(g1_b1*100):.12f}% accepted")
    print("First-card-only Bellelba fallback",b_only,
          f"{float(b_only*100):.12f}% accepted")
    print("Second-card fraction of natural triplets",
          f"{float(g1_b1/x.natural_triplet_probability*100):.9f}%")
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
