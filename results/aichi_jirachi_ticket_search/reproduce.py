"""Regression for late post-G&H Stellar Wish Item access."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.aichi_jirachi_ticket_search import (
    PACKAGES, output, select_post_gnh_stellar, simulate,
)
from tools.aichi_post_gnh_prize_reset import ENDPOINTS


def main():
    full_top = ((3, "TechSlot1"), (5, "TechSlot2"),
                (7, "TechSlot3"), (8, "TechSlot4"), (9, "Pidgey"))
    no_first = tuple(entry for entry in full_top if entry[1] != "TechSlot1")
    no_first_third = tuple(entry for entry in no_first if entry[1] != "TechSlot3")
    only_fourth = ((8, "TechSlot4"), (9, "Pidgey"))

    assert select_post_gnh_stellar(Counter(), PACKAGES["one_ticket"], full_top) == (3, "TechSlot1")
    assert select_post_gnh_stellar(
        Counter({"TechSlot1": 1}), PACKAGES["two_tickets_no_map"], no_first
    ) is None
    assert select_post_gnh_stellar(
        Counter({"TechSlot1": 1, "TechSlot3": 1}),
        PACKAGES["two_tickets_one_map"], no_first_third
    ) == (5, "TechSlot2")
    assert select_post_gnh_stellar(
        Counter({"TechSlot1": 1, "TechSlot2": 1}),
        PACKAGES["two_tickets_one_map"],
        ((7, "TechSlot3"), (8, "TechSlot4"), (9, "Pidgey"))
    ) == (7, "TechSlot3")
    assert select_post_gnh_stellar(
        Counter({"TechSlot1": 1, "TechSlot2": 1, "TechSlot3": 1}),
        PACKAGES["two_tickets_one_map"], only_fourth
    ) is None

    summary = simulate(raw_trials=15_000, seed=20261008)
    assert 0 < summary.late_stellar_eligible <= summary.core <= summary.accepted
    for package in PACKAGES:
        assert summary.selected[package] <= summary.late_stellar_eligible
        assert (summary.first_item_access_gain[package]
                + summary.second_item_access_gain[package]) <= summary.selected[package]
        for endpoint in ENDPOINTS:
            old = summary.no_stellar_rescue[(package, endpoint)]
            new = summary.late_stellar_rescue[(package, endpoint)]
            helped = summary.late_stellar_helps[(package, endpoint)]
            hurt = summary.late_stellar_hurts[(package, endpoint)]
            assert new - old == helped - hurt
            assert 0 <= old <= summary.core - summary.baseline[endpoint]
            assert 0 <= new <= summary.core - summary.baseline[endpoint]
    assert all(summary.no_stellar_rescue[("baseline", ep)] == 0 for ep in ENDPOINTS)
    print("PASS: realistic held/top-five separation and paired late Stellar effect conservation")
    print(output(summary))


if __name__ == "__main__":
    main()
