"""Independent uniform labeled-world oracle for the finite deck/Prize policy."""
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import permutations

from tools.arc_phone_deck_order_policy import exact_unknown_orders, optimize


@lru_cache(None)
def oracle(worlds, arc, shoes, discard):
    if not worlds[0][1] or not (arc or shoes):
        return Fraction()
    seen = defaultdict(list)
    for world in worlds:
        seen[world[1][0]].append(world)
    values = [Fraction()]
    if arc:
        result = Fraction()
        for same_top in seen.values():
            options = [oracle(tuple(same_top), arc - 1, shoes, discard)]
            for slot in range(len(same_top[0][0])):
                after = []
                for prizes, deck in same_top:
                    p = prizes[:slot] + (deck[0],) + prizes[slot+1:]
                    d = (prizes[slot],) + deck[1:]
                    after.append((p, d))
                options.append(oracle(tuple(after), arc - 1, shoes, discard))
            result += Fraction(len(same_top), len(worlds)) * max(options)
        values.append(result)
    if shoes:
        result = Fraction()
        for top, same_top in seen.items():
            kept = Fraction(1) if top == 'T' else oracle(
                tuple((p, d[1:]) for p, d in same_top),
                arc + (top == 'A'), shoes - 1 + (top == 'S'), discard)
            if discard and len(same_top[0][1]) >= 2:
                candidates = defaultdict(list)
                for world in same_top:
                    candidates[world[1][1]].append(world)
                other = Fraction()
                for drawn, group in candidates.items():
                    answer = Fraction(1) if drawn == 'T' else oracle(
                        tuple((p, d[2:]) for p, d in group),
                        arc + (drawn == 'A'), shoes - 1 + (drawn == 'S'), discard)
                    other += Fraction(len(group), len(same_top)) * answer
                kept = max(kept, other)
            result += Fraction(len(same_top), len(worlds)) * kept
        values.append(result)
    return max(values)


def test():
    fixtures = [
        (('T','A','F'),('A','S','F'),1,2,Fraction(1,18)),
        (('T','S','F'),('A','S','F'),1,2,Fraction(1,18)),
        (('T','A','S'),('A','S','F'),1,2,0),
        (('T','A','F'),('A','S','F'),2,1,0),
        (('T','A','S'),('A','S','F'),2,1,0),
        (('T','S','F'),('A','A','F'),1,1,0),
        (('T','A','F'),('F','S','F'),2,1,0),
        (('T','A','S','F'),('A','S','F'),2,2,Fraction(1,24)),
        (('T','A','S','F'),('A','S','F'),3,2,Fraction(1,36)),
        (('T','A','A'),('S','S','F'),1,1,0),
    ]
    for prizes, deck, a, s, gain in fixtures:
        belief = exact_unknown_orders(prizes, deck)
        worlds = tuple((p,d) for p in sorted(set(permutations(prizes)))
                             for d in sorted(set(permutations(deck))))
        base = optimize(belief,a,s,False)
        full = optimize(belief,a,s,True)
        assert base == oracle(worlds,a,s,False)
        assert full == oracle(worlds,a,s,True)
        assert full - base == gain
        print('OK', prizes, deck, a, s, base, full)
    print('ALL TESTS PASSED')


if __name__ == '__main__':
    test()
