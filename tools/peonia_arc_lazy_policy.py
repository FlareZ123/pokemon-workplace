"""Peonia-first exact position reveal joined to compact Arc/Shoes deck policy.

Only modeled Prize groups are T and filler. The player has a spare filler
in hand, so retaining T from the Peonia selection is always affordable.
Other drawn Prize fillers are returned to the same physical positions.
"""
from fractions import Fraction
from itertools import combinations

from tools.arc_phone_lazy_deck import initial, normalize, optimize


def evaluate(prizes, deck, arc, shoes, selections=3, allow_discard=True):
    """Target found via Peonia or subsequent Arc/Shoes before resources run out."""
    start = initial(tuple(prizes), tuple(deck))
    size = len(prizes)
    if prizes.count('T') != 1 or any(c != 'F' for c in prizes if c != 'T'):
        raise ValueError('one target and filler Prizes required')
    if not 0 <= selections <= min(3, size):
        raise ValueError('Peonia may choose up to three Prizes')
    baseline = optimize(start, arc, shoes, allow_discard)
    if not selections:
        return baseline
    best = Fraction()
    for chosen in combinations(range(size), selections):
        missing = {
            state: p for state, p in start
            if not any(state[0][i] == 'T' for i in chosen)
        }
        miss_chance = sum(missing.values(), Fraction())
        if miss_chance:
            continuation = optimize(normalize(missing), arc, shoes, allow_discard)
        else:
            continuation = Fraction()
        best = max(best, Fraction(1) - miss_chance + miss_chance * continuation)
    return best


def shuffled_counterfactual(prizes, deck, arc, shoes, selections=3):
    """Counterfactual randomizes Prize positions after Peonia misses."""
    base = optimize(initial(tuple(prizes), tuple(deck)), arc, shoes)
    n = len(prizes)
    return Fraction(selections, n) + Fraction(n-selections,n)*base
