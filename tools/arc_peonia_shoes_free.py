"""Exact shoes-free Arc Phone / Peonia Prize rescue model."""
from fractions import Fraction
from functools import cache
from itertools import combinations
from math import comb


def belief_optimum(n: int, d: int, arcs: int, *, prized: bool) -> Fraction:
    """Bellman policy; only one target T, all other cards inert filler."""
    if not 1 <= n <= 6 or d < 1 or not 0 <= arcs <= 4:
        raise ValueError("Invalid Prize/deck/Arc counts")
    p = (Fraction(1, n if prized else n+d),) * n
    top = Fraction(0 if prized else 1, n+d)
    deep = Fraction(0 if prized else d-1, n+d)

    @cache
    def solve(prizes, top, deep, remaining):
        peonia = sum(sorted(prizes, reverse=True)[:3], Fraction())
        if remaining == 0:
            return peonia
        if top == 1:
            return Fraction(1)
        q = 1-top
        pp = tuple(v/q for v in prizes)
        dd = deep/q
        options = [solve(pp, Fraction(), dd, remaining-1)]
        for i, mass in enumerate(pp):
            changed = list(pp)
            changed[i] = Fraction()
            options.append(solve(tuple(changed), mass, dd, remaining-1))
        return max(peonia, top + q*max(options))

    return solve(p, top, deep, arcs)


def world_oracle(n: int, d: int, arcs: int, *, prized: bool) -> Fraction:
    """Independent labeled physical-world oracle with observation partition."""
    worlds = []
    for target in range(n if prized else n+d):
        cards = tuple("T" if k == target else "F" for k in range(n+d))
        worlds.append((cards[:n], cards[n:]))

    @cache
    def solve(belief, remaining):
        count = len(belief)
        raw = max(sum(any(prizes[i] == "T" for i in slots)
                      for prizes, _ in belief)
                  for slots in combinations(range(n), min(n, 3)))
        peonia = Fraction(raw, count)
        if remaining == 0:
            return peonia
        after_arc = Fraction()
        for observed_top in ("T", "F"):
            observed = tuple(w for w in belief if w[1][0] == observed_top)
            if not observed:
                continue
            continuations = [solve(observed, remaining-1)]
            for slot in range(n):
                changed = []
                for prize, deck in observed:
                    replacement = list(prize)
                    replacement[slot] = deck[0]
                    changed.append((tuple(replacement), (prize[slot],) + deck[1:]))
                continuations.append(solve(tuple(changed), remaining-1))
            after_arc += Fraction(len(observed), count)*max(continuations)
        return max(peonia, after_arc)

    return solve(tuple(worlds), arcs)


def natural_access(h: int) -> Fraction:
    """60-card conditional model: T Prized, Peonia+filler held, A4 among 57."""
    if not 0 <= h <= 52:
        raise ValueError("h must be 0..52")
    return sum((
        Fraction(comb(4, a)*comb(53, h-a), comb(57, h))
        * (Fraction(1, 2) if a <= 1 else Fraction(a+2, 6))
        for a in range(5) if 0 <= h-a <= 53
    ), Fraction())


def check() -> None:
    tested = 0
    for n in range(1, 7):
        for d in range(1, 5):
            for a in range(5):
                for prized in (True, False):
                    actual = belief_optimum(n, d, a, prized=prized)
                    oracle = world_oracle(n, d, a, prized=prized)
                    formula = (
                        Fraction(min(n, 3 if a == 0 else a+2), n)
                        if prized else
                        Fraction((0 if a == 0 else 1)
                                 + min(n, 3 if a == 0 else a+2), n+d)
                    )
                    assert actual == oracle == formula, (n, d, a, prized)
                    tested += 1
    assert natural_access(7) == Fraction(8674, 16929)
    assert natural_access(20) == Fraction(707, 1188)
    assert natural_access(40) == Fraction(13580, 16929)
    print(f"PASS: {tested} exact cases, full physical oracle and closed form")
    print("K1 Prized:", [str(belief_optimum(6, 46, a, prized=True))
                          for a in range(5)])
    print("K0 uniform:", [str(belief_optimum(6, 46, a, prized=False))
                          for a in range(5)])
    print("Visible-Arc overlay:", [(h, str(natural_access(h)))
                                    for h in (7, 10, 20, 40)])


if __name__ == "__main__":
    check()
