"""SFT: exact natural Jirachi/G&H/spare-TM/spare-Jet opportunity."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations

from tools.aichi_held_spare_gnh_opportunity import exact


def physical(
    n: int, h: int, p: int, basics: int, gnh: int, artazon: int,
) -> Fraction:
    """Enumerate ordered opener -> Prize set -> natural draw physical states."""
    filler = n-1-gnh-4-artazon
    cards = (("J",)+("S",)*(basics-1)+("G",)*gnh+
             ("TM",)*2+("Jet",)*2+("Art",)*artazon+
             ("Other",)*(filler-(basics-1)))
    assert len(cards) == n
    wins = trials = 0
    for opener in combinations(range(n),h):
        if not any(cards[i] in ("J","S") for i in opener):
            continue
        rest = tuple(i for i in range(n) if i not in opener)
        for prized in combinations(rest,p):
            deck = tuple(i for i in rest if i not in prized)
            for drawn in deck:
                trials += 1
                if 0 not in opener:
                    continue
                visible = opener+(drawn,)
                if not (any(cards[i] == "G" for i in visible)
                        and sum(cards[i] == "TM" for i in visible) == 1
                        and sum(cards[i] == "Jet" for i in visible) == 1):
                    continue
                searchable = tuple(i for i in deck if i != drawn)
                wins += int(
                    sum(cards[i] == "TM" for i in searchable) >= 1
                    and sum(cards[i] == "Jet" for i in searchable) >= 1
                    and sum(cards[i] == "Art" for i in searchable) >= 1)
    return Fraction(wins,trials)


def main() -> None:
    cases = (
        (11,3,2,2,1,1),
        (12,3,2,3,2,1),
        (13,4,2,3,2,2),
        (12,4,3,3,2,2),
    )
    for args in cases:
        model = exact(*args)
        counted = physical(*args)
        assert model.probability == counted, (args,model.probability,counted)
        assert sum((mass for _,_,mass in model.by_held_gnh_and_artazon),
                   Fraction(0)) == model.probability
    print(f"PASS: {len(cases)} independent physical opening/Prize/draw enumerations")

    real = exact()
    assert real.probability == Fraction(18187043,13418412800)
    assert all(mass >= 0 for _,_,mass in real.by_held_gnh_and_artazon)
    assert sum((mass for _,_,mass in real.by_held_gnh_and_artazon),
               Fraction(0)) == real.probability
    print("PASS: 60-card Aichi named natural-route opportunity",
          real.probability, f"{100*float(real.probability):.12f}% accepted")
    print("This is a necessary configuration, not payoff or strategic discardability.")


if __name__ == "__main__":
    main()
