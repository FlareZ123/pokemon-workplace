"""SFT: exact late-Wish acquisition and payment-frontier invariants."""
from __future__ import annotations

from collections import Counter
from itertools import combinations
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.aichi_jirachi_payment_frontier import (
    OBJECTIVES, accessible_probability, sample_hit_probability,
    output, simulate, prior_full_deck_search,
)
from tools.aichi_gnh_discard_frontier import paid_gnh_states
from tools.aichi_post_gnh_prize_reset import Prepared, DECK

TM = "Technical Machine: Evolution"
JET = "Jet Energy"


def main() -> None:
    for size in range(1, 11):
        for targets in range(size + 1):
            gold = sum(any(i < targets for i in indices)
                       for indices in combinations(range(size), min(5, size)))
            gold /= comb(size, min(5, size))
            got = sample_hit_probability(size, targets)
            assert abs(got - gold) < 1e-12, (size, targets, got, gold)
    print("PASS: hypergeometric top-five hit probability matches exhaustive combinations")

    h = Counter({"TechSlot1": 1, "TechSlot2": 1})
    d = Counter({"TechSlot1": 2, "TechSlot2": 1, "Other": 7})
    assert accessible_probability(h, d, ("T", "M"), True, "first") == 1
    assert accessible_probability(h, d, ("T", "M"), True, "second") == sample_hit_probability(10, 2)
    assert accessible_probability(h, d, ("T", "M"), False, "second") == 0
    assert accessible_probability(Counter({"TechSlot1": 2}), d, ("T", "M"), True, "second") == sample_hit_probability(10, 1)
    assert accessible_probability(Counter(), d, ("T", "M"), True, "second") == 0
    print("PASS: first and second reset have correct one-card acquisition gates")

    state = Prepared(Counter({"Pidgey": 1, "Faba": 1, "TechSlot1": 1}),
                     Counter({TM: 1, JET: 1}), "Jirachi", (), True)
    payments = paid_gnh_states(state)
    assert len(payments) == 3
    assert any(p.hand["TechSlot1"] == 1 for p in payments)
    assert any(p.hand["TechSlot1"] == 0 for p in payments)
    print("PASS: optional discard payment permits preserving and sacrificing held Ticket")

    # Concrete thinning witness: discard an already-held TM and re-search
    # another copy, preserving the attack output and removing an extra
    # non-Ticket from the deck before late Stellar Wish.
    thinning = Prepared(
        Counter({TM: 1, "Faba": 1, "Gladion": 1, "Pidgey": 1}),
        Counter({TM: 1, JET: 1, "Artazon": 1, "TechSlot1": 1, "Other": 5}),
        "Jirachi", (), True,
    )
    by_payment = {p.paid_with: p for p in paid_gnh_states(thinning)}
    keep_tm = by_payment[("Faba", "Gladion")]
    replace_tm = by_payment[("Faba", TM)]
    assignment = ("T",)
    base = accessible_probability(keep_tm.hand, keep_tm.remaining, assignment, True, "first")
    thinned = accessible_probability(replace_tm.hand, replace_tm.remaining, assignment, True, "first")
    assert keep_tm.hand[TM] == replace_tm.hand[TM] == 1
    assert thinned > base
    assert abs(base - 5 / 7) < 1e-12 and abs(thinned - 5 / 6) < 1e-12
    print("PASS: held-Tool replacement raises legal post-G&H Ticket density")

    # Direct supporter: no full-deck search before the payment.
    order = list(range(len(DECK)))
    first_gnh = next(i for i, card in enumerate(DECK) if card == "Guzma & Hala")
    assert prior_full_deck_search(order, "Jirachi", False)
    order[0], order[first_gnh] = order[first_gnh], order[0]
    assert not prior_full_deck_search(order, "Jirachi", False)
    order[0], order[first_gnh] = order[first_gnh], order[0]
    order[14], order[first_gnh] = order[first_gnh], order[14]
    assert not prior_full_deck_search(order, "Jirachi", False)
    assert prior_full_deck_search(order, "Jirachi", True)
    print("PASS: direct, early-Stellar, deferred-Tag-Call K0/K1 provenance")

    sampled = simulate(raw_trials=2500, seed=20261009)
    assert sampled.accepted > 0 and sampled.core > 0
    for ep in OBJECTIVES:
        assert sampled.paid_endpoint[ep] <= sampled.offered[ep]
    print("PASS: 2,500-start paired Aichi payment and late-Wish regression")
    print(output(sampled))


if __name__ == "__main__":
    main()
