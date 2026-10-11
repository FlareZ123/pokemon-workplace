"""SFT: exact Ticket-multiplicity late Wish gain against physical toy games."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations

from tools.aichi_held_spare_multi_ticket_lift import (
    exact, ticket_at_least_one,
)
from tools.aichi_held_spare_ticket_lift import exact as singleton


def physical(
    n: int, h: int, p: int, basics: int, gnh: int,
    artazon: int, tickets: int,
) -> dict[int,Fraction]:
    """Enumerate accepted seven-equivalent opener, Prize, next-draw worlds."""
    filler = n-1-gnh-4-artazon-tickets
    cards = (("J",)+("S",)*(basics-1)+("G",)*gnh+
             ("TM",)*2+("Jet",)*2+("Art",)*artazon+
             ("Ticket",)*tickets+("Other",)*(filler-(basics-1)))
    assert len(cards) == n
    hit = Counter()
    worlds = 0
    for opener in combinations(range(n),h):
        if not any(cards[i] in ("J","S") for i in opener):
            continue
        outside = tuple(i for i in range(n) if i not in opener)
        for prize in combinations(outside,p):
            deck = tuple(i for i in outside if i not in prize)
            for drawn in deck:
                worlds += 1
                if 0 not in opener:
                    continue
                visible = opener+(drawn,)
                if (not any(cards[i] == "G" for i in visible)
                        or sum(cards[i] == "TM" for i in visible) != 1
                        or sum(cards[i] == "Jet" for i in visible) != 1
                        or any(cards[i] == "Ticket" for i in visible)):
                    continue
                searchable = tuple(i for i in deck if i != drawn)
                if (not any(cards[i] == "TM" for i in searchable)
                        or not any(cards[i] == "Jet" for i in searchable)
                        or not any(cards[i] == "Art" for i in searchable)):
                    continue
                k = sum(cards[i] == "Ticket" for i in searchable)
                hit[k] += 1
    return {k:Fraction(hit[k],worlds) for k in range(tickets+1)}


def main() -> None:
    cases = (
        (12,3,2,2,1,1,1,2),
        (13,3,2,2,2,1,2,2),
        (14,4,2,3,2,2,2,2),
        (14,3,2,3,1,1,3,2),
    )
    for n,h,p,basics,g,a,q,s in cases:
        calculated = exact(q,n,h,p,basics,g,a,s)
        observed = physical(n,h,p,basics,g,a,q)
        assert dict(calculated.available_ticket_masses) == observed
        deck=n-h-1-p
        gain = sum((mass*(
            ticket_at_least_one(deck-3,k,s)
            -ticket_at_least_one(deck-1,k,s))
                    for k,mass in observed.items()),Fraction(0))
        assert calculated.optimistic_accepted_access_gain == gain
    print(f"PASS: {len(cases)} independent physical Prize/opening/draw counts")

    for n in range(5,11):
        for q in range(0,4):
            for s in range(1,4):
                if q > n or s > n:
                    continue
                direct = Fraction(
                    sum(any(i < q for i in subset)
                        for subset in combinations(range(n),s)),
                    sum(1 for _ in combinations(range(n),s)),
                )
                assert ticket_at_least_one(n,q,s) == direct
    print("PASS: independent physical top-card subset geometry")

    expected = (
        Fraction(111113,19535630400),
        Fraction(524926447,54553899079680),
        Fraction(15595805891,1282016628372480),
        Fraction(3118069277,228931540780800),
    )
    computed = tuple(exact(q).optimistic_accepted_access_gain
                     for q in range(1,5))
    assert computed == expected, (computed, expected)
    assert computed[0] == singleton().accepted_start_access_gain
    gains = (computed[0],)+tuple(
        computed[i]-computed[i-1] for i in range(1,len(computed)))
    assert all(gains[i+1] < gains[i] for i in range(3))
    for q,score in enumerate(computed,start=1):
        print(f"Ticket copies {q}: optimistic accepted-start uplift {score} "
              f"= {100*float(score):.12f} percentage points")
    print("PASS: q1..4 exact values, increasing ceilings, decreasing marginal lift")


if __name__ == "__main__":
    main()
