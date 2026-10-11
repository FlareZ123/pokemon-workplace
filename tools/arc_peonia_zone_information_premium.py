"""Value of free prior Prize-zone revelation for fixed Arc/Shoes inventory.

This is a controlled K1 *information* experiment, not a modeled search
payment. A target T is uniformly within six face-down Prizes with prior
p and uniformly within a d-card deck otherwise. Remaining hidden cards
inert filler. Peonia, replacement filler and a fixed four-Item mix held.

The prior-oblivious policy can choose action modes adaptively upon card
observations. The zone-revealed policy may choose modes after learning
T's zone before spending its first card.
"""
from fractions import Fraction
from arc_peonia_mixed_prior import optimum as physical_prior
from arc_peonia_two_dimensional_phases import optimize, coverage_pairs, line_value


def premium(d: int, arcs: int, prior: Fraction):
    """(prior value, zone-revealed value, pure information premium)."""
    prior=Fraction(prior)
    if d < 1 or not 0 <= arcs <= 4 or not 0 <= prior <= 1:
        raise ValueError("Invalid deck, arc count or prior")
    rows=tuple(row for row in coverage_pairs(d) if row[0] == arcs)
    unknown=max(line_value(r,k,d,prior) for _,r,k,_ in rows)
    prize=max(r for _,r,_,_ in rows)
    deck=max(k for _,_,k,_ in rows)
    revealed=prior*Fraction(prize,6)+(1-prior)*Fraction(deck,d)
    return unknown,revealed,revealed-unknown


def predicted_information_gain(d: int, arcs: int, prior: Fraction):
    """Closed-form information premium from the two mode tradeoff."""
    if arcs == 0 or arcs == 4 or d <= 2*(4-arcs):
        return Fraction()
    return min(Fraction(prior,6),Fraction(1-prior,d))


def check() -> None:
    tests = 0
    for d in tuple(range(1,9))+(46,):
        priors={Fraction(0),Fraction(1,4),Fraction(1,2),
                Fraction(3,4),Fraction(1),
                Fraction(6,6+d),Fraction(12,d+12)}
        for p in sorted(priors):
            for arcs in range(5):
                unknown, revealed, gain=premium(d,arcs,p)
                assert gain == predicted_information_gain(d,arcs,p), (d,arcs,p,gain)
                physical_unknown = physical_prior(6,d,arcs,4-arcs,p)
                physical_revealed = (
                    p*physical_prior(6,d,arcs,4-arcs,Fraction(1))
                    +(1-p)*physical_prior(6,d,arcs,4-arcs,Fraction(0))
                )
                assert unknown == physical_unknown and revealed == physical_revealed, (
                    d,arcs,p,unknown,physical_unknown,revealed,physical_revealed
                )
                tests += 1
    # Global hypothetical ability to choose item *inventory* after the zone
    # becomes known versus actual best single preselected inventory.
    d=46
    p=Fraction(6,29)
    before=optimize(d,p)[0]
    after=(
        p*max(premium(d,a,Fraction(1))[1] for a in range(5))
        +(1-p)*max(premium(d,a,Fraction(0))[1] for a in range(5))
    )
    assert before == Fraction(7,29)
    assert after == Fraction(10,29)
    assert after-before == Fraction(3,29)
    for a in range(1,4):
        assert premium(46,a,Fraction(3,26))[2] == Fraction(1,52)
    print("PASS",tests,"free-zone-information physical policy checks")
    print("d=46, p=3/26, exact gains by Arc count:",
          [str(premium(46,a,Fraction(3,26))[2]) for a in range(5)])
    print("d=46, p=6/29, hypothetical package flexibility ceiling:",
          before,after,after-before)


if __name__=="__main__":
    check()
