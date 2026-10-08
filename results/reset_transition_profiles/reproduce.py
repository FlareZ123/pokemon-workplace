"""Reproduce typed full-hand reset transition profiles."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from compile_reset_transition_profiles import compile_reset_transition_profiles


def main() -> None:
    profiles = compile_reset_transition_profiles(ROOT / "resources")
    assert len(profiles) == 15

    source_counts = Counter(profile.source_kind for profile in profiles)
    assert source_counts == Counter({"trainer": 5, "ability": 6, "attack": 4})

    assert sum(profile.ends_turn for profile in profiles) == 5
    assert sum(profile.fresh_hand_actionable_same_turn for profile in profiles) == 10
    assert sum(profile.supporter_cost for profile in profiles) == 5
    assert sum(profile.requires_bench_slot for profile in profiles) == 1
    assert sum(profile.deck_position_sensitive for profile in profiles) == 1
    assert sum(
        profile.draw_position_source == "top_or_bottom_choice"
        for profile in profiles
    ) == 1

    resources = Counter(profile.once_per_game_resource for profile in profiles)
    assert resources["vstar_power"] == 1
    assert resources["gx_attack"] == 1

    first_turn = Counter(profile.first_turn_rule for profile in profiles)
    assert first_turn["first_turn_only"] == 1
    assert first_turn["going_first_exception"] == 3
    assert first_turn["none"] == 11

    by_name = {profile.name: profile for profile in profiles}

    dede = by_name["Dedenne-GX"]
    assert dede.source_gate == "hand_to_bench"
    assert dede.requires_bench_slot
    assert dede.draw_count == 6

    squawk = by_name["Squawkabilly ex"]
    assert squawk.first_turn_rule == "first_turn_only"
    assert squawk.fresh_hand_actionable_same_turn

    zoroark = by_name["Hisuian Zoroark VSTAR"]
    assert zoroark.once_per_game_resource == "vstar_power"

    zamazenta = by_name["Zamazenta V"]
    assert zamazenta.ends_turn
    assert not zamazenta.fresh_hand_actionable_same_turn

    ray_gx = by_name["Rayquaza-GX"]
    assert ray_gx.once_per_game_resource == "gx_attack"
    assert ray_gx.ends_turn

    ingo = by_name["Ingo & Emmet"]
    assert ingo.supporter_cost
    assert ingo.deck_position_sensitive
    assert ingo.draw_position_source == "top_or_bottom_choice"

    print("Typed reset transition profile regression: PASS")


if __name__ == "__main__":
    main()
