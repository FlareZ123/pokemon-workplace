"""Reproduce the typed Prize-origin E-31 profile catalog."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from before_hand_prize_profiles import build_before_hand_prize_profiles

RESOURCES = ROOT / "resources"


def main() -> None:
    profiles = build_before_hand_prize_profiles(RESOURCES)
    by_id = {profile.card_id: profile for profile in profiles}

    assert set(by_id) == {
        "sm7-97",
        "sv3pt5-113",
        "swsh7-146",
        "swsh7-165",
        "xy11-102",
    }

    jirachi = by_id["sm7-97"]
    assert jirachi.card_name == "Jirachi ◇"
    assert jirachi.activation_family == "self_to_bench"
    assert jirachi.self_destination == "in_play"
    assert jirachi.during_own_turn_explicit
    assert jirachi.card_text_requires_open_bench
    assert jirachi.extra_prize_mode == "guaranteed"
    assert not jirachi.searches_pokemon_to_bench

    chansey = by_id["sv3pt5-113"]
    assert chansey.activation_family == "self_to_bench"
    assert chansey.during_own_turn_explicit
    assert chansey.card_text_requires_open_bench
    assert chansey.extra_prize_mode == "coin_heads"

    dream_ball = by_id["swsh7-146"]
    assert dream_ball.activation_family == "item_play"
    assert dream_ball.self_destination == "discard_after_use"
    assert not dream_ball.during_own_turn_explicit
    assert not dream_ball.card_text_requires_open_bench
    assert dream_ball.extra_prize_mode == "none"
    assert dream_ball.searches_pokemon_to_bench

    treasure = by_id["swsh7-165"]
    assert treasure.activation_family == "self_attach"
    assert treasure.self_destination == "attached"
    assert treasure.during_own_turn_explicit
    assert treasure.extra_prize_mode == "none"

    greedy = by_id["xy11-102"]
    assert greedy.activation_family == "item_play"
    assert greedy.self_destination == "discard_after_use"
    assert greedy.extra_prize_mode == "coin_heads"
    assert not greedy.searches_pokemon_to_bench

    families = {}
    for profile in profiles:
        families[profile.activation_family] = (
            families.get(profile.activation_family, 0) + 1
        )
    assert families == {
        "item_play": 2,
        "self_attach": 1,
        "self_to_bench": 2,
    }

    print("Prize-origin E-31 profiles passed:", len(profiles), families)


if __name__ == "__main__":
    main()
