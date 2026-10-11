"""Two-dimensional Arc/Shoes four-Item allocation frontier.

A single T occupies six Prizes with prior p, uniformly there, or one of
d deck positions with prior 1-p, uniformly there. Peonia, filler payment
and four immediately usable Items are held. All other cards inert F.

Eight attainable Prize/deck coverage pairs generate the exact upper
envelope, crosschecked against an observation-respecting physical Bellman.
"""
from fractions import Fraction
from arc_peonia_mixed_prior import optimum as physical_optimum


def coverage_pairs(d: int):
    if d < 1:
        raise ValueError("Deck must be nonempty")
    pairs = [(0,3,min(8,d),"Shoes-only")]
    for a in range(1,4):
        s=4-a
        pairs.append((a,min(6,a+2),min(d,1+2*s),"deck-heavy"))
        pairs.append((a,min(6,a+3),min(d,2*s),"Prize-heavy"))
    pairs.append((4,6,min(d,1),"Arc-only"))
    return tuple(pairs)


def line_value(prizes: int, deck: int, d: int, prior: Fraction):
    return prior*Fraction(prizes,6)+(1-prior)*Fraction(deck,d)


def optimize(d: int, prior: Fraction):
    """Optimal success probability and all tied Arc inventory counts."""
    prior = Fraction(prior)
    if not 0 <= prior <= 1:
        raise ValueError("Prior must lie in [0,1]")
    rows=coverage_pairs(d)
    values=tuple(line_value(pr,dk,d,prior) for _,pr,dk,_ in rows)
    best=max(values)
    winners=tuple(sorted({a for (a,_,_,_),value in zip(rows,values) if value==best}))
    return best,winners


def rational_breakpoints(d: int):
    """Intersections that actually change the optimal-inventory set."""
    pairs=coverage_pairs(d)
    lines=[(
        Fraction(deck,d),
        Fraction(pr,6)-Fraction(deck,d)
    ) for _,pr,deck,_ in pairs]
    candidates={Fraction(),Fraction(1)}
    for i,(b,m) in enumerate(lines):
        for bb,mm in lines[i+1:]:
            if m != mm:
                p=(bb-b)/(m-mm)
                if 0 < p < 1:
                    candidates.add(p)
    candidates=sorted(candidates)
    segments=[]
    for lo,hi in zip(candidates,candidates[1:]):
        winners=optimize(d,(lo+hi)/2)[1]
        if segments and segments[-1][1]==lo and segments[-1][2]==winners:
            segments[-1]=(segments[-1][0],hi,winners)
        else:
            segments.append((lo,hi,winners))
    return tuple(segments)


EXPECTED={
    1: ((Fraction(0),Fraction(1),(3,4)),),
    2: ((Fraction(0),Fraction(1),(3,)),),
    3: ((Fraction(0),Fraction(2,3),(2,3)),(Fraction(2,3),Fraction(1),(3,))),
    4: ((Fraction(0),Fraction(3,4),(2,)),(Fraction(3,4),Fraction(1),(3,))),
    5: ((Fraction(0),Fraction(6,11),(1,2)),(Fraction(6,11),Fraction(12,17),(2,)),(Fraction(12,17),Fraction(1),(3,))),
    6: ((Fraction(0),Fraction(2,3),(1,)),(Fraction(2,3),Fraction(1),(3,))),
    7: ((Fraction(0),Fraction(6,13),(0,1)),(Fraction(6,13),Fraction(12,19),(1,)),(Fraction(12,19),Fraction(1),(3,))),
    8: ((Fraction(0),Fraction(3,5),(0,)),(Fraction(3,5),Fraction(1),(3,))),
    46: ((Fraction(0),Fraction(6,29),(0,)),(Fraction(6,29),Fraction(1),(3,))),
}


def check():
    tested = 0
    # Independent full action policy checks at endpoints, every phase
    # midpoint and every exact breakpoint.
    for d in list(range(1,9))+[46]:
        segments=rational_breakpoints(d)
        assert segments == EXPECTED[d], (d,segments,EXPECTED[d])
        pset={Fraction(0),Fraction(1)}
        for lo,hi,_ in segments:
            pset.update((lo,hi,(lo+hi)/2))
        for p in sorted(pset):
            predicted,winners=optimize(d,p)
            observed=tuple(
                physical_optimum(6,d,a,4-a,p) for a in range(5)
            )
            assert predicted == max(observed), (d,p,predicted,observed)
            actual_winners=tuple(a for a,v in enumerate(observed) if v==predicted)
            assert winners == actual_winners, (d,p,winners,actual_winners)
            tested += 5
    # Large-deck theorem: the only interior inventory switch is
    # p = 12/(d+12), for all checked d>=8.
    for d in range(8,47):
        expected_cross=Fraction(12,d+12)
        expected_segs=((Fraction(0),expected_cross,(0,)),(expected_cross,Fraction(1),(3,)))
        assert rational_breakpoints(d)==expected_segs, (d,rational_breakpoints(d))
    print("PASS",tested,"physical mixed-prior comparisons and 46 exact phase structures")
    for d in (2,3,4,5,6,7,8,46):
        print("d",d,"phases",rational_breakpoints(d))


if __name__=="__main__":
    check()
