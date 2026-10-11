"""Exact K1 Peonia / Arc Phone / Trekking Shoes resource substitution.

One T is initially uniformly Prized among n physical slots. All deck cards
are inert F. One Peonia and an expendable replacement F are available.
Arc sees top before optionally swapping with a face-down Prize.
Shoes takes observed top. Its discard-and-next-draw alternative is dominated
here because every card below the top is inert filler F.
"""
from fractions import Fraction
from functools import cache
from itertools import combinations


def optimum(n: int, arcs: int, shoes: int) -> Fraction:
    """Observable-policy optimum for a controlled K1 target acquisition."""
    if not 1 <= n <= 6 or not 0 <= arcs <= 4 or not 0 <= shoes <= 4:
        raise ValueError("Expected 1..6 Prizes and 0..4 of each Item")
    top = n

    @cache
    def solve(worlds, remaining_arcs, remaining_shoes, peonia):
        size = len(worlds)
        options = [Fraction()]
        if peonia:
            for selected in combinations(range(n), min(n, 3)):
                hit = sum(where in selected for where in worlds)
                missed = tuple(where for where in worlds if where not in selected)
                score = Fraction(hit, size)
                if missed:
                    score += Fraction(len(missed), size) * solve(
                        missed, remaining_arcs, remaining_shoes, False
                    )
                options.append(score)
        if remaining_arcs:
            score = Fraction()
            for top_is_target in (True, False):
                seen = tuple(
                    where for where in worlds
                    if (where == top) == top_is_target
                )
                if not seen:
                    continue
                choices = [solve(seen, remaining_arcs-1, remaining_shoes, peonia)]
                for slot in range(n):
                    swapped = tuple(
                        top if where == slot else slot if where == top else where
                        for where in seen
                    )
                    choices.append(solve(
                        swapped, remaining_arcs-1, remaining_shoes, peonia
                    ))
                score += Fraction(len(seen), size)*max(choices)
            options.append(score)
        if remaining_shoes:
            if top in worlds:
                score = Fraction(1, size)
                other = tuple(where for where in worlds if where != top)
                if other:
                    score += Fraction(len(other), size)*solve(
                        other, remaining_arcs, remaining_shoes-1, peonia
                    )
            else:
                score = solve(worlds, remaining_arcs, remaining_shoes-1, peonia)
            options.append(score)
        return max(options)

    return solve(tuple(range(n)), arcs, shoes, True)


def check() -> None:
    tests = 0
    for n in range(1, 7):
        for arcs in range(5):
            for shoes in range(5):
                # No Shoes: a-1 novel Prize positions can be revealed by
                # successive Arcs before Peonia checks three.
                # Shoes >=1: the final swapped Prize can be retrieved directly.
                extra = arcs if shoes and arcs else max(0, arcs-1)
                expected = Fraction(min(n, 3+extra), n)
                obtained = optimum(n, arcs, shoes)
                assert obtained == expected, (n, arcs, shoes, obtained, expected)
                tests += 1
    print(f"PASS: {tests} physical-world adaptive policies match closed form")
    for s in (0, 1, 2):
        print("Six Prizes, Shoes", s, [str(optimum(6, a, s)) for a in range(5)])


if __name__ == "__main__":
    check()
