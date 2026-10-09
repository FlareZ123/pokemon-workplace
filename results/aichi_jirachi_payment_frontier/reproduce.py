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
    output, simulate,
)
from tools.aichi_gnh_discard_frontier import paid_gnh_states
from tools.aichi_post_gnh_prize_reset import Prepared

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

    sampled = simulate(raw_trials=2500, seed=20261009)
    assert sampled.accepted > 0 and sampled.core > 0
    for ep in OBJECTIVES:
        assert sampled.paid_endpoint[ep] <= sampled.offered[ep]
    print("PASS: 2,500-start paired Aichi payment and late-Wish regression")
    print(output(sampled))


if __name__ == "__main__":
    main()
