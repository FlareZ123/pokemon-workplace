"""Access-mask coupling: one Shoes substitutes for the last Arc Phone.

One T uniformly in n face-down Prizes (K1) or n Prizes+d deck positions
(K0), other cards inert filler. Peonia and replacement payment in hand.
Compare two four-card inventory packages with the *same* visibility masks:
four Arc Phones versus three Arc Phones + one Trekking Shoes.
Only copies in the accessible mask may be played; unseen source cards do not
become newly usable upon a Shoes draw. This is a static access projection.
"""
from fractions import Fraction
from itertools import combinations
from math import comb
from arc_peonia_shoes_comparison import optimum as k1_physical
from arc_peonia_k0_shoes import optimum as k0_physical
from arc_peonia_mixed_prior import optimum as mixed_physical


def mask_counts(mask: int):
    """Bit 3 is the replaced Arc/Shoes; bits 0..2 are unchanged Arcs."""
    return (mask & 7).bit_count(), bool(mask & 8)


def fixed_mask_pair(n: int, d: int, mask: int, p: Fraction):
    """(four-Arc, three-Arc-plus-Shoes), exact optimal mixed-prior values."""
    arcs, shoes = mask_counts(mask)
    return (
        mixed_physical(n, d, arcs+int(shoes), 0, p),
        mixed_physical(n, d, arcs, int(shoes), p),
    )


def expected_access_value(h: int, *, p: Fraction, d: int):
    """Full 57-location source mask enumeration, all four Items distinct.

    T is independently located in the n=6 Prize positions with prior p,
    or among d hidden deck positions with prior 1-p. A random h-subset of
    a 57-location independent source universe is accessible; there are four
    candidate Items and 53 inert entries.
    """
    if not 0 <= h <= 57 or d < 2:
        raise ValueError("h must be 0..57 and d>=2")
    values = [Fraction(), Fraction()]
    for mask in range(16):
        copies = mask.bit_count()
        if not 0 <= h-copies <= 53:
            continue
        # Every particular subset of the 4 labeled Item slots occurs with
        # this exact hypergeometric probability.
        weight = Fraction(comb(53, h-copies), comb(57, h))
        a, shoes = mask_counts(mask)
        old_k1 = Fraction(min(6, 3+max(0, a+int(shoes)-1)), 6)
        new_k1 = Fraction(min(6, 3+(a if shoes and a else max(0, a-1))), 6)
        old_k0 = (
            Fraction(3, 6+d) if not a+int(shoes)
            else Fraction(min(6,a+int(shoes)+2)+1, 6+d)
        )
        new_k0 = (
            Fraction(3, 6+d) if not a and not shoes else
            Fraction(min(6,3)+min(d,2),6+d) if shoes and not a else
            Fraction(min(6+d, 3+a+2*int(shoes),
                     min(6,a+2+int(shoes))+min(d,1+2*int(shoes))),6+d)
        )
        old = p*old_k1 + (1-p)*Fraction(old_k0*(6+d)-(old_k1*6), d)
        new = p*new_k1 + (1-p)*Fraction(new_k0*(6+d)-(new_k1*6), d)
        values[0] += weight*old
        values[1] += weight*new
    assert sum(
        Fraction(comb(53,h-mask.bit_count()), comb(57,h))
        for mask in range(16) if 0 <= h-mask.bit_count() <= 53
    ) == 1
    return tuple(values)


def check():
    cases = 0
    # Exact physical K1 and K0 adaptivity versus the target-region counting
    # formula for every held-item mask. n<=6, d>=2 (no deck saturation).
    for n in range(1, 7):
        for d in range(2, 9):
            for mask in range(16):
                a, s = mask_counts(mask)
                old_a = a+int(s)
                old_k1 = k1_physical(n, old_a, 0)
                new_k1 = k1_physical(n, a, int(s))
                assert old_k1 == new_k1, (n,d,mask,old_k1,new_k1)
                old_k0 = k0_physical(n,d,old_a,0)
                new_k0 = k0_physical(n,d,a,int(s))
                difference = Fraction(int(s and (a+3 < n or d >= 2)), n+d)
                # When Prize saturation happens at low n, Shoes still
                # increases deck access if its extra deck position exists,
                # except if both packages already cover all positions.
                if s:
                    difference = Fraction(1 if d>=2 and (a+3 < n+d) else 0, n+d)
                else:
                    difference = Fraction()
                assert new_k0-old_k0 == difference, (n,d,mask,new_k0,old_k0,difference)
                cases += 1
    # Uniform-zone model: T Prized probability n/(n+d) is the exact K0
    # physical prior. Additional arbitrary mixed-prior spot checks show
    # that the action planner preserves this pointwise identity.
    for p in (Fraction(0),Fraction(1,10),Fraction(1,2),Fraction(9,10),Fraction(1)):
        for mask in range(16):
            old, new = fixed_mask_pair(6, 8, mask, p)
            expected = (1-p)*Fraction(int(bool(mask & 8)),8)
            assert new-old == expected, (p,mask,new,old,expected)
            cases += 1
    for h in (0,1,3,7,15,20,40,52,57):
        for p in (Fraction(), Fraction(1,2), Fraction(1)):
            old,new=expected_access_value(h,p=p,d=46)
            assert new-old == Fraction(h,57)*(1-p)/46, (h,p,old,new)
            cases += 1
    print("PASS", cases, "physical mask and mixed-prior access checks")
    for h in (7,20,40,52):
        old,new = expected_access_value(h,p=Fraction(6,52),d=46)
        print("visible",h,"old",old,"new",new,"improvement",new-old)


if __name__=="__main__":
    check()
