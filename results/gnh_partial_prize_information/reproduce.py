"""SFT: exact G&H partial-Prize signals against physical labeled cards."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from math import comb

from tools.gnh_partial_prize_observability import NAMES, optimize
from tools.gnh_large_unseen_information_frontier import calculate


def physical_value(
    unseen: int, prizes: int, inspect: int, penalty: Fraction,
    observed: tuple[str, ...],
) -> Fraction:
    """Independent oracle: deal labeled Prizes and enumerate Stellar Wish subsets."""
    cards = NAMES + tuple(f"Filler{i}" for i in range(unseen-4))
    states: dict[tuple[bool, ...], list[Fraction]] = defaultdict(
        lambda: [Fraction(), Fraction()]
    )
    n_worlds = 0
    for picked in combinations(cards, prizes):
        prize_set = set(picked)
        remaining = tuple(name for name in cards if name not in prize_set)
        kept = tuple(name for name in remaining if name != "Artazon")
        paid = tuple(name for name in kept if name not in ("TM", "Jet"))
        hit_keep = sum("Ticket" in chosen for chosen in combinations(kept, inspect))
        hit_pay = sum("Ticket" in chosen for chosen in combinations(paid, inspect))
        keep_value = Fraction(hit_keep, comb(len(kept), inspect))
        paid_value = Fraction(hit_pay, comb(len(paid), inspect)) - penalty
        signal = tuple(name in prize_set for name in observed)
        states[signal][0] += keep_value
        states[signal][1] += paid_value
        n_worlds += 1
    return sum((max(keep, pay) for keep, pay in states.values()),
               Fraction()) / n_worlds


def main() -> None:
    signals = [subset for size in range(5) for subset in combinations(NAMES, size)]
    tested = 0
    for unseen in range(7, 10):
        for prizes in range(3):
            for inspect in (1, 2):
                for penalty in (Fraction(0), Fraction(1, 100), Fraction(1, 10)):
                    vals = {}
                    for observed in signals:
                        exact = optimize(unseen, prizes, inspect, penalty, observed)
                        brute = physical_value(unseen, prizes, inspect, penalty, observed)
                        assert exact.value == brute, (unseen, prizes, inspect, penalty, observed)
                        vals[frozenset(observed)] = exact.value
                        tested += 1
                    for subset, value in vals.items():
                        for larger, expanded_value in vals.items():
                            if subset <= larger:
                                assert value <= expanded_value
                    previous = calculate(unseen, prizes, inspect, penalty)
                    assert vals[frozenset()] == previous.k0
                    assert vals[frozenset(NAMES)] == previous.k1
    print(f"PASS: {tested} exact partial-observation policy/physical-label comparisons")

    unseen, prizes, inspect = 52, 6, 5
    price = Fraction(10, 2499)
    empty = optimize(unseen, prizes, inspect, price)
    full = optimize(unseen, prizes, inspect, price, NAMES)
    assert empty.value == Fraction(5, 51)
    assert full.value == Fraction(25989, 262990)
    assert full.value-empty.value == Fraction(617, 788970)
    known_ticket = optimize(unseen, prizes, inspect, price, ("Ticket",))
    known_tm = optimize(unseen, prizes, inspect, price, ("TM",))
    known_tm_jet = optimize(unseen, prizes, inspect, price, ("TM", "Jet"))
    known_tm_ticket = optimize(unseen, prizes, inspect, price, ("TM", "Ticket"))
    known_three = optimize(unseen, prizes, inspect, price, ("TM", "Jet", "Ticket"))
    assert known_ticket.value-empty.value == Fraction(5, 10829)
    assert known_tm.value-empty.value == Fraction(1, 4420)
    assert known_tm_jet.value-empty.value == Fraction(173, 424830)
    assert known_tm_ticket.value-empty.value == Fraction(7099, 11045580)
    assert known_three.value == full.value
    for signals_subset in signals:
        if len(signals_subset) < 3:
            assert optimize(unseen, prizes, inspect, price, signals_subset).value < full.value
    for signal, action in known_three.actions.items():
        assert (action == "pay") == (signal == (False, False, False))
    for signal, action in full.actions.items():
        assert (action == "pay") == (signal[1:] == (False, False, False))
    assert Fraction(1, 396) < price < Fraction(5, 1012)
    for test_price in (Fraction(3, 1000), Fraction(4, 1000)):
        three = optimize(unseen, prizes, inspect, test_price, ("TM", "Jet", "Ticket"))
        all_four = optimize(unseen, prizes, inspect, test_price, NAMES)
        assert three.value == all_four.value
        assert sum(action == "pay" for action in three.actions.values()) == 1
    counterprice = Fraction(1, 405)
    assert (optimize(unseen, prizes, inspect, counterprice, ("TM", "Jet", "Ticket")).value <
            optimize(unseen, prizes, inspect, counterprice, NAMES).value)
    print("PASS: U52/P6 three-card sufficient signals, minimal named subset, exact fractions")
    print("PASS: Artazon status irrelevant inside calibrated interval, relevant outside")
    print("K0", empty.value, "K1", full.value, "information premium", full.value-empty.value)


if __name__ == "__main__":
    main()
