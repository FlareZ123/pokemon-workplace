"""Joint rescue of several known-Prized targets with Arc Phone and Peonia.

The q target singleton identities are interchangeable for the *joint success*
objective: all q must be in hand after one Peonia. Each target starts in a
distinct unknown face-down Prize among n, deck top is inert filler F.
Arc sees top then optionally exchanges with chosen Prize. The later Arc
can reveal the preceding Prize displaced onto deck top. Held replacement
filler suffices to retain all q prizes acquired.
"""
from fractions import Fraction
from functools import cache
from itertools import combinations
from math import comb


def hypergeometric_probe_policy(n: int, q: int, arcs: int, m: int = 3):
    """Exact success for a standard distinct-slot Arc probing policy."""
    k = min(n, max(0, arcs-1))
    total = Fraction()
    for j in range(max(0,k-(n-q)), min(k,q)+1):
        prior=Fraction(comb(q,j)*comb(n-q,k-j),comb(n,k))
        remaining_slots=min(m-j,n-k)
        if m<j or remaining_slots<q-j:
            continue
        conditional=Fraction(comb(remaining_slots,q-j),comb(n-k,q-j))
        total += prior*conditional
    return total


def physical_optimum(n: int, q: int, arcs: int, m: int = 3):
    """Independent exact observable-world Bellman over physical Arc swaps."""
    if not 1 <= q <= n or not 1 <= m <= n or not 0 <= arcs <= 4:
        raise ValueError("Invalid Prize, target, probe, or Peonia counts")
    top = n
    worlds=tuple(combinations(range(n),q))

    @cache
    def solve(belief, remaining_arcs):
        total=len(belief)
        # Peonia can choose <=m physical slots, acquiring both/all targets.
        successes=max(
            sum(all(t in selected for t in world) for world in belief)
            for selected in combinations(range(n),m)
        )
        best=Fraction(successes,total)
        if not remaining_arcs or best==1:
            return best
        result=Fraction()
        # The only relevant observation of the top-card identity is
        # whether it is one of the q target singletons.
        for hit in (False,True):
            seen=tuple(w for w in belief if (top in w)==hit)
            if not seen:
                continue
            choices=[solve(seen,remaining_arcs-1)]
            for slot in range(n):
                exchanged=tuple(tuple(sorted(
                    top if t==slot else slot if t==top else t
                    for t in world
                )) for world in seen)
                choices.append(solve(exchanged,remaining_arcs-1))
            result += Fraction(len(seen),total)*max(choices)
        return max(best,result)

    return solve(worlds,arcs)


def check():
    checks=0
    for n in range(3,8):
        for q in range(1,min(n,3)+1):
            for a in range(5):
                physical=physical_optimum(n,q,a)
                formula=hypergeometric_probe_policy(n,q,a)
                assert physical==formula, (n,q,a,physical,formula)
                checks+=1
    assert physical_optimum(6,2,4) == Fraction(4,5)
    assert physical_optimum(6,3,4) == Fraction(2,5)
    print("PASS",checks,"joint-target exact physical-world checks")
    for q in (1,2,3):
        print("six prizes, target count",q,
              [str(physical_optimum(6,q,a)) for a in range(5)])


if __name__=="__main__":
    check()
