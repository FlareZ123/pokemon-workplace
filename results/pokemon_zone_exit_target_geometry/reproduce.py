"""Reproduce conservative direct zone-exit target geometry compilation."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from pokemon_zone_exit_target_geometry import (
    compile_zone_exit_target_profiles,
)


def _profile(profiles: tuple, card_id: str):
    matches = [
        profile
        for profile in profiles
        if profile.card_id == card_id
    ]
    if len(matches) != 1:
        raise AssertionError((card_id, matches))
    return matches[0]


def main() -> None:
    result = compile_zone_exit_target_profiles(
        ROOT / "resources"
    )
    summary = result["summary"]
    profiles = result["profiles"]

    assert summary["profiles"] == 143
    assert summary["unique_names"] == 70
    assert summary["filter_print_counts"] == {
        "basic": 4,
        "colorless_and_damaged": 4,
        "damaged": 4,
        "exclude_name_corviknight": 1,
        "name_combee": 1,
        "none": 127,
        "unqualified_scope": 2,
    }
    assert summary["filter_unique_name_counts"] == {
        "basic": 1,
        "colorless_and_damaged": 1,
        "damaged": 2,
        "exclude_name_corviknight": 1,
        "name_combee": 1,
        "none": 63,
        "unqualified_scope": 1,
    }
    assert summary["geometry_print_counts"] == {
        "both_active": 1,
        "opponent_active": 11,
        "opponent_bench_all": 2,
        "opponent_bench_all_except_selected_three": 2,
        "opponent_bench_one": 7,
        "opponent_bench_one_and_self": 3,
        "opponent_one": 4,
        "own_any_number": 3,
        "own_bench_one": 6,
        "own_one": 26,
        "self": 76,
        "unqualified_one_to_your_hand": 2,
    }
    assert summary["geometry_unique_name_counts"] == {
        "both_active": 1,
        "opponent_active": 7,
        "opponent_bench_all": 1,
        "opponent_bench_all_except_selected_three": 1,
        "opponent_bench_one": 5,
        "opponent_bench_one_and_self": 2,
        "opponent_one": 2,
        "own_any_number": 1,
        "own_bench_one": 4,
        "own_one": 8,
        "self": 39,
        "unqualified_one_to_your_hand": 1,
    }

    witnesses = {
        "bw5-11": "self",
        "bw10-95": "own_one",
        "rsv10pt5-37": "own_bench_one",
        "sm3-39": "opponent_active",
        "sm7-14": "opponent_one",
        "sm8-149": "opponent_bench_one",
        "sm8-34": "own_any_number",
        "sm12-143": "opponent_bench_all",
        "sv5-5": "opponent_bench_all_except_selected_three",
        "sv3pt5-12": "opponent_bench_one_and_self",
        "sv2-18": "both_active",
        "xy4-91": "unqualified_one_to_your_hand",
    }
    for card_id, geometry in witnesses.items():
        assert _profile(profiles, card_id).target_geometry == geometry

    assert _profile(profiles, "sm3-112").target_filter == "damaged"
    assert _profile(profiles, "sv1-183").target_filter == "basic"
    assert (
        _profile(profiles, "swsh9-134").target_filter
        == "colorless_and_damaged"
    )
    assert (
        _profile(profiles, "swsh3-156").target_filter
        == "exclude_name_corviknight"
    )
    assert _profile(profiles, "sv2-9").target_filter == "name_combee"
    assert _profile(profiles, "xy4-91").target_filter == "unqualified_scope"
    assert _profile(profiles, "bw10-95").target_filter == "none"

    excluded = {"bw6-115", "xy9-113", "xyp-XY93"}
    assert not excluded & {
        profile.card_id
        for profile in profiles
    }

    print(summary)
    for card_id in witnesses:
        profile = _profile(profiles, card_id)
        print(
            profile.card_id,
            profile.name,
            profile.target_geometry,
            profile.pokemon_destination,
            profile.attachment_destination,
        )


if __name__ == "__main__":
    main()
