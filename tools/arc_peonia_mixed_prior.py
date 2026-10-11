"""Mixed K0/K1 prior: exact Arc Phone, Shoes, Peonia item choice.

The singleton target T is Prized with prior p, uniformly across six Prize
slots, or in a 46-card deck with prior 1-p, uniformly across deck positions.
All other unknown cards are inert filler. Peonia, replacement filler and four
total Items (a Arc and 4-a Shoes) are accessible. Exact Fraction policies
condition only on observed cards, not on their unobserved starting zone.
"""
from fractions import Fraction
from functools import cache
from itertools import combinations


def optimum(n: int, d: int, arcs: int, shoes: int, p: Fraction) -> Fraction:
    """Return unconditional successful mass of the optimal adaptive policy."""
    p = Fraction(p)
    if not 0 <= p <= 1 or n < 1 or d < 1:
        raise ValueError("Invalid zone prior or location counts")
    if arcs < 0 or shoes < 0:
        raise ValueError("Negative Item inventory")

    # (current physical location, starting zone); zone label preserves
    # weights even after physical Prize/top exchanges and deck shifts.
    initial = (
        tuple((j, 1) for j in range(n) if p)
        + tuple((j, 0) for j in range(n, n+d) if p < 1)
    )
    prized_weight = p/n
    deck_weight = (1-p)/d

    def mass(worlds):
        return sum(
            (prized_weight if origin_prized else deck_weight)
            for _, origin_prized in worlds
        ) if worlds else Fraction()

    @cache
    def solve(worlds, length, remaining_arcs, remaining_shoes, peonia):
        alternatives = [Fraction()]
        if peonia:
            for selected in combinations(range(n), min(n, 3)):
                hit = tuple(w for w in worlds if w[0] in selected)
                missed = tuple(w for w in worlds if w[0] not in selected)
                gain = mass(hit)
                if missed:
                    gain += solve(
                        missed, length, remaining_arcs, remaining_shoes, False
                    )
                alternatives.append(gain)

        if remaining_arcs and length:
            gain = Fraction()
            for top_is_target in (True, False):
                seen = tuple(
                    w for w in worlds if (w[0] == n) == top_is_target
                )
                if not seen:
                    continue
                choices = [solve(
                    seen, length, remaining_arcs-1, remaining_shoes, peonia
                )]
                for slot in range(n):
                    changed = tuple((
                        n if where == slot else slot if where == n else where,
                        origin,
                    ) for where, origin in seen)
                    choices.append(solve(
                        changed, length, remaining_arcs-1, remaining_shoes, peonia
                    ))
                gain += max(choices)
            alternatives.append(gain)

        if remaining_shoes and length:
            hit = tuple(w for w in worlds if w[0] == n)
            missed = tuple(w for w in worlds if w[0] != n)
            gain = mass(hit)
            if missed:
                take_filler = tuple((
                    where if where < n else where-1, origin
                ) for where, origin in missed)
                best = solve(
                    take_filler, length-1, remaining_arcs,
                    remaining_shoes-1, peonia
                )
                if length >= 2:
                    second_hit = tuple(w for w in missed if w[0] == n+1)
                    after_second = tuple((
                        where if where < n else where-2, origin
                    ) for where, origin in missed if where != n+1)
                    discard = mass(second_hit)
                    if after_second:
                        discard += solve(
                            after_second, length-2, remaining_arcs,
                            remaining_shoes-1, peonia
                        )
                    best = max(best, discard)
                gain += best
            alternatives.append(gain)
        return max(alternatives)

    return solve(initial, d, arcs, shoes, True)


def four_item_frontier(arcs: int, p: Fraction) -> Fraction:
    """Proved 6-Prize/46-deck bound, attained by explicit observation paths."""
    p = Fraction(p)
    q = 1-p
    if arcs == 0:
        return p*Fraction(3, 6)+q*Fraction(8, 46)
    if arcs == 4:
        return p+q*Fraction(1, 46)
    prize_heavy = p*Fraction(arcs+3, 6)+q*Fraction(8-2*arcs, 46)
    deck_heavy = p*Fraction(arcs+2, 6)+q*Fraction(9-2*arcs, 46)
    return max(prize_heavy, deck_heavy)


def check() -> None:
    priors = (
        [Fraction(i, 20) for i in range(21)]
        + [Fraction(3, 26), Fraction(6, 29)]
        + [Fraction(6, 29)-Fraction(1, 1000),
           Fraction(6, 29)+Fraction(1, 1000)]
    )
    tests = 0
    for p in priors:
        values = []
        for arcs in range(5):
            calculated = optimum(6, 46, arcs, 4-arcs, p)
            formula = four_item_frontier(arcs, p)
            assert calculated == formula, (p, arcs, calculated, formula)
            values.append(calculated)
            tests += 1
        expected = max(values[0], values[3])
        assert max(values) == expected, (p, values)
    threshold = Fraction(6, 29)
    assert all(
        four_item_frontier(i, threshold) == Fraction(7, 29)
        for i in range(4)
    )
    print(f"PASS {tests} rational mixed-prior adaptive policy comparisons")
    print("Full prior switch: Prized probability p = 6/29")
    for p in (Fraction(1, 10), threshold, Fraction(1, 2), Fraction(1)):
        values = [four_item_frontier(a, p) for a in range(5)]
        print(p, max(values), [a for a, v in enumerate(values) if v == max(values)])


if __name__ == "__main__":
    check()
