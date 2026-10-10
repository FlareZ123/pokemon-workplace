"""Reproduce the exact Prize-information action catalog."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_information_actions import build_catalog  # noqa: E402


def _find(catalog, mechanism: str, card_name: str, effect_name: str = ""):
    return [
        row
        for row in catalog["exact_variants"]
        if row["mechanism"] == mechanism
        and row["card_name"] == card_name
        and row["effect_name"] == effect_name
    ]


def main() -> None:
    catalog = build_catalog(ROOT / "resources")

    assert catalog["legal_print_count"] == 14829
    assert catalog["exact_variant_count"] == 880

    expected_exact_counts = {
        "exact_prize_inspection|Attack": 3,
        "exact_prize_inspection|Item": 3,
        "exact_prize_inspection|Supporter": 3,
        "full_deck_inspection|Ability": 122,
        "full_deck_inspection|Attack": 568,
        "full_deck_inspection|Energy": 2,
        "full_deck_inspection|Item": 87,
        "full_deck_inspection|Pokémon Tool": 3,
        "full_deck_inspection|Supporter": 89,
    }
    assert catalog["exact_counts"] == expected_exact_counts

    data_check = _find(catalog, "full_deck_inspection", "Porygon", "Data Check")
    assert len(data_check) == 1
    assert data_check[0]["print_ids"] == ["xy7-64"]
    assert data_check[0]["text"] == "Look through your deck. Shuffle your deck afterward."

    direct_names = {
        row["card_name"]
        for row in catalog["exact_variants"]
        if row["mechanism"] == "exact_prize_inspection"
    }
    assert direct_names == {
        "Town Map",
        "Naganadel & Guzzlord-GX",
        "Gladion",
        "Celesteela-GX",
        "Beast Ball",
        "Poipole",
        "Daisy's Help",
        "Hisuian Heavy Ball",
        "Here Comes Team Rocket!",
    }

    town_map = _find(catalog, "exact_prize_inspection", "Town Map")
    assert len(town_map) == 1
    assert town_map[0]["action_class"] == "Item"

    wonder_tag = _find(catalog, "full_deck_inspection", "Tapu Lele-GX", "Wonder Tag")
    assert len(wonder_tag) == 1
    assert wonder_tag[0]["ability_timing_bucket"] == "play_from_hand_trigger"

    assert catalog["partial_counts"] == {
        "partial_deck_inspection|Ability": 37,
        "partial_deck_inspection|Attack": 59,
        "partial_deck_inspection|Item": 33,
        "partial_deck_inspection|Stadium": 1,
        "partial_deck_inspection|Supporter": 22,
        "partial_prize_inspection|Attack": 5,
        "partial_prize_inspection|Item": 1,
    }

    print("Legal Expanded prints:", catalog["legal_print_count"])
    print("Exact-information text variants:", catalog["exact_variant_count"])
    for key, value in catalog["exact_counts"].items():
        print(f"  {key}: {value}")

    print("\nDirect exact-Prize cards:")
    for name in sorted(direct_names):
        print(f"  {name}")

    print("\nPartial-information text variants:", catalog["partial_variant_count"])
    for key, value in catalog["partial_counts"].items():
        print(f"  {key}: {value}")

    print("\nAll Prize-information action checks passed.")


if __name__ == "__main__":
    main()
