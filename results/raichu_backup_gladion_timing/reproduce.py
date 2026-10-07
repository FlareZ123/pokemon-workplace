"""Reproduce timed backup-Gladion access after K0 visible-copy discard."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from raichu_backup_gladion_timing import backup_gladion_timing


def exhaustive_slot_probability(exposures: int) -> float:
    """Independent labeled-slot enumeration over 50 unresolved positions."""

    successes = 0
    for backup_position in range(50):
        if 5 <= backup_position < 5 + exposures:
            successes += 1
    return successes / 50.0


def main() -> None:
    horizons = (0, 1, 2, 5, 10, 45)
    rows = []

    for exposures in horizons:
        result = backup_gladion_timing(random_exposures=exposures)
        exhaustive = exhaustive_slot_probability(exposures)
        assert abs(result.timed_access_probability - exhaustive) < 1e-12
        assert abs(result.backup_in_deck_probability - 0.9) < 1e-12
        rows.append(
            {
                "random_exposures": exposures,
                "timed_access": result.timed_access_probability,
                "topology_ceiling": result.backup_in_deck_probability,
                "topology_minus_timed": result.topology_minus_timed_access,
            }
        )

    same_turn = backup_gladion_timing(random_exposures=1)
    next_draw = backup_gladion_timing(random_exposures=2)

    assert abs(same_turn.timed_access_probability - 0.02) < 1e-12
    assert abs(next_draw.timed_access_probability - 0.04) < 1e-12
    assert abs(same_turn.topology_minus_timed_access - 0.88) < 1e-12

    print(
        json.dumps(
            {
                "conditioning": {
                    "alolan_raichu_prized": True,
                    "crobat_v_confirmed_in_deck_then_searched_out": True,
                    "visible_gladion_already_discarded": True,
                },
                "backup_gladion_in_deck_probability": 0.9,
                "same_turn_dark_asset_one_draw_access": 0.02,
                "through_next_natural_draw_two_exposures": 0.04,
                "deterministic_preserving_connector_ceiling": 0.9,
                "horizons": rows,
                "exhaustive_labeled_slot_validation": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
