"""Reproduce the multi-copy zone-state counterexample and combinatorics."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from multicopy_zone_state import (  # noqa: E402
    ZoneCountState,
    exchangeable_distribution_count,
    single_zone_map_capacity,
)


def main() -> None:
    # A single name -> zone map silently collapses repeated keys.
    collapsed = dict(
        [
            ("Quick Ball", "hand"),
            ("Quick Ball", "deck"),
        ]
    )
    assert collapsed == {"Quick Ball": "deck"}

    state = ZoneCountState.from_mapping(
        {
            ("Quick Ball", "hand"): 1,
            ("Quick Ball", "deck"): 1,
            ("Tapu Lele-GX", "deck"): 1,
        }
    )
    assert state.total("Quick Ball") == 2
    assert state.count("Quick Ball", "hand") == 1
    assert state.count("Quick Ball", "deck") == 1

    after_play = state.move("Quick Ball", "hand", "discard")
    assert after_play.total("Quick Ball") == 2
    assert after_play.count("Quick Ball", "hand") == 0
    assert after_play.count("Quick Ball", "deck") == 1
    assert after_play.count("Quick Ball", "discard") == 1

    # Four exchangeable copies distributed across deck/hand/Prize/discard have
    # C(7,3)=35 count states. A one-zone value has only four representable values.
    four_copy_states = exchangeable_distribution_count(4, 4)
    assert four_copy_states == 35
    assert single_zone_map_capacity(4) == 4

    # Ten exchangeable Energy across five zones already have 1001 count vectors.
    ten_energy_states = exchangeable_distribution_count(10, 5)
    assert ten_energy_states == 1001
    assert single_zone_map_capacity(5) == 5

    print(
        json.dumps(
            {
                "quick_ball_copies_preserved": after_play.total("Quick Ball"),
                "quick_ball_zone_counts_after_play": dict(
                    after_play.zone_counts("Quick Ball")
                ),
                "four_copies_four_zones_count_states": four_copy_states,
                "four_zone_single_value_capacity": single_zone_map_capacity(4),
                "ten_copies_five_zones_count_states": ten_energy_states,
                "five_zone_single_value_capacity": single_zone_map_capacity(5),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
