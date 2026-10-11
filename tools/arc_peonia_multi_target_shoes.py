"""Physical Peonia, Arc Phone, Shoes policy for simultaneous Prized targets.

q interchangeable targets all in n facedown Prize slots. All other
deck cards are inert filler, with an ample filler tail. Held Peonia and
sufficient expendable filler permit all replacements. Both Items are
physically held and can be sequenced before or after Peonia.

We model an actual observation before each conditional Arc optional swap
or Shoes take, and Peonia's chosen slots before seeing their contents.
"""
from collections import defaultdict
from fractions import Fraction
from functools import cache
from itertools import combinations


def joint_optimum(n: int, q: int, arcs: int, shoes: int, m: int = 3) -> Fraction:
    if not 1 <= q <= n or not 1 <= m <= n or arcs < 0 or shoes < 0:
        raise ValueError("Invalid target, Prize, or Item count")
    top=n
    initial=tuple(combinations(range(n),q))

    @cache
    def solve(belief, a, s, peonia):
        if not belief[0]:
            return Fraction(1)
        if not a and not s and not peonia:
            return Fraction()
        total=len(belief)
        best=Fraction()

        if peonia:
            for chosen in combinations(range(n),m):
                # The retrieved cards are observed and the selected Prize
                # slots become filler. Every remaining target stays where it
                # was. We branch on the *number* of retrieved targets.
                groups=defaultdict(list)
                for world in belief:
                    remaining=tuple(t for t in world if t not in chosen)
                    groups[q-len(remaining)].append(remaining)
                value=sum((
                    Fraction(len(group),total)
                    *solve(tuple(sorted(group)),a,s,False)
                    for group in groups.values()
                ),Fraction())
                if value>best:
                    best=value

        if a:
            groups=defaultdict(list)
            for world in belief:
                groups[top in world].append(world)
            value=Fraction()
            for observed in groups.values():
                sub=tuple(sorted(observed))
                choices=[solve(sub,a-1,s,peonia)]
                for j in range(n):
                    swapped=tuple(sorted(
                        tuple(sorted(
                            top if t==j else j if t==top else t
                            for t in world
                        )) for world in observed
                    ))
                    choices.append(solve(swapped,a-1,s,peonia))
                value+=Fraction(len(observed),total)*max(choices)
            best=max(best,value)

        if s:
            groups=defaultdict(list)
            for world in belief:
                groups[top in world].append(world)
            value=Fraction()
            for observed in groups.values():
                updated=tuple(sorted(
                    tuple(t for t in world if t!=top)
                    for world in observed
                ))
                value+=Fraction(len(observed),total)*solve(updated,a,s-1,peonia)
            best=max(best,value)
        return best

    return solve(initial,arcs,shoes,True)


def check() -> None:
    tests=0
    for n in range(3,7):
        for q in range(1,min(3,n)+1):
            for a in range(5):
                s=4-a
                value=joint_optimum(n,q,a,s)
                assert 0 <= value <= 1
                tests+=1
    # Crosscheck extremes with the independent no-Shoes multi-target oracle
    # and singleton Arc/Shoes formula.
    from arc_peonia_multi_target import physical_optimum
    from arc_peonia_shoes_comparison import optimum as singleton_optimum
    for n in range(3,7):
        for q in range(1,min(3,n)+1):
            for a in range(5):
                assert joint_optimum(n,q,a,0) == physical_optimum(n,q,a)
                tests+=1
        for a in range(5):
            assert joint_optimum(n,1,a,4-a) == singleton_optimum(n,a,4-a)
            tests+=1
    print("PASS",tests,"multi-target physical and independent boundary checks")
    print("Six Prize, q=1..3, four-Item allocation frontier:")
    for q in (1,2,3):
        print(q, [(a,str(joint_optimum(6,q,a,4-a))) for a in range(5)])


if __name__=="__main__":
    check()
