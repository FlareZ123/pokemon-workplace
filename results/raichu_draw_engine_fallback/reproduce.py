"""Seeded regression for the Harto Raichu draw-engine fallback simulation."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from raichu_draw_engine_fallback import (
    CROBAT,
    DEDENNE,
    DECK_COUNTS,
    GIRATINA,
    OTHER_STARTER,
    SQUAWK,
    simulate,
)
from raichu_draw_engine_profiles import compile_raichu_draw_engine_profiles


def main() -> None:
    profiles = {
        profile.name: profile
        for profile in compile_raichu_draw_engine_profiles(ROOT / "resources")
    }
    assert profiles["Crobat V"].hand_effect == "draw_to_six"
    assert profiles["Crobat V"].forest_seal_host
    assert profiles["Dedenne-GX"].hand_effect == "discard_hand_draw_six"
    assert not profiles["Dedenne-GX"].first_turn_only
    assert profiles["Squawkabilly ex"].hand_effect == "discard_hand_draw_six"
    assert profiles["Squawkabilly ex"].first_turn_only

    assert int(DECK_COUNTS.sum()) == 60
    assert int(
        DECK_COUNTS[CROBAT]
        + DECK_COUNTS[DEDENNE]
        + DECK_COUNTS[SQUAWK]
        + DECK_COUNTS[GIRATINA]
        + DECK_COUNTS[OTHER_STARTER]
    ) == 16

    result = simulate(samples=1_000_000, seed=20261008)

    assert abs(
        result["branch_given_valid"]
        - result["exact_observable_branch_given_valid"]
    ) < 0.0015
    assert abs(
        result["paired_sample_baseline"]
        - result["exact_existing_combined_visible_baseline"]
    ) < 0.015

    assert 0.115 < result["paired_gain_non_first_turn"] < 0.130
    assert 0.117 < result["paired_gain_first_turn"] < 0.132
    assert 0.0012 < result["squawk_first_turn_increment"] < 0.0025

    nonfirst_attribution = sum(
        result["gain_attribution_non_first_turn"].values()
    )
    first_attribution = sum(result["gain_attribution_first_turn"].values())
    assert abs(
        nonfirst_attribution - result["paired_gain_non_first_turn"]
    ) < 1e-12
    assert abs(first_attribution - result["paired_gain_first_turn"]) < 1e-12

    assert (
        result["gain_attribution_first_turn"]["dedenne_deck"] > 0.10
    )
    assert result["calibrated_first_turn"] > result["calibrated_non_first_turn"]

    print(json.dumps(result, indent=2, sort_keys=True))
    print("Raichu draw-engine fallback regression: PASS")


if __name__ == "__main__":
    main()
