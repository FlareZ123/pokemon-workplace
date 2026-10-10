"""SFT: physical labeled validation of Tag Call target availability partition."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from aichi_tagcall_target_availability import exact_tagcall_target_partition
from aichi_tagcall_bellelba_ceiling import exact_tagcall_bellelba_fallback


def independent_labeled_targets():
    # J one Basic; other Basic S2; G&H2; Tag Call2; Bellelba1; fillers3.
    pool = ["J"] + ["G"]*2 + ["T"]*2 + ["B"] + ["S"]*2 + ["F"]*3
    total = 0
    classified = Counter()
    for opening in combinations(range(len(pool)), 4):
        if not any(pool[i] in ("J", "S") for i in opening):
            continue
        outside = [i for i in range(len(pool)) if i not in opening]
        for draw in outside:
            exposed = opening + (draw,)
            remaining = [i for i in outside if i != draw]
            for prized in combinations(remaining, 2):
                total += 1
                if pool[0] != "J" or 0 not in opening:
                    continue
                if not (any(pool[i] == "G" for i in exposed)
                        and any(pool[i] == "T" for i in exposed)):
                    continue
                deck = [i for i in remaining if i not in prized]
                classified[(
                    any(pool[i] == "G" for i in deck),
                    any(pool[i] == "B" for i in deck),
                )] += 1
    return {
        key: Fraction(classified[key], total)
        for key in ((False,False),(False,True),(True,False),(True,True))
    }


def main():
    toy = exact_tagcall_target_partition(
        deck_size=11, opener=4, natural_draws=1, prizes=2,
        basics=3, gnh=2, tagcall=2,
    )
    oracle = independent_labeled_targets()
    for g, b, expected in toy.probabilities:
        assert oracle[g,b] == expected
    assert toy.natural_triplet_probability == Fraction(17, 91)
    assert toy.probability(gnh_searchable=False, bellelba_searchable=True) == Fraction(62,1365)
    print("11-card independent physically labeled oracle: PASS")
    print("Tiny partition:", oracle)

    full = exact_tagcall_target_partition()
    assert full.natural_triplet_probability == Fraction(14895153, 734673280)
    assert full.probability(gnh_searchable=False, bellelba_searchable=True) == Fraction(74221,1341841280)
    assert (full.probability(gnh_searchable=False, bellelba_searchable=True)
            == exact_tagcall_bellelba_fallback().accepted_probability)
    print("\nAichi TAG TEAM target availability, among all Basic-valid openers")
    for g, b, p in full.probabilities:
        print("G&H in deck",g,"Bellelba in deck",b,
              "fraction",p, "percentage", f"{float(p*100):.12f}%")
    print("Natural Jirachi/G&H/Tag Call triplet:",
          full.natural_triplet_probability,
          f"{float(full.natural_triplet_probability*100):.12f}%")
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
