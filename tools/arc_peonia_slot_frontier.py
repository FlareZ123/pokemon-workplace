"""Exact fixed-slot frontier for Arc Phone, Peonia and top-five Items."""
from fractions import Fraction

from tools.rotom_arc_peonia_incidence import with_top_five


def candidates(slots):
    """All four-copy-feasible Arc/Peonia and eight-card top-five splits."""
    output = []
    for arcs in range(1, 5):
        for peonias in range(1, 5):
            arrangers = slots - arcs - peonias
            if 0 <= arrangers <= 8:
                filler = 47 - slots
                value = with_top_five(
                    starters=12, arcs=arcs, peonias=peonias,
                    arrangers=arrangers, disposable=filler,
                    total=60, opening=7, prizes=6,
                )
                output.append((value, arcs, peonias, arrangers))
    return sorted(output, reverse=True)


def run():
    # Each tuple is (fixed package slots, optimal Arc, Peonia, arrangers,
    # exact optimal probability conditional on an accepted Basic opener).
    expected = (
        (2,1,1,0,Fraction(1594523,6526246584)),
        (3,2,1,0,Fraction(9106961,19578739752)),
        (4,2,2,0,Fraction(21180725,23929570808)),
        (5,3,2,0,Fraction(90706637,71788712424)),
        (6,3,3,0,Fraction(129423757,71788712424)),
        (7,3,3,1,Fraction(90498637,35894356212)),
        (8,4,3,1,Fraction(17705999,5522208648)),
        (9,4,4,1,Fraction(73147397,17947178106)),
        (10,4,4,2,Fraction(10668913,2070828243)),
        (11,4,4,3,Fraction(55053199,8973589053)),
        (12,4,4,4,Fraction(189263039,26920767159)),
        (13,4,4,5,Fraction(140765015,17947178106)),
        (14,4,4,6,Fraction(20994991,2447342469)),
        (15,4,4,7,Fraction(248777512,26920767159)),
        (16,4,4,8,Fraction(264758135,26920767159)),
    )
    for slots,a,p,r,expected_value in expected:
        options = candidates(slots)
        best = options[0]
        assert best == (expected_value,a,p,r), (slots,best)
        assert all(v <= expected_value for v,*_ in options)
        # For a/p asymmetry, the model is symmetric by construction:
        for value,x,y,z in options:
            other = next(v for v,b,c,d in options if (b,c,d)==(y,x,z))
            assert value == other
        print(f"K={slots:2d}: {a} Arc, {p} Peonia, {r} arrangers "
              f"-> {float(best[0]):.9%} ({len(options)} candidates)")
    # Exact crossover: a top-five arranger is dominated before the seventh slot.
    assert candidates(6)[0][3] == 0
    assert candidates(7)[0][3] == 1
    print("All 15 exact fixed-slot frontiers verified.")


if __name__ == "__main__":
    run()
