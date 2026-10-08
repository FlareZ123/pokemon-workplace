"""SFT-style regression for G&H discard feasibility and Item protection."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.aichi_post_gnh_prize_reset import Prepared, ENDPOINTS
from tools.aichi_gnh_discard_frontier import (
    paid_gnh_states, output, simulate,
)
from tools.aichi_repeated_ticket_access import PACKAGES


TM = "Technical Machine: Evolution"
JET = "Jet Energy"


def test_payment_pairs():
    no_pay = Prepared(
        Counter({TM: 1, JET: 1, "TechSlot1": 1}),
        Counter({"Artazon": 1}), "Jirachi", (), True,
    )
    paths = paid_gnh_states(no_pay)
    assert len(paths) == 1 and paths[0].paid_with is None
    assert paths[0].hand["TechSlot1"] == 1
    assert paths[0].hand["Artazon"] == 1

    forced = Prepared(
        Counter({"TechSlot1": 1, "Pidgey": 1}),
        Counter({TM: 1, JET: 1, "Artazon": 1}),
        "Jirachi", (), True,
    )
    paths = paid_gnh_states(forced)
    assert len(paths) == 1
    assert paths[0].paid_with == ("Pidgey", "TechSlot1")
    assert paths[0].hand["TechSlot1"] == 0
    assert paths[0].hand[TM] == 1 and paths[0].hand[JET] == 1

    flexible = Prepared(
        Counter({"TechSlot1": 1, "Pidgey": 1, "Faba": 1, "Gladion": 1}),
        Counter({TM: 1, JET: 1, "Artazon": 1}),
        "Jirachi", (), True,
    )
    options = paid_gnh_states(flexible)
    assert len(options) == 6
    assert any(
        p.paid_with == ("Faba", "Gladion")
        and p.hand["TechSlot1"] == 1 and p.hand["Pidgey"] == 1
        for p in options
    )

    duplicate = Prepared(
        Counter({"TechSlot1": 2, "Pidgey": 1}),
        Counter({TM: 1, JET: 1}), "Jirachi", (), True,
    )
    assert any(p.paid_with == ("TechSlot1", "TechSlot1")
               for p in paid_gnh_states(duplicate))

    no_payment = Prepared(
        Counter({"TechSlot1": 1}),
        Counter({TM: 1, JET: 1}), "Jirachi", (), True,
    )
    assert paid_gnh_states(no_payment) == []
    no_tool = Prepared(
        Counter({"Faba": 1, "Gladion": 1}),
        Counter({JET: 1}), "Jirachi", (), True,
    )
    assert paid_gnh_states(no_tool) == []


def main():
    test_payment_pairs()
    result = simulate(raw_trials=15_000, seed=20261008)
    assert 0 < result.payment_feasible <= result.core_offered <= result.accepted
    for endpoint in ENDPOINTS:
        assert 0 <= result.paid_baseline[endpoint] <= result.original_baseline[endpoint]
    for package in PACKAGES:
        assert 0 <= result.paid_first[package] <= result.nominal_first[package]
        assert 0 <= result.paid_second[package] <= result.nominal_second[package]
        assert result.paid_dual_and_first[package] <= result.original_dual_and_first[package]
        assert result.paid_dual_and_second[package] <= result.original_dual_and_second[package]
    print("PASS: no-pay, forced Item sacrifice, duplicate discard, protected pairing, unreachable Tool, and Monte Carlo upper-bound ordering")
    print(output(result))


if __name__ == "__main__":
    main()
