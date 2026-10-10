"""Enumerate minimal winning resource coalitions for Mimikyu recovery.

A coalition is a set of *available* actions/effects, not a decklist inclusion
probability. Minimality is tested by exhaustively checking every subset.
"""

from __future__ import annotations

from dataclasses import replace
from itertools import combinations, product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from shadow_rider_post_trifrost_recovery import (  # noqa: E402
    RecoveryScenario, find_recovery
)

RESOURCE_FIELDS = (
    "tulip_available",
    "night_stretcher_available",
    "float_stone_available",
    "guzma_available",
    "acerola_available",
    "underworld_door_enabled",
    "dimension_valley",
)


def resource_set(resources: set[str], baseline: RecoveryScenario) -> RecoveryScenario:
    return replace(
        baseline,
        **{f: f in resources for f in RESOURCE_FIELDS},
    )


def enumerate_minimal_coalitions(
    baseline: RecoveryScenario,
) -> dict[frozenset[str], tuple[str, ...]]:
    candidates = []
    for bitset in product((False, True), repeat=len(RESOURCE_FIELDS)):
        enabled = frozenset(
            name for name, present in zip(RESOURCE_FIELDS, bitset) if present
        )
        solution = find_recovery(resource_set(set(enabled), baseline))
        if solution is not None:
            candidates.append((enabled, solution.actions))
    frontier = {}
    for enabled, actions in candidates:
        if not any(other < enabled for other, _ in candidates):
            frontier[enabled] = actions
    # Proof by exhaustion that every winning set includes a minimal subset,
    # and no recorded frontier has a smaller successful subset.
    assert all(any(key <= enabled for key in frontier)
               for enabled, _ in candidates)
    assert all(not any(other < key for other in frontier)
               for key in frontier)
    return frontier


def main() -> None:
    # Both the knocked-out Mimikyu and two Psychic Energy in discard.
    base = RecoveryScenario(
        psychic_in_hand=0, psychic_in_discard=2,
        opponent_has_bench=True, active_damaged=True,
    )
    first = enumerate_minimal_coalitions(base)
    expected = {
        frozenset(("tulip_available", "float_stone_available",
                   "underworld_door_enabled")),
        frozenset(("tulip_available", "float_stone_available",
                   "dimension_valley")),
    }
    assert set(first) == expected, first

    # Alternative post-KO state: Energy is already in hand, so single-Item
    # Mimikyu retrieval can preserve the Supporter for Guzma or Acerola.
    held_energy = replace(base, psychic_in_hand=2, psychic_in_discard=0)
    second = enumerate_minimal_coalitions(held_energy)
    assert len(second) == 8, second
    for promotion in (
        "float_stone_available", "guzma_available", "acerola_available"
    ):
        for attachment in ("underworld_door_enabled", "dimension_valley"):
            assert frozenset(("night_stretcher_available", promotion,
                              attachment)) in second
    for attachment in ("underworld_door_enabled", "dimension_valley"):
        assert frozenset(("tulip_available", "float_stone_available",
                          attachment)) in second

    without_opp_bench = enumerate_minimal_coalitions(
        replace(held_energy, opponent_has_bench=False)
    )
    assert len(without_opp_bench) == 6
    assert all("guzma_available" not in x for x in without_opp_bench)

    without_active_damage = enumerate_minimal_coalitions(
        replace(held_energy, active_damaged=False)
    )
    assert len(without_active_damage) == 6
    assert all("acerola_available" not in x for x in without_active_damage)

    no_float_tool_slot = enumerate_minimal_coalitions(
        replace(held_energy, active_tool_free=False)
    )
    assert len(no_float_tool_slot) == 4
    assert all("float_stone_available" not in x for x in no_float_tool_slot)

    print(json.dumps({
        "all_discard_minimal_coalitions": [
            sorted(x) for x in sorted(first, key=lambda x: tuple(sorted(x)))
        ],
        "energy_in_hand_minimal_coalitions": [
            sorted(x) for x in sorted(second, key=lambda x: tuple(sorted(x)))
        ],
        "with_no_opponent_bench_count": len(without_opp_bench),
        "with_no_active_damage_count": len(without_active_damage),
        "with_no_empty_active_tool_slot_count": len(no_float_tool_slot),
        "total_subsets_checked_per_scenario": 2 ** len(RESOURCE_FIELDS),
    }, indent=2))


if __name__ == "__main__":
    main()
