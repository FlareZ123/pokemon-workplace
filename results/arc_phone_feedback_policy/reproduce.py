"""Independent labeled-world oracle for Arc/Shoes adaptive Prize retrieval."""
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import permutations

from tools.arc_phone_feedback_policy import (
    alternating_policy, exact_composition, free_top_information_after_swap,
    optimal_retrieval,
)


@lru_cache(maxsize=None)
def oracle(worlds, arc, shoes):
    """Enumerate physical states, retaining multiplicity of collapsed worlds."""
    if not arc and not shoes:
        return Fraction()
    total = len(worlds)
    grouped = defaultdict(list)
    for prize_layout, deck_top in worlds:
        grouped[deck_top].append((prize_layout, deck_top))
    candidates = [Fraction()]
    if shoes:
        subtotal = Fraction()
        for seen, members in grouped.items():
            if seen == "T":
                answer = Fraction(1)
            else:
                next_worlds = tuple(sorted((prizes, "F") for prizes, _ in members))
                answer = oracle(next_worlds, arc + int(seen == "A"),
                                shoes - 1 + int(seen == "S"))
            subtotal += Fraction(len(members), total) * answer
        candidates.append(subtotal)
    if arc:
        subtotal = Fraction()
        for members in grouped.values():
            known = tuple(sorted(members))
            alternatives = [oracle(known, arc - 1, shoes)]
            for position in range(len(known[0][0])):
                exchanged = []
                for prize_layout, deck_top in members:
                    outgoing = prize_layout[position]
                    next_prizes = prize_layout[:position] + (deck_top,) + prize_layout[position+1:]
                    exchanged.append((next_prizes, outgoing))
                alternatives.append(oracle(tuple(sorted(exchanged)), arc - 1, shoes))
            subtotal += Fraction(len(members), total) * max(alternatives)
        candidates.append(subtotal)
    return max(candidates)


def main():
    cases = {
        ("T", "A", "S"): ((1, 1), (2, 1), (2, 2)),
        ("T", "A", "S", "F"): ((2, 1), (2, 2), (3, 2)),
        ("T", "A", "S", "F", "F", "F"): ((2, 1), (2, 2), (3, 2)),
    }
    for composition, inventories in cases.items():
        layouts = tuple(sorted(set(permutations(composition))))
        initial_worlds = tuple((layout, "F") for layout in layouts)
        for arc, shoes in inventories:
            expected = oracle(initial_worlds, arc, shoes)
            actual = optimal_retrieval(exact_composition(composition), arc, shoes)
            alternating = Fraction(sum(alternating_policy(layout, arc, shoes)
                                       for layout in layouts), len(layouts))
            assert actual == expected and actual >= alternating
            print("ORACLE OK", len(layouts), arc, shoes, actual, alternating)
    three = exact_composition(("T", "A", "S"))
    assert optimal_retrieval(three, 2, 1) == Fraction(2, 3)
    assert optimal_retrieval(three, 2, 2) == 1
    four = exact_composition(("T", "A", "S", "F"))
    assert optimal_retrieval(four, 3, 2) == Fraction(7, 8)
    assert free_top_information_after_swap(four, 3, 2, 0) == Fraction(23, 24)
    six = exact_composition(("T", "A", "S", "F", "F", "F"))
    assert optimal_retrieval(six, 3, 2) == Fraction(13, 24)
    print("ALL FEEDBACK TESTS PASSED")


if __name__ == "__main__":
    main()
