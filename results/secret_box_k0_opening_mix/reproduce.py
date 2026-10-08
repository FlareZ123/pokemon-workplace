"""SFT: exact hand mixture, checked by independent labeled opening enumeration."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from secret_box_gnh_tool_pipeline import counts
from secret_box_k0_opening_mix import opening_hand_distribution, average_box_payment_policy


def labeled_opening_distribution(deck, starter_count, hand_size):
    """Enumerate labeled opening subsets and turn-start draw positions."""
    cards = []
    for kind, n in zip(("D","I","A","B","G","S","E"), deck[:-1]):
        cards.extend((kind, i) for i in range(n))
    cards.extend(("starter", i) for i in range(starter_count))
    cards.extend(("protected", i) for i in range(deck[-1]-starter_count))
    indices = tuple(range(len(cards)))
    frequencies = Counter()
    total = 0
    for opener in combinations(indices, hand_size-1):
        if not any(cards[i][0] == "starter" for i in opener):
            continue
        held = set(opener)
        for draw in indices:
            if draw in held:
                continue
            shown = Counter(
                ("P" if cards[i][0] in ("starter","protected") else cards[i][0])
                for i in opener+(draw,)
            )
            frequencies[counts(**shown)] += 1
            total += 1
    return dict(frequencies), total


def main():
    small = counts(D=4,I=1,A=1,B=1,G=1,S=1,E=1,P=3)
    category, denominator = opening_hand_distribution(
        small, basic_starters=2, opening_hand_size=5,
    )
    literal, total = labeled_opening_distribution(small, 2, 5)
    assert denominator == total == 3465
    assert category == literal
    assert len(category) == 121
    print("Independent labeled accepted-opening and draw: 121 states, 3465 weighted orders PASS")

    big = counts(D=20,I=1,A=2,B=1,G=2,S=2,E=1,P=30)
    result = average_box_payment_policy(big,basic_starters=12)
    assert result.clairvoyant_success == Fraction(212294030549929,617187111967426)
    assert result.k0_success == Fraction(211843556807353,617187111967426)
    assert result.information_gap == Fraction(1575083016,2157996894991)
    assert result.gap_visible_hand_mass == Fraction(21389344,1818954753)
    assert (result.visible_state_count,result.gap_state_count) == (548,10)
    assert result.clairvoyant_success >= result.k0_success
    print("Conditional Box in valid opening + one turn draw + 6 Prizes:")
    print(" clairvoyant:",result.clairvoyant_success,float(result.clairvoyant_success))
    print(" nonanticipating:",result.k0_success,float(result.k0_success))
    print(" optimism gap:",result.information_gap,float(result.information_gap))
    print(" gap-bearing visible hand probability:",float(result.gap_visible_hand_mass))
    print(" ALL TESTS PASSED")


if __name__ == "__main__":
    main()
