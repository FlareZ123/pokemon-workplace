"""Exact K0 Peonia, Arc Phone and Trekking Shoes acquisition frontier.

One target T is initially uniformly located among n Prize and d deck
positions; all other cards F inert. Peonia and one expendable replacement
F are held. Each Arc Phone looks at the top, optionally swaps one facedown
Prize with it. Each Shoes looks top, then either takes it or discards it
and draws the next card. One Peonia may select up to three Prize positions.
The search respects each observation and actual deck-length transitions.
"""
from fractions import Fraction
from functools import cache
from itertools import combinations


def optimum(n: int, d: int, arcs: int, shoes: int) -> Fraction:
    """Return the exact adaptive target-in-hand probability."""
    if not 1 <= n <= 6 or d < 1 or not 0 <= arcs <= 4 or not 0 <= shoes <= 4:
        raise ValueError("Expected 1..6 Prizes, deck >=1, Items 0..4")

    @cache
    def solve(worlds, deck_length, a, s, peonia):
        size = len(worlds)
        options = [Fraction()]
        if peonia:
            for chosen in combinations(range(n), min(n, 3)):
                hits = sum(t in chosen for t in worlds)
                missed = tuple(t for t in worlds if t not in chosen)
                value = Fraction(hits, size)
                if missed:
                    value += Fraction(len(missed), size)*solve(
                        missed, deck_length, a, s, False
                    )
                options.append(value)

        if a and deck_length:
            expectation = Fraction()
            for top_is_target in (True, False):
                observed = tuple(
                    t for t in worlds if (t == n) == top_is_target
                )
                if not observed:
                    continue
                alternatives = [solve(observed, deck_length, a-1, s, peonia)]
                for j in range(n):
                    swapped = tuple(
                        n if t == j else j if t == n else t
                        for t in observed
                    )
                    alternatives.append(
                        solve(swapped, deck_length, a-1, s, peonia)
                    )
                expectation += Fraction(len(observed), size)*max(alternatives)
            options.append(expectation)

        if s and deck_length:
            top_hit = Fraction(int(n in worlds), size)
            missed = tuple(t for t in worlds if t != n)
            if not missed:
                options.append(Fraction(1))
            else:
                # Shoes takes a known F top, shifting the deck by one.
                after_take = tuple(t if t < n else t-1 for t in missed)
                best = solve(after_take, deck_length-1, a, s-1, peonia)
                if deck_length >= 2:
                    # Shoes instead discards F and draws the next card.
                    second_hit = sum(t == n+1 for t in missed)
                    after_second = tuple(
                        t if t < n else t-2
                        for t in missed if t != n+1
                    )
                    alternate = Fraction(second_hit, len(missed))
                    if after_second:
                        alternate += Fraction(len(after_second), len(missed))*solve(
                            after_second, deck_length-2, a, s-1, peonia
                        )
                    best = max(best, alternate)
                options.append(top_hit+Fraction(len(missed), size)*best)
        return max(options)

    return solve(tuple(range(n+d)), d, arcs, shoes, True)


def closed_form(n: int, d: int, arcs: int, shoes: int) -> Fraction:
    """Candidate finite-card upper bound, attaining all verified states."""
    if arcs == 0:
        covered = min(n, 3)+min(d, 2*shoes)
    else:
        prize_limit = min(n, arcs+2+int(shoes > 0))
        deck_limit = min(d, 1+2*shoes)
        observation_limit = 3+arcs+2*shoes
        covered = min(n+d, prize_limit+deck_limit, observation_limit)
    return Fraction(covered, n+d)


def check() -> None:
    count = 0
    for n in range(1, 7):
        for d in range(1, 9):
            for arcs in range(5):
                for shoes in range(5):
                    actual = optimum(n, d, arcs, shoes)
                    formula = closed_form(n, d, arcs, shoes)
                    assert actual == formula, (n, d, arcs, shoes, actual, formula)
                    count += 1
    for arcs in range(5):
        for shoes in range(5):
            actual = optimum(6, 46, arcs, shoes)
            formula = closed_form(6, 46, arcs, shoes)
            assert actual == formula, (arcs, shoes, actual, formula)
            count += 1
    print(f"PASS {count} full physical adaptive world/belief comparisons")
    print("Uniform T among 6 Prize + 46 deck positions, four-Item mixes:")
    for arcs in range(5):
        shoes = 4-arcs
        print(f"Arc {arcs}, Shoes {shoes}: {closed_form(6,46,arcs,shoes)}")


if __name__ == "__main__":
    check()
