"""End-to-end physical-order regression for an access-limited Ticket policy."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.prize_ticket_reinspection import analyze_tickets
from tools.prize_ticket_natural_access import analyze_natural_access
from tools.prize_ticket_policy_access import combine_access_and_stopping


def enumerate_physical_game():
    deck = ('A', 'B', 'S0', 'S1', 'T0', 'T1', 'M0', 'M1', 'F0', 'F1')
    joint_total = 0
    witness_total = 0
    joint_success = [0, 0, 0]
    expected_uses_sum = 0
    for hand in combinations(deck, 3):
        if not any(c.startswith('S') for c in hand):
            continue
        after_hand = tuple(c for c in deck if c not in hand)
        for prizes in combinations(after_hand, 2):
            after_prizes = tuple(c for c in after_hand if c not in prizes)
            for drawn in after_prizes:
                residual = tuple(c for c in after_prizes if c != drawn)
                for order in permutations(residual):
                    joint_total += 1
                    if 'A' not in prizes or 'B' not in residual:
                        continue
                    witness_total += 1
                    seen = hand + (drawn,)
                    available_ticket = sum(x.startswith('T') for x in seen)
                    available_map = sum(x.startswith('M') for x in seen)
                    if available_ticket:
                        first_live = 'B' not in order[:2]
                    else:
                        first_live = False
                    second_live = (
                        first_live or (available_ticket >= 2 and available_map >= 1
                                       and 'B' not in order[2:4])
                    )
                    joint_success[1] += first_live
                    joint_success[2] += second_live
                    expected_uses_sum += (
                        int(available_ticket >= 1)
                        + int(available_ticket >= 2 and available_map >= 1 and not first_live)
                    )
    return (
        Fraction(witness_total, joint_total),
        tuple(Fraction(x, joint_total) for x in joint_success),
        Fraction(expected_uses_sum, witness_total),
    )


def main():
    oracle = analyze_tickets((0, 1), (1, 0), (1, 1),
                             deck_size=4, prize_count=2, max_resets=2)
    access = [analyze_natural_access(
        deck_size=10, starters=2, tickets=2, town_maps=2,
        original_prized_singletons=1, original_deck_singletons=1,
        opening_hand=3, prize_cards=2, later_draws=1,
        needed_tickets=k, needed_maps=k-1) for k in (1, 2)]
    composed = combine_access_and_stopping(
        tuple(x.item_access_given_witness for x in access),
        oracle.success_by_limit,
        access[0].witness_probability_given_valid_opening,
    )
    witness, joint_success, uses = enumerate_physical_game()
    assert witness == access[0].witness_probability_given_valid_opening
    assert joint_success == composed.joint_success_by_limit, (joint_success, composed.joint_success_by_limit)
    assert uses == composed.conditional_expected_uses, (uses, composed.conditional_expected_uses)

    large_oracle = analyze_tickets((0, 1, 1), (1, 0, 0), (1, 1, 1),
                                   deck_size=47, prize_count=6, max_resets=3)
    large_access = tuple(analyze_natural_access(
        needed_tickets=k, needed_maps=k-1) for k in (1, 2, 3))
    large = combine_access_and_stopping(
        tuple(x.item_access_given_witness for x in large_access),
        large_oracle.success_by_limit,
        large_access[0].witness_probability_given_valid_opening,
    )
    assert large.conditional_success_by_limit[-1] == Fraction(1090973770532, 3137085268525)
    assert large.conditional_success_by_limit[2] == Fraction(218190842512, 627417053705)
    assert large.conditional_success_by_limit[1] == Fraction(16478932954, 48262850285)
    assert large.conditional_expected_uses <= 1
    print('PASS: complete labeled small-game enum equals independently composed conditional access + sequential Prize transition')
    for k in (1, 2, 3):
        print(f'{k} reset ceiling: conditional policy success {float(large.conditional_success_by_limit[k]):.9%}, '
              f'joint witness + policy success {float(large.joint_success_by_limit[k]):.9%}')
    print(f'expected actual Tickets used per initial witness state: {float(large.conditional_expected_uses):.9f}')


if __name__ == '__main__':
    main()
