"""SFT: material-price-ignored upper bound on first Ticket Wish gain."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations

from tools.aichi_held_spare_ticket_lift import exact


def physical(
    n: int, h: int, p: int, basics: int, gnh: int, art: int,
) -> Fraction:
    """Independent opening, Prize placement, and natural draw enumeration."""
    filler = n-1-gnh-4-art-1
    cards = (("J",)+("S",)*(basics-1)+("G",)*gnh+
             ("TM",)*2+("Jet",)*2+("Art",)*art+
             ("Ticket",)+("Other",)*(filler-(basics-1)))
    assert len(cards) == n
    favorable = total = 0
    for opener in combinations(range(n),h):
        if not any(cards[i] in ("J","S") for i in opener):
            continue
        residual = tuple(i for i in range(n) if i not in opener)
        for prized in combinations(residual,p):
            deck = tuple(i for i in residual if i not in prized)
            for drawn in deck:
                total += 1
                if 0 not in opener:
                    continue
                visible = opener+(drawn,)
                if not (any(cards[i] == "G" for i in visible)
                        and sum(cards[i] == "TM" for i in visible) == 1
                        and sum(cards[i] == "Jet" for i in visible) == 1):
                    continue
                searchable = tuple(i for i in deck if i != drawn)
                favorable += int(
                    any(cards[i] == "TM" for i in searchable)
                    and any(cards[i] == "Jet" for i in searchable)
                    and any(cards[i] == "Art" for i in searchable)
                    and any(cards[i] == "Ticket" for i in searchable))
    return Fraction(favorable,total)


def main() -> None:
    cases = (
        (12,3,2,2,2,1,2),
        (13,3,2,3,2,2,2),
        (13,4,2,3,2,2,2),
        (14,4,3,3,2,2,2),
    )
    for values in cases:
        n,h,p,basics,g,a,s=values
        modeled = exact(n,h,p,basics,g,a,s)
        independent = physical(n,h,p,basics,g,a)
        assert modeled.ticket_searchable_mass == independent, (
            values,modeled.ticket_searchable_mass,independent)
        assert (modeled.accepted_start_access_gain ==
                independent*modeled.conditional_access_gain)
    print(f"PASS: {len(cases)} independent physical Prize/draw/opening cases")

    x = exact()
    assert x.opportunity_mass == Fraction(18187043,13418412800)
    assert x.ticket_searchable_mass == Fraction(4777859,4341251200)
    assert x.ticket_searchable_given_opportunity == Fraction(7062922,8698151)
    assert x.conditional_access_gain == Fraction(2,387)
    assert x.accepted_start_access_gain == Fraction(111113,19535630400)
    print("PASS: natural named line with Ticket in deck:",
          x.ticket_searchable_mass)
    print("PASS: optimistic direct first-Wish Ticket gain across accepted starts:",
          x.accepted_start_access_gain,
          f"{100*float(x.accepted_start_access_gain):.12f} percentage points")


if __name__ == "__main__":
    main()
