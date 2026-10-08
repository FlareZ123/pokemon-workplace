"""Targeted tests for preserving a later Stellar Wish via redundant connector substitution."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.aichi_post_gnh_prize_reset import DECK, prepare
from tools.aichi_jirachi_ticket_search import (
    output, prepare_with_deferred_stellar, simulate,
)


def make_order(opening: tuple[str, ...], draw: str, wish_top: tuple[str, ...]) -> list[int]:
    used: set[int] = set()

    def take(name: str) -> int:
        for i, card in enumerate(DECK):
            if card == name and i not in used:
                used.add(i)
                return i
        raise AssertionError(f"missing physical card: {name}")

    selected_opening = [take(name) for name in opening]
    selected_draw = take(draw)
    selected_top = [take(name) for name in wish_top]
    prizes = [i for i in range(len(DECK)) if i not in used][:6]
    used.update(prizes)
    result = selected_opening + prizes + [selected_draw] + selected_top + [
        i for i in range(len(DECK)) if i not in used
    ]
    assert sorted(result) == list(range(len(DECK)))
    return result


def check_connector_defer():
    extra = ("TechSlot1", "TechSlot2", "TechSlot3", "TechSlot4", "Gladion")
    rest = ("Pidgeotto", "Gloom", "Herdier", "Oddish")
    cases = (
        (("Jirachi", "Guzma & Hala") + extra, "Guzma & Hala"),
        (("Jirachi", "Guzma & Hala") + extra, "Tag Call"),
        (("Jirachi", "Tag Call") + extra, "Guzma & Hala"),
        (("Jirachi", "Tag Call") + extra, "Tag Call"),
    )

    for opening, early_pick in cases:
        order = make_order(opening, "Faba", (early_pick,) + rest)
        original = prepare(order)
        revised, deferred = prepare_with_deferred_stellar(order)
        assert original is not None and revised is not None and deferred
        assert original.gnh_access == revised.gnh_access
        assert original.prizes == revised.prizes
        assert original.active == revised.active == "Jirachi"
        assert all(value >= 0 for value in revised.hand.values())
        assert all(value >= 0 for value in revised.remaining.values())
        if "Guzma & Hala" in opening:
            assert revised.hand[early_pick] == original.hand[early_pick] - 1
            assert revised.remaining[early_pick] == original.remaining[early_pick] + 1
        elif early_pick == "Guzma & Hala":
            assert revised.hand["Tag Call"] == original.hand["Tag Call"] - 1
            assert revised.remaining == original.remaining
        else:
            assert revised.hand["Tag Call"] == original.hand["Tag Call"] - 1
            assert revised.remaining["Tag Call"] == original.remaining["Tag Call"] + 1

    no_direct = ("Jirachi",) + extra + ("Lusamine",)
    order = make_order(no_direct, "Faba", ("Guzma & Hala",) + rest)
    revised, deferred = prepare_with_deferred_stellar(order)
    assert not deferred and revised == prepare(order)


def main():
    check_connector_defer()
    base = simulate(raw_trials=15_000, seed=20261008)
    deferred = simulate(raw_trials=15_000, seed=20261008,
                        defer_redundant_stellar=True)
    assert deferred.core == base.core
    assert deferred.accepted == base.accepted
    assert deferred.late_stellar_eligible >= base.late_stellar_eligible
    assert deferred.late_stellar_rescue[("baseline", "dual_stage2")] == 0
    print("PASS: four physical connector substitutions, genuine no-connector counterexample, and deferred Jirachi simulation")
    print("initial Ability-available count:", base.late_stellar_eligible)
    print("with redundant early connector deferred:", deferred.late_stellar_eligible)
    print(output(deferred))


if __name__ == "__main__":
    main()
