"""SFT: exact K0/K1 paid G&H cost-value frontier with physical Wish samples."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb

from tools.gnh_prized_spare_information_frontier import (
    CARDS, NAMED, OTHER, gain_distribution, switch_penalty, values, worlds,
)


def grouped_oracle(prizes: int, penalty: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    """Independent named-Prize occupancy plus filler combinatorial weights."""
    keep_total = Fraction(0)
    paid_total = Fraction(0)
    k1_total = Fraction(0)
    denominator = comb(len(CARDS), prizes)
    for subset_size in range(min(prizes,len(NAMED))+1):
        for picked in combinations(NAMED, subset_size):
            filler_prizes = prizes-subset_size
            if not 0 <= filler_prizes <= len(OTHER):
                continue
            weight = Fraction(comb(len(OTHER),filler_prizes),denominator)
            missing = set(picked)
            d = len(CARDS)-prizes
            before = d-int("Artazon" not in missing)
            after = before-int("TM" not in missing)-int("Jet" not in missing)
            keep = Fraction(5,before) if "Ticket" not in missing else Fraction(0)
            paid = Fraction(5,after) if "Ticket" not in missing else Fraction(0)
            keep_total += weight*keep
            paid_total += weight*(paid-penalty)
            k1_total += weight*max(keep, paid-penalty)
    return keep_total, paid_total, k1_total


def literal_wish_hit(prized: tuple[str, ...], extra: bool) -> Fraction:
    """Physically remove searched sources then enumerate every five-subset."""
    blocked = set(prized)|{"Artazon"}
    if extra:
        blocked.update({"TM", "Jet"})
    deck = tuple(c for c in CARDS if c not in blocked)
    all_draws = tuple(combinations(deck, 5))
    return Fraction(sum("Ticket" in drawn for drawn in all_draws),len(all_draws))


def main() -> None:
    for p in range(5):
        threshold = switch_penalty(p)
        assert threshold == Fraction(10,99)
        for penalty in (
            Fraction(0), Fraction(1,18), Fraction(5,72),
            Fraction(1,10), threshold, Fraction(1,8), Fraction(10,63),
            Fraction(1,5),
        ):
            exact = values(p,penalty)
            k,paid,k1 = grouped_oracle(p,penalty)
            assert (k,paid,k1) == (exact.keep,exact.paid_after_cost,exact.k1)
            assert exact.k0 == max(k,paid)
            assert exact.information_value == k1-max(k,paid)
        print(f"PASS: P={p} group oracle and K0 threshold {threshold}")

    tested = 0
    for w in worlds(2):
        assert w.keep == literal_wish_hit(w.prizes,False)
        assert w.pay == literal_wish_hit(w.prizes,True)
        tested += 1
    assert tested == 66
    print("PASS: 66 Prize worlds x literal five-card selection oracle")

    expected = {
        Fraction(0):Fraction(12,66), Fraction(1,18):Fraction(2,66),
        Fraction(5,72):Fraction(16,66), Fraction(1,8):Fraction(8,66),
        Fraction(10,63):Fraction(28,66),
    }
    assert gain_distribution(2) == expected
    v = values(2,Fraction(1,10))
    assert v.keep == Fraction(5,11)
    assert v.paid_after_cost == Fraction(41,90)
    assert v.k0 == Fraction(41,90)
    assert v.k1 == Fraction(1433,2970)
    assert v.information_value == Fraction(8,297)
    at_switch = values(2,Fraction(10,99))
    assert at_switch.information_value == Fraction(179,6534)
    assert values(0,Fraction(10,99)).information_value == 0
    print("PASS: exact P2 lambda=1/10 K0 and K1 values")
    print("PASS: maximum K1 option premium at the K0 action-switch cost")
    print("P2 lambda=1/10 K0:",v.k0,"K1:",v.k1,
          "information premium:",v.information_value)


if __name__ == "__main__":
    main()
