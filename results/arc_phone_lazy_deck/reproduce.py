"""Crosscheck deck-tail factorization against fully permuted physical decks."""
from collections import Counter, defaultdict
from fractions import Fraction

from tools.arc_phone_deck_order_policy import (
    arc_swap as full_swap, draw as full_draw,
    exact_unknown_orders, optimize as full_optimize,
)
from tools.arc_phone_lazy_deck import (
    GROUPS, advance, initial, normalize, optimize, swap,
)


def project(physical):
    collapsed = defaultdict(Fraction)
    for (prizes, deck), p in physical:
        top = deck[0] if deck else None
        tail = Counter(deck[1:])
        signature = (prizes, top, tuple(tail[g] for g in GROUPS))
        collapsed[signature] += p
    return normalize(collapsed)


def main():
    checks = (
        (('T','A','F'),('A','S','F'),1,2),
        (('T','F'),('A','A','F'),1,2),
        (('T','F','F'),('A','A','F'),2,2),
        (('T','A','S','F'),('A','S','F'),3,2),
    )
    for prizes, deck, a, s in checks:
        physical = exact_unknown_orders(prizes, deck)
        compressed = initial(prizes, deck)
        assert project(physical) == compressed
        assert project(full_draw(physical,1)) == advance(compressed)
        assert project(full_draw(physical,2)) == advance(advance(compressed))
        for slot in range(len(prizes)):
            assert project(full_swap(physical,slot)) == swap(compressed,slot)
        for discard in (False,True):
            exact = full_optimize(physical,a,s,discard)
            compact = optimize(compressed,a,s,discard)
            assert exact == compact, (prizes,deck,a,s,discard,exact,compact)
        print('PHYSICAL MATCH',len(prizes),len(deck),a,s)

    # Six Prizes, 47 deck cards, seven opening cards: 1 Basic Active,
    # 2 Arc and 2 Shoes plus 2 filler in hand; T is among Prizes.
    prizes = ('T',)+('F',)*5
    deck = ('A','A','S','S')+('F',)*43
    state = initial(prizes,deck)
    assert len(state) == 18
    base = optimize(state,2,2,False)
    full = optimize(state,2,2,True)
    assert base == Fraction(46,135)
    assert full == Fraction(111820,321057)
    assert full > base
    print('60-CARD SNAPSHOT',base,full,'gain',full-base)
    print('ALL FACTORIZATION TESTS PASSED')


if __name__ == '__main__':
    main()
