"""Single-file correctness checks for continuation-aware generic Energy payments."""
from __future__ import annotations

from itertools import product
from pathlib import Path

from tools.energy_discard_continuation_frontier import build, irredundant_discard_sets


def independent_irredundant_oracle(units: tuple[int, ...], cost: int) -> set[tuple[int, ...]]:
    target = min(cost, sum(units))
    if cost == 0:
        return {()}
    solutions = set()
    for mask in range(1 << len(units)):
        chosen = tuple(i for i in range(len(units)) if mask & (1 << i))
        paid = sum(units[i] for i in chosen)
        if paid < target:
            continue
        if all(paid - units[i] < target for i in chosen):
            solutions.add(chosen)
    return solutions


def verify() -> dict[str, int]:
    checked = 0
    for count in range(1, 6):
        for units in product((1, 2, 3), repeat=count):
            cards = [{"units": u} for u in units]
            for cost in range(8):
                actual = set(irredundant_discard_sets(cards, cost))
                expected = independent_irredundant_oracle(units, cost)
                assert actual == expected, (units, cost, actual ^ expected)
                checked += 1

    payload = build(Path("resources"))
    scan = payload["three_basic_type_multiset_scan"]
    assert scan["all_triples"] == 165
    assert scan["initial_apex_ready"] == 81
    assert scan["minimum_card_breaks_but_two_cards_preserve_apex"] == 80
    assert scan["minimum_card_preserves_apex"] == 1
    assert payload["summary"]["minimum_card_payments_retaining_apex"] == 0
    assert payload["summary"]["two_card_payments_retaining_apex"] == 3
    return {"unit_payment_state_checks": checked, **scan}


if __name__ == "__main__":
    report = verify()
    for key, value in report.items():
        print(f"{key}: {value}")
    print("PASS")
