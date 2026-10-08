"""Independent exhaustive check of accepted-opener / exact-K1 Item access."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.prize_ticket_natural_access import analyze_natural_access


def brute(need_tickets: int, need_maps: int):
    labels = ('A', 'B', 'S0', 'S1', 'T0', 'T1', 'M0', 'M1', 'F0', 'F1')
    legal_count = 0
    witness_count = 0
    joint_count = 0
    for hand in combinations(labels, 3):
        if not any(x.startswith('S') for x in hand):
            continue
        unhanded = tuple(x for x in labels if x not in hand)
        for prizes in combinations(unhanded, 2):
            post_prize = tuple(x for x in unhanded if x not in prizes)
            for drawn in post_prize:
                legal_count += 1
                # Original Prized singleton A, original deck singleton B.
                if 'A' not in prizes or 'B' in hand or 'B' in prizes or drawn == 'B':
                    continue
                witness_count += 1
                seen = hand + (drawn,)
                if (sum(x.startswith('T') for x in seen) >= need_tickets and
                    sum(x.startswith('M') for x in seen) >= need_maps):
                    joint_count += 1
    return (Fraction(witness_count, legal_count),
            Fraction(joint_count, witness_count),
            Fraction(joint_count, legal_count))


def main():
    for needed_tickets, needed_maps in ((1, 0), (1, 1), (2, 1), (2, 2)):
        actual = analyze_natural_access(
            deck_size=10, starters=2, tickets=2, town_maps=2,
            original_prized_singletons=1, original_deck_singletons=1,
            opening_hand=3, prize_cards=2, later_draws=1,
            needed_tickets=needed_tickets, needed_maps=needed_maps,
        )
        expected = brute(needed_tickets, needed_maps)
        assert (actual.witness_probability_given_valid_opening,
                actual.item_access_given_witness,
                actual.joint_probability_given_valid_opening) == expected

    one = analyze_natural_access(needed_tickets=1, needed_maps=0)
    two = analyze_natural_access(needed_tickets=2, needed_maps=1)
    three = analyze_natural_access(needed_tickets=3, needed_maps=2)
    expected_witness = Fraction(616121493, 9991556608)
    assert one.witness_probability_given_valid_opening == expected_witness
    assert two.witness_probability_given_valid_opening == expected_witness
    assert three.witness_probability_given_valid_opening == expected_witness
    assert one.item_access_given_witness == Fraction(200962597, 446464850)
    assert two.item_access_given_witness == Fraction(88104758, 2902021525)
    assert three.item_access_given_witness == Fraction(543277, 2902021525)
    assert one.joint_probability_given_valid_opening > two.joint_probability_given_valid_opening > three.joint_probability_given_valid_opening
    print('PASS: exhaustive 10-card placement census at four Item thresholds and independent 60-card rational checks')
    for n, r in ((1, one), (2, two), (3, three)):
        print(f'{n} Tickets and {n-1} Maps: conditional access={float(r.item_access_given_witness):.9%}; '
              f'joint accepted-start mass={float(r.joint_probability_given_valid_opening):.9%}')


if __name__ == '__main__':
    main()
