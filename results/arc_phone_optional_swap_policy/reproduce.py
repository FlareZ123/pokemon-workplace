"""Independent physical-world tests for the Arc Phone optional-exchange branch."""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations_with_replacement, permutations

from tools.arc_phone_optional_swap_policy import compare


@lru_cache(None)
def forced_oracle(worlds, arc, shoes):
    if not worlds[0][1] or not (arc or shoes):
        return Fraction()
    groups = defaultdict(list)
    for w in worlds:
        groups[w[1][0]].append(w)
    actions = [Fraction()]
    if arc:
        value = Fraction()
        for cases in groups.values():
            branches = []
            for slot in range(len(cases[0][0])):
                next_worlds = []
                for p, d in cases:
                    next_worlds.append(
                        (p[:slot] + (d[0],) + p[slot+1:],
                         (p[slot],) + d[1:]))
                branches.append(forced_oracle(tuple(next_worlds), arc-1, shoes))
            value += Fraction(len(cases), len(worlds)) * max(branches)
        actions.append(value)
    if shoes:
        value = Fraction()
        for top, cases in groups.items():
            kept = Fraction(1) if top == 'T' else forced_oracle(
                tuple((p, d[1:]) for p, d in cases),
                arc + (top == 'A'), shoes-1+(top == 'S'))
            if len(cases[0][1]) >= 2:
                by_next = defaultdict(list)
                for w in cases:
                    by_next[w[1][1]].append(w)
                discarded = Fraction()
                for second, contingent in by_next.items():
                    continuation = Fraction(1) if second == 'T' else forced_oracle(
                        tuple((p, d[2:]) for p, d in contingent),
                        arc + (second == 'A'), shoes-1+(second == 'S'))
                    discarded += Fraction(len(contingent), len(cases)) * continuation
                kept = max(kept, discarded)
            value += Fraction(len(cases), len(worlds)) * kept
        actions.append(value)
    return max(actions)


def main():
    counts = {}
    for n in (2, 3, 4):
        checked = 0
        positives = 0
        maximum = Fraction()
        for other in combinations_with_replacement('ASF', n-1):
            prizes = ('T',) + other
            for deck in combinations_with_replacement('ASF', 3):
                supply = Counter(prizes + deck)
                for arc in (1,2,3):
                    for shoes in (1,2,3):
                        if supply['A']+arc > 4 or supply['S']+shoes > 4:
                            continue
                        forced, optional = compare(prizes, deck, arc, shoes)
                        assert optional >= forced
                        checked += 1
                        positives += optional > forced
                        maximum = max(maximum, optional-forced)
        counts[n] = (checked, positives, maximum)
        print('SWEEP', n, checked, positives, maximum)
    assert counts == {
        2: (164,29,Fraction(1,2)),
        3: (251,101,Fraction(1,3)),
        4: (305,156,Fraction(1,4))
    }
    p,d = ('T','F'),('F','F','F')
    worlds = tuple((q,r) for q in set(permutations(p))
                         for r in set(permutations(d)))
    forced, optional = compare(p,d,2,1)
    assert forced == forced_oracle(worlds,2,1) == Fraction(1,2)
    assert optional == Fraction(1)
    print('INDEPENDENT ORACLE OK', forced, optional)
    print('ALL OPTIONAL-SWAP TESTS PASSED')


if __name__ == '__main__':
    main()
