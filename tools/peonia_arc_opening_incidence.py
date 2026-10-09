"""Exact opening incidence for Arc Phone -> Peonia deck-top repacking.

An accepted Basic opener is followed by the ordinary turn draw. The event
requires an Arc, Peonia and expendable filler in hand, and the next deck top
to be a critical singleton T. Hidden Prize locations are marginalized.
"""
from fractions import Fraction
from itertools import combinations
from math import comb


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def exact_event(starters=12, arcs=4, peonias=2, disposable=41,
                total=60, opening=7):
    """Probability conditional on a Basic in the first opening hand."""
    if total < opening + 2:
        raise ValueError("Need a turn draw and another deck-top observation")
    protected = total - starters - arcs - peonias - 1 - disposable
    if min(starters, arcs, peonias, disposable, protected) < 0:
        raise ValueError("Invalid deck partition")
    valid = Fraction(
        choose(total, opening) - choose(total - starters, opening),
        choose(total, opening)
    )
    if not valid:
        raise ValueError("No accepted Basic opening exists")

    exposure = Fraction()
    seen = opening + 1
    for b in range(1, min(starters, seen) + 1):
        for a in range(1, min(arcs, seen-b) + 1):
            for p in range(1, min(peonias, seen-b-a) + 1):
                for f in range(1, min(disposable, seen-b-a-p) + 1):
                    o = seen-b-a-p-f
                    if not 0 <= o <= protected:
                        continue
                    combinations_count = (
                        choose(starters,b) * choose(arcs,a)
                        * choose(peonias,p) * choose(disposable,f)
                        * choose(protected,o)
                    )
                    # If exactly one Basic is among the first H+1 cards,
                    # that Basic must be among the first H, not the turn draw.
                    opener_valid = Fraction(opening,seen) if b == 1 else 1
                    exposure += (
                        Fraction(combinations_count,choose(total,seen))
                        * opener_valid
                    )

    # Among the total-H-1 cards not yet exposed, T occupies the precise
    # next deck position with probability 1/(total-H-1). Prize locations
    # are fully marginalized; this holds when enough deck cards remain.
    return exposure / valid / (total - opening - 1)


def physical_oracle(starters, arcs, peonias, disposable, opening):
    """Independent labeled-card oracle enumerating opening/turn draw/top."""
    cards = ("B" * starters + "A" * arcs + "P" * peonias
             + "T" + "F" * disposable)
    successes = denominator = 0
    for opening_set in combinations(range(len(cards)), opening):
        if not any(cards[i] == "B" for i in opening_set):
            continue
        remaining = [j for j in range(len(cards)) if j not in opening_set]
        for drawn in remaining:
            held = opening_set + (drawn,)
            ready = all(any(cards[i] == kind for i in held)
                        for kind in "APF")
            for next_top in remaining:
                if next_top == drawn:
                    continue
                denominator += 1
                successes += int(ready and cards[next_top] == "T")
    return Fraction(successes, denominator)


def run():
    assert exact_event() == Fraction(345378629, 215366137272)

    for b,a,p,f,h in ((3,2,2,5,4),(3,2,1,6,4),
                      (2,2,2,4,4),(3,1,2,5,4)):
        n = b+a+p+f+1
        analytical = exact_event(starters=b, arcs=a, peonias=p,
                                 disposable=f, opening=h, total=n)
        enumerated = physical_oracle(b,a,p,f,h)
        assert analytical == enumerated, ((b,a,p,f,h),analytical,enumerated)

    expected = {
        1: Fraction(347895,2175415528),
        2: Fraction(33034169,107683068636),
        4: Fraction(30394321,53841534318),
        8: Fraction(8587547,8973589053),
        12: Fraction(5972921,4894684938),
        16: Fraction(37405858,26920767159),
        24: Fraction(41761267,26920767159),
        32: Fraction(42969412,26920767159),
        41: Fraction(345378629,215366137272),
    }
    for disposable, value in expected.items():
        result = exact_event(disposable=disposable)
        assert result == value, (disposable,result,value)
        print(f"F={disposable:2d} -> {float(result):.9%} "
              f"(conditional valid opening)")
    print("Exact grouped counts and 4 independent physical-card oracles pass.")


if __name__ == "__main__":
    run()
