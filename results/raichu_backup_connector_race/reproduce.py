"""Reproduce the conditioned one-draw backup-Gladion connector race."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from raichu_backup_connector_race import backup_connector_race


PRIZE_POSITIONS = frozenset(range(5))
TOP_DECK_POSITION = 5
DECK_POSITIONS = frozenset(range(5, 50))


def exhaustive(computer_gate: bool, forest_gate: bool) -> float:
    success = 0
    total = 0

    for backup in range(50):
        for computer in range(50):
            if computer == backup:
                continue
            for forest in range(50):
                if forest in {backup, computer}:
                    continue
                total += 1

                direct = backup == TOP_DECK_POSITION
                via_computer = (
                    computer_gate
                    and computer == TOP_DECK_POSITION
                    and backup in DECK_POSITIONS
                )
                via_forest = (
                    forest_gate
                    and forest == TOP_DECK_POSITION
                    and backup in DECK_POSITIONS
                )
                if direct or via_computer or via_forest:
                    success += 1

    return success / total


def main() -> None:
    cases = {}
    for computer_gate, forest_gate, label in (
        (False, False, "direct_only"),
        (True, False, "computer_only"),
        (False, True, "forest_only"),
        (True, True, "both_connectors"),
    ):
        result = backup_connector_race(
            computer_gate_live=computer_gate,
            forest_seal_gate_live=forest_gate,
        )
        exact = exhaustive(computer_gate, forest_gate)
        assert abs(result.union_access - exact) < 1e-12
        cases[label] = {
            "access": result.union_access,
            "topology_ceiling": result.backup_in_deck_ceiling,
            "topology_minus_access": result.topology_minus_union,
        }

    both = backup_connector_race()
    assert abs(both.direct_backup_draw - 0.02) < 1e-12
    assert abs(
        both.computer_search_rescue - 0.017959183673469388
    ) < 1e-12
    assert abs(
        both.forest_seal_rescue - 0.017959183673469388
    ) < 1e-12
    assert abs(both.union_access - 0.05591836734693877) < 1e-12
    assert abs(both.backup_in_deck_ceiling - 0.9) < 1e-12

    print(
        json.dumps(
            {
                "direct_backup_draw": both.direct_backup_draw,
                "computer_search_marginal": both.computer_search_rescue,
                "forest_seal_marginal": both.forest_seal_rescue,
                "both_connectors_union": both.union_access,
                "backup_in_deck_ceiling": both.backup_in_deck_ceiling,
                "still_stranded_relative_to_topology": both.topology_minus_union,
                "cases": cases,
                "exhaustive_distinct_position_validation": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
