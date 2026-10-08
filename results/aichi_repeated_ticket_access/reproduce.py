"""Regression for first-turn post-G&H Ticket/Town Map alternative slot packages."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.aichi_repeated_ticket_access import (
    PACKAGES, deck_after_tickets, output, package_items, simulate,
)


def main() -> None:
    source = Counter({"B": 1, "C": 1, "F": 10})
    order = ("B", "F", "C") + ("F",) * 9
    old = ("A", "X")
    one = deck_after_tickets(source, old, order, 1)
    two = deck_after_tickets(source, old, order, 2)
    assert one["B"] == 0 and one["C"] == 1
    assert two["B"] == 1 and two["C"] == 0
    assert one["A"] == two["A"] == 1
    assert sum(one.values()) == sum(two.values()) == sum(source.values())
    try:
        deck_after_tickets(source, old, order, 7)
        assert False, "should reject exhausting untouched topdeck"
    except ValueError:
        pass

    hand = Counter({"TechSlot1": 1, "TechSlot2": 1, "TechSlot3": 1, "TechSlot4": 1})
    assert package_items(hand, PACKAGES["one_ticket"]) == (1, 0)
    assert package_items(hand, PACKAGES["two_tickets_one_map"]) == (2, 1)
    assert package_items(hand, PACKAGES["three_tickets_one_map"]) == (3, 1)

    summary = simulate(raw_trials=20_000, seed=20261008)
    assert 0 < summary.core_ready <= summary.accepted <= summary.raw_trials
    for endpoint, baseline in summary.baseline.items():
        assert 0 <= baseline <= summary.core_ready
        assert summary.rescue[("one_ticket", endpoint)] == summary.rescue[("one_ticket_one_map", endpoint)]
        assert summary.rescue[("one_ticket", endpoint)] <= summary.rescue[("two_tickets_no_map", endpoint)]
        assert summary.rescue[("two_tickets_no_map", endpoint)] <= summary.rescue[("two_tickets_one_map", endpoint)]
        assert summary.rescue[("two_tickets_one_map", endpoint)] <= summary.rescue[("two_tickets_two_maps", endpoint)]
        assert summary.rescue[("one_ticket", endpoint)] + baseline <= summary.core_ready
        for package in PACKAGES:
            assert 0 <= summary.second_reset_rescue[(package, endpoint)] <= summary.rescue[(package, endpoint)]
    assert summary.access_second["two_tickets_no_map"] == 0
    assert summary.access_second["two_tickets_two_maps"] >= summary.access_second["two_tickets_one_map"]
    print("PASS: physical two-block transition, package roles, resource-access order, and paired endpoint monotonicity")
    print(output(summary))


if __name__ == "__main__":
    main()
