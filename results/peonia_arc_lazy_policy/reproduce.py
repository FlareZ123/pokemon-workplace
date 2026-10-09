"""Independent full deck-permutation Peonia-to-Items oracle."""
from fractions import Fraction
from itertools import combinations

from tools.arc_phone_deck_order_policy import (
    exact_unknown_orders, optimize as full_optimize,
)
from tools.peonia_arc_lazy_policy import evaluate, shuffled_counterfactual


def brute(prizes, deck, arc, shoes, count):
    physical = exact_unknown_orders(prizes, deck)
    if not count:
        return full_optimize(physical, arc, shoes)
    values = []
    for selected in combinations(range(len(prizes)), count):
        miss = [(s,p) for s,p in physical
                if all(s[0][i] != 'T' for i in selected)]
        missmass = sum((p for _,p in miss), Fraction())
        if missmass:
            conditioned = tuple((state,p/missmass) for state,p in miss)
            suffix = full_optimize(conditioned,arc,shoes)
        else:
            suffix = Fraction()
        values.append(1-missmass+missmass*suffix)
    return max(values)


def main():
    cases = (
        (('T','F','F'),('A','S','F'),1,2),
        (('T','F','F'),('A','A','F'),2,2),
        (('T','F','F','F'),('A','S','F'),2,2),
        (('T','F','F','F'),('A','A','S','F'),2,1),
    )
    for prizes, deck, a, s in cases:
        for n in range(0,min(3,len(prizes))+1):
            actual = evaluate(prizes,deck,a,s,n)
            independent = brute(prizes,deck,a,s,n)
            assert actual == independent, (prizes,deck,a,s,n,actual,independent)
        print('PHYSICAL PEONIA MATCH',len(prizes),len(deck),a,s)

    prizes = ('T',) + ('F',)*5
    deck = ('A','A','S','S') + ('F',)*43
    baseline = evaluate(prizes,deck,2,2,0)
    peonia3 = evaluate(prizes,deck,2,2,3)
    counterfactual = shuffled_counterfactual(prizes,deck,2,2,3)
    assert baseline == Fraction(111820,321057)
    assert peonia3 == Fraction(544697,642114)
    assert counterfactual == Fraction(432877,642114)
    assert peonia3-counterfactual == Fraction(55910,321057)
    print('60-CARD COMBINED',baseline,peonia3,counterfactual)
    print('ALL PEONIA POSITION TESTS PASSED')


if __name__ == '__main__':
    main()
