"""Independent exhaustive labeled-card verification of the grouped chain model."""
from collections import defaultdict
from fractions import Fraction
from itertools import combinations, permutations

from tools.arc_phone_chain_access import exact_access, fixed_resource_case


def best_kept(cards, n, chained, slots):
    best = 0
    for returned in combinations(range(len(cards)), n):
        left = [c[0] for i, c in enumerate(cards) if i not in returned]
        arc, shoes = left.count("A"), left.count("S")
        if shoes:
            best = max(best, min(slots, arc if chained else min(arc, shoes)))
    return best


def labeled_oracle(seen, chained):
    deck = ("T0", "P0", "A0", "A1", "S0", "S1", "F0", "F1", "F2", "F3")
    total = Fraction()
    cases = 0
    for extra in combinations(deck[1:], 2):
        prizes = ("T0",) + extra
        layouts = tuple(permutations(prizes))
        for hand in combinations(tuple(c for c in deck[1:] if c not in extra), seen):
            cases += 1
            a = sum(c[0] == "A" for c in hand)
            s = sum(c[0] == "S" for c in hand)
            k = min(3, a if chained else min(a, s)) if s else 0
            choices = [Fraction(k, 3)]
            if "P0" in hand:
                leftovers = tuple(c for c in hand if c != "P0")
                for n in (1, 2):
                    observed = defaultdict(list)
                    for layout in layouts:
                        label = tuple(sorted(c[0] for c in layout[:n]))
                        observed[label].append(layout)
                    success = 0
                    for label, scenarios in observed.items():
                        if "T" in label:
                            if leftovers:
                                success += len(scenarios)
                            continue
                        kept = best_kept(leftovers + scenarios[0][:n],
                                         n, chained, 3 - n)
                        success += sum("T0" in scenario[n:n+kept] for scenario in scenarios)
                    choices.append(Fraction(success, len(layouts)))
            total += max(choices)
    return total / cases


def main():
    assert fixed_resource_case() == (Fraction(1), Fraction(2, 3))
    for d in (1, 2, 3, 4):
        for chained in (False, True):
            actual = exact_access(seen=d, deck=(1, 1, 2, 2, 4),
                                  prize_count=3, peonia_limit=2, chained=chained)
            oracle = labeled_oracle(d, chained)
            assert actual == oracle, (d, chained, actual, oracle)
            print("oracle:", d, chained, actual)
    for d in (7, 10, 13, 16):
        a = exact_access(seen=d)
        b = exact_access(seen=d, chained=False)
        assert a >= b
        print("sixty:", d, f"{float(a):.9%}", f"{float(b):.9%}")
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
