"""Exact four-Item Arc/Shoes policy phases as unknown deck size depletes.

One singleton T uniform among six Prize positions and d deck positions;
all other hidden cards inert filler, one Peonia and replacement filler held.
Find the best initial four-Item inventory (a Arc, 4-a Shoes).
"""
from fractions import Fraction
from arc_peonia_k0_shoes import optimum, closed_form

EXPECTED_BEST = {
    1: (3, 4),
    2: (3,),
    3: (2, 3),
    4: (2,),
    5: (1, 2),
    6: (1,),
    7: (0, 1),
}


def four_item_phase(d: int):
    if d < 1:
        raise ValueError("Remaining deck size must be >= 1")
    counts = tuple(int(closed_form(6,d,a,4-a)*(6+d)) for a in range(5))
    peak = max(counts)
    winners = tuple(a for a, covered in enumerate(counts) if covered == peak)
    return Fraction(peak,6+d), counts, winners


def check() -> None:
    tests = 0
    for d in range(1,47):
        p, counts, winners = four_item_phase(d)
        assert winners == EXPECTED_BEST.get(d,(0,)), (d,counts,winners)
        if d <= 12 or d == 46:
            for a in range(5):
                physical = optimum(6,d,a,4-a)
                expected = Fraction(counts[a],6+d)
                assert physical == expected, (d,a,physical,expected)
                tests += 1
    assert four_item_phase(1)[0] == 1
    assert four_item_phase(4)[0] == Fraction(9,10)
    assert four_item_phase(6)[0] == Fraction(5,6)
    assert four_item_phase(8)[0] == Fraction(11,14)
    assert four_item_phase(46)[0] == Fraction(11,52)
    print("PASS", tests, "physical policy comparisons + all 46 exact phase classifications")
    print("d, Prized/Deck target acquisition optimum, best Arc counts:")
    for d in range(1,10):
        p,counts,winners = four_item_phase(d)
        print(d,str(p),counts,winners)
    print("d>=8: four Shoes optimal; success 11/(6+d)")


if __name__=="__main__":
    check()
