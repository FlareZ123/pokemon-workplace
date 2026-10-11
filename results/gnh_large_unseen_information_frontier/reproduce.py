"""SFT: scalable grouped G&H K0/K1 frontier vs labeled physical oracle."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations

from tools.gnh_large_unseen_information_frontier import calculate
from tools.gnh_prized_spare_information_frontier import worlds, values


def brute(unseen: int, prizes: int, seen: int, penalty: Fraction) -> tuple[
    Fraction, Fraction, Fraction
]:
    """Physical labeled Prize subsets, with independent postsearch deck sizes."""
    names = ("Artazon","TM","Jet","Ticket")
    cards = names + tuple(f"Other{i}" for i in range(unseen-len(names)))
    keep_total = paid_total = oracle_total = Fraction(0)
    count = 0
    for chosen in combinations(cards,prizes):
        deck = [name for name in cards if name not in chosen]
        baseline = [name for name in deck if name != "Artazon"]
        extended = [name for name in baseline if name not in ("TM","Jet")]
        keep = Fraction(seen,len(baseline)) if "Ticket" in baseline else Fraction(0)
        paid = Fraction(seen,len(extended)) if "Ticket" in extended else Fraction(0)
        keep_total += keep
        paid_total += paid-penalty
        oracle_total += max(keep,paid-penalty)
        count += 1
    return keep_total/count, paid_total/count, oracle_total/count


def main() -> None:
    tested = 0
    for u in range(6,12):
        for p in range(min(4,u-4)+1):
            for seen in range(1,min(4,u-3-p)+1):
                for cost in (Fraction(0),Fraction(1,100),Fraction(1,10)):
                    result = calculate(u,p,seen,cost)
                    baseline,paid,oracle = brute(u,p,seen,cost)
                    assert (result.keep,result.paid_after_cost,result.k1) == (
                        baseline,paid,oracle)
                    tested += 1
    print(f"PASS: {tested} fully enumerated physical Prize/cost/search configurations")

    for p in range(5):
        for cost in (Fraction(0),Fraction(1,10),Fraction(10,99)):
            result = calculate(12,p,5,cost)
            other = values(p,cost)
            assert (result.keep,result.paid_after_cost,result.k0,result.k1) == (
                other.keep,other.paid_after_cost,other.k0,other.k1)
    print("PASS: generalized grouped solver matches old 12-card labeled model")

    premiums = []
    for p in range(7):
        x = calculate(52,p,5,Fraction(10,2499))
        assert x.keep == Fraction(5,51)
        assert x.paid_after_cost == Fraction(5,49)-Fraction(10,2499)
        assert x.switch_penalty == Fraction(10,2499)
        premiums.append(x.information_value)
    assert premiums == sorted(premiums)
    six = calculate(52,6,5,Fraction(10,2499))
    assert six.information_value == Fraction(617,788970)
    assert six.k1 == Fraction(25989,262990)
    eighteen = calculate(18,6,5,Fraction(2,51))
    assert eighteen.information_value == Fraction(335,20808)
    print("PASS: U52/P6 exact K0/K1 access 5/51 -> 25989/262990")
    print("PASS: six-Prize conditional information premium 617/788970")
    print("PASS: monotone P=0..6 information premium in this specific 52-card toy")


if __name__ == "__main__":
    main()
