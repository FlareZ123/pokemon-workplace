"""Independent labeled opening/Pride enumeration for Basic acceptance."""
from collections import Counter
from fractions import Fraction
from itertools import combinations

from tools.arc_opening_basic_conditioning import exact_accepted
from tools.arc_phone_chain_access import _state_value, exact_access


def labeled_oracle(*, counts, prizes, hand):
    p, a, s, b, f = counts
    pool = (tuple(f'P{i}' for i in range(p))
            + tuple(f'A{i}' for i in range(a))
            + tuple(f'S{i}' for i in range(s))
            + tuple(f'B{i}' for i in range(b))
            + tuple(f'F{i}' for i in range(f)))
    accepted = 0
    summed = Fraction()
    size = 0
    for hidden in combinations(pool, prizes-1):
        prize_cards = ('T0',) + hidden
        remaining = tuple(x for x in pool if x not in hidden)
        for held in combinations(remaining, hand):
            size += 1
            hc = Counter(x[0] for x in held)
            if not hc['B']:
                continue
            accepted += 1
            pc = Counter(x[0] for x in prize_cards)
            prize_state = (pc['T'], pc['P'], pc['A'], pc['S'], pc['B'] + pc['F'])
            hand_state = (0,hc['P'],hc['A'],hc['S'],hc['B'] + hc['F'] - 1)
            summed += _state_value(prize_state,hand_state,True,min(3,prizes),True)
    return Fraction(accepted,size),summed/accepted


def main():
    samples = ((1,2,2,2,4), (1,2,2,3,3), (1,1,2,3,4))
    for counts in samples:
        actual = exact_accepted(other=counts,prize_count=3,opening_size=4)
        independent = labeled_oracle(counts=counts,prizes=3,hand=4)
        assert (actual.acceptance,actual.access_given_accepted) == independent
        print('ORACLE OK', counts, *independent)
    baseline = exact_access(seen=7)
    expected = {
        1: '0.07592762358586176',
        8: '0.08129563012587744',
        50: '0.09106094527453373',
    }
    for b in (1,4,8,12,16,20,30,50):
        actual = exact_accepted(other=(1,4,4,b,50-b))
        assert actual.access_given_accepted <= baseline
        if b in expected:
            assert abs(float(actual.access_given_accepted) - float(expected[b])) < 1e-14
        print('SIXTY',b,round(float(actual.acceptance),8),
              round(float(actual.access_given_accepted),10))
    print('ALL BASIC-CONDITIONING TESTS PASSED')


if __name__ == '__main__':
    main()
