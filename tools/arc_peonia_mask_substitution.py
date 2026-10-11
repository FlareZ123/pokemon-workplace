"""Static source-access mask substitution: 4 Arc vs 3 Arc + 1 Shoes.

One valuable singleton T, all other hidden cards inert filler; held
Peonia and an expendable hand replacement. Compare the same *available*
four labeled candidate Item slots: one slot is an Arc Phone in the old
package and a Trekking Shoes in the new package.

K1: T certainly Prized, top filler. K0: T uniformly across n Prize
and d deck positions. Dynamic actions acquired from elsewhere are out of
scope; unseen source cards are inaccessible throughout this comparison.
"""
from fractions import Fraction
from math import comb
from arc_peonia_shoes_comparison import optimum as k1_physical
from arc_peonia_k0_shoes import optimum as k0_physical, closed_form


def mask_counts(mask: int):
    """Bits 0..2 are Arcs; bit 3 is substituted Arc / Shoes."""
    return (mask & 7).bit_count(), int(bool(mask & 8))


def expected_access(h: int, *, prized: bool, d: int = 46):
    """Exact natural-access projection over all 16 four-slot masks."""
    if not 0 <= h <= 57 or d < 2:
        raise ValueError("h must be 0..57 and d>=2")
    old = new = Fraction()
    weight_sum = Fraction()
    for mask in range(16):
        a, replacement = mask_counts(mask)
        k = mask.bit_count()
        if not 0 <= h-k <= 53:
            continue
        # For each particular labeled subset of source Items:
        weight = Fraction(comb(53, h-k), comb(57, h))
        weight_sum += weight
        if prized:
            old_hit = k1_formula(6,a+replacement,0)
            new_hit = k1_formula(6,a,replacement)
        else:
            old_hit = closed_form(6,d,a+replacement,0)
            new_hit = closed_form(6,d,a,replacement)
        old += weight*old_hit
        new += weight*new_hit
    assert weight_sum == 1
    return old,new


def k1_formula(n: int, arcs: int, shoes: int) -> Fraction:
    additional = arcs if shoes and arcs else max(0,arcs-1)
    return Fraction(min(n,3+additional),n)


def check() -> None:
    cases = 0
    for n in range(1,7):
        for d in range(2,9):
            for mask in range(16):
                a, replacement = mask_counts(mask)
                old_k1 = k1_physical(n,a+replacement,0)
                new_k1 = k1_physical(n,a,replacement)
                assert old_k1 == new_k1, (n,d,mask,old_k1,new_k1)
                old_k0 = k0_physical(n,d,a+replacement,0)
                new_k0 = k0_physical(n,d,a,replacement)
                expected = Fraction(replacement,n+d)
                assert new_k0-old_k0 == expected, (n,d,mask,old_k0,new_k0,expected)
                cases += 1
    for h in (0,1,3,7,15,20,40,52,57):
        old_k1,new_k1=expected_access(h,prized=True)
        assert old_k1 == new_k1, (h,old_k1,new_k1)
        old_k0,new_k0=expected_access(h,prized=False)
        assert new_k0-old_k0 == Fraction(h,57*52), (h,old_k0,new_k0)
        cases += 2
    print("PASS", cases, "K1/K0 physical masks and natural-access identities")
    for h in (7,20,40,52):
        old,new=expected_access(h,prized=False)
        print("h",h,"old",old,"new",new,"gain",new-old)


if __name__=="__main__":
    check()
