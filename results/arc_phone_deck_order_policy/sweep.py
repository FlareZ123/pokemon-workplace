"""Exhaustive small-state sensitivity sweep under four-copy Item limits."""
from collections import Counter
from fractions import Fraction
from itertools import combinations_with_replacement

from tools.arc_phone_deck_order_policy import exact_unknown_orders, optimize
from results.arc_phone_deck_order_policy.reproduce import oracle


EXPECTED = {
    2: (164, 6, Fraction(1, 6)),
    3: (251, 22, Fraction(1, 9)),
    4: (305, 35, Fraction(1, 12)),
}


def scan(prize_count):
    scenarios = []
    for other_prizes in combinations_with_replacement('ASF', prize_count - 1):
        prizes = ('T',) + other_prizes
        for deck in combinations_with_replacement('ASF', 3):
            prior = exact_unknown_orders(prizes, deck)
            supply = Counter(prizes + deck)
            for arc in (1, 2, 3):
                for shoes in (1, 2, 3):
                    if supply['A'] + arc > 4 or supply['S'] + shoes > 4:
                        continue
                    take_only = optimize(prior, arc, shoes, False)
                    full = optimize(prior, arc, shoes, True)
                    scenarios.append((full - take_only, prizes, deck, arc,
                                      shoes, take_only, full))
    return scenarios


def main():
    for prize_count, (count, positive, maximum) in EXPECTED.items():
        rows = scan(prize_count)
        gainful = [r for r in rows if r[0] > 0]
        observed = max(r[0] for r in rows)
        assert (len(rows), len(gainful), observed) == (count, positive, maximum)
        print('SWEEP', prize_count, 'tested', len(rows),
              'improved', len(gainful), 'maxgain', observed)

        # Independently enumerate every labeled world for the maximizers.
        witnesses = [r for r in rows if r[0] == maximum]
        for gain, prizes, deck, a, s, base, full in witnesses:
            from itertools import permutations
            worlds = tuple((p,d) for p in sorted(set(permutations(prizes)))
                                 for d in sorted(set(permutations(deck))))
            assert base == oracle(worlds, a, s, False)
            assert full == oracle(worlds, a, s, True)
        print('MAXIMIZERS independently checked', len(witnesses))
    print('ALL SWEEP TESTS PASSED')


if __name__ == '__main__':
    main()
