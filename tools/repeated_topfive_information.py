"""Repeated Rotom and Pokédex target discovery before Arc -> Peonia.

Models a single target T in a shuffled deck, with Rotom Phone's reshuffle
after every failed five-card observation. A held Pokédex may inspect one last
fresh group, but repeated Pokédex alone cannot refresh that group.
"""
from fractions import Fraction
from functools import lru_cache
from math import comb

from tools.rotom_arc_peonia_incidence import assert_card_text, with_top_five


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def lookup_success(deck_size, rotoms, pokedex):
    """P(find unique T with held top-five Items | T uniformly in deck)."""
    if deck_size < 1 or min(rotoms,pokedex) < 0:
        raise ValueError("Invalid deck or held Item counts")
    depth = min(deck_size,5)
    q = (rotoms+int(pokedex>0)) if rotoms else int(pokedex>0)
    if q == 0:
        return Fraction(1,deck_size)  # Arc alone sees immediate top.
    if depth == deck_size:
        return Fraction(1)
    # Initial Rotom/Pokédex probe sees five unknown positions. After a
    # failed Rotom the retained non-T top is fixed; shuffle makes the T
    # uniformly random among the remaining deck_size-1 positions.
    survival = (Fraction(deck_size-depth,deck_size)
                * Fraction(deck_size-depth,deck_size-1)**(q-1))
    return 1-survival


def position_oracle(deck_size, rotoms, pokedex):
    """Independent exact physical-position transition, no closed formula."""
    depth = min(5,deck_size)

    @lru_cache(None)
    def value(position,r,d):
        if r:
            if position < depth:
                return Fraction(1)
            # Miss: choose a known non-target top card and shuffle the
            # other four with the deck tail. Each target position 1..L-1
            # is equally possible for the next physical deck ordering.
            return sum((value(pos,r-1,d) for pos in range(1,deck_size)),
                       Fraction()) / (deck_size-1)
        if d:
            return Fraction(int(position < depth))
        return Fraction(int(position == 0))

    return sum((value(pos,rotoms,pokedex)
                for pos in range(deck_size)),Fraction()) / deck_size


def exact_opening(starters=12, arcs=4, peonias=2, rotoms=4,
                  pokedex=0, disposable=None, total=60, opening=7, prizes=6):
    """Conditional raw access event with repeated held top-five Items."""
    if disposable is None:
        disposable=total-starters-arcs-peonias-rotoms-pokedex-1
    protected=total-starters-arcs-peonias-rotoms-pokedex-disposable-1
    if min(starters,arcs,peonias,rotoms,pokedex,disposable,protected)<0:
        raise ValueError("Invalid disjoint physical-card partition")
    deck_size=total-opening-prizes-1
    if deck_size < 1:
        raise ValueError("No deck top after ordinary turn draw")
    unseen=total-opening-1
    valid=Fraction(choose(total,opening)-choose(total-starters,opening),
                   choose(total,opening))
    if not valid:
        raise ValueError("No Basic opening")
    event=Fraction()
    seen=opening+1
    for b in range(1,min(starters,seen)+1):
        for a in range(1,min(arcs,seen-b)+1):
            for p in range(1,min(peonias,seen-b-a)+1):
                for r in range(0,min(rotoms,seen-b-a-p)+1):
                    for d in range(0,min(pokedex,seen-b-a-p-r)+1):
                        for f in range(1,min(disposable,seen-b-a-p-r-d)+1):
                            o=seen-b-a-p-r-d-f
                            if not 0 <= o <= protected:
                                continue
                            mass = Fraction(
                                choose(starters,b)*choose(arcs,a)
                                *choose(peonias,p)*choose(rotoms,r)
                                *choose(pokedex,d)*choose(disposable,f)
                                *choose(protected,o),
                                choose(total,seen)
                            )
                            opener_factor=Fraction(opening,seen) if b==1 else 1
                            # T absent hand; it lies in the live deck with
                            # probability deck_size/unseen (else Prized).
                            # The q=0 term already accounts for Arc top1.
                            success=Fraction(deck_size,unseen)*lookup_success(
                                deck_size,r,d
                            )
                            event+=mass*opener_factor*success/valid
    return event


def run():
    assert_card_text()
    for size in (5,6,7,12,46):
        for r in range(5):
            for d in range(3):
                formula=lookup_success(size,r,d)
                enumerated=position_oracle(size,r,d)
                assert formula==enumerated,(size,r,d,formula,enumerated)
    # When an Arc alone is used, the conditional chance T in the first
    # unknown top position is 1/unseen: the deck/prize split is respected.
    expected_rotom_only=(
        Fraction(345378629,215366137272),
        Fraction(20123651,8973589053),
        Fraction(0), # computed separately for >=2 as repeated improvements
        Fraction(0),
        Fraction(26990286436963,6541746419637000),
    )
    for copies in (0,1,4):
        actual=exact_opening(rotoms=copies)
        assert actual==expected_rotom_only[copies]
    for r,d,numerator,denominator in (
        (0,4,830344565,215366137272),
        (1,3,1431598043,358943562120),
        (2,2,1197995657,293681096280),
        (3,1,26990286436963,6541746419637000),
        (4,0,26990286436963,6541746419637000),
        (4,4,1244995684883,198234739989000),
    ):
        actual=exact_opening(rotoms=r,pokedex=d)
        assert actual==Fraction(numerator,denominator),(r,d,actual)
        print(f"Rotom={r} Pokédex={d}: {float(actual):.9%}")
    # Previous one-probe top-five approximation is a strict lower bound.
    assert (exact_opening(rotoms=4,pokedex=0)
            > with_top_five(arrangers=4))
    assert (exact_opening(rotoms=4,pokedex=4)
            > with_top_five(arrangers=8))
    print("75 exact positional oracles and 9 population assertions pass.")


if __name__ == "__main__":
    run()
