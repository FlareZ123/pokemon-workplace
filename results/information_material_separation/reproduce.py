"""Reproduce card-text premises for information/material-access separation."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_information_actions import build_catalog  # noqa: E402


def _find(catalog, card_name: str, effect_name: str = ""):
    return [
        row
        for row in catalog["exact_variants"]
        if row["mechanism"] == "full_deck_inspection"
        and row["card_name"] == card_name
        and row["effect_name"] == effect_name
    ]


def main() -> None:
    catalog = build_catalog(ROOT / "resources")

    nest_ball = _find(catalog, "Nest Ball")
    quick_ball = _find(catalog, "Quick Ball")
    wonder_tag = _find(catalog, "Tapu Lele-GX", "Wonder Tag")
    skyla = _find(catalog, "Skyla")
    lead = _find(catalog, "Jigglypuff", "Lead")

    assert nest_ball
    assert quick_ball
    assert wonder_tag
    assert skyla
    assert lead

    assert all(row["action_class"] == "Item" for row in nest_ball)
    assert all("put it onto your Bench" in row["text"] for row in nest_ball)

    assert all(row["action_class"] == "Item" for row in quick_ball)
    assert all("put it into your hand" in row["text"] for row in quick_ball)

    assert wonder_tag[0]["action_class"] == "Ability"
    assert wonder_tag[0]["ability_timing_bucket"] == "play_from_hand_trigger"
    assert "play this Pokémon from your hand onto your Bench" in wonder_tag[0]["text"]

    assert all(row["action_class"] == "Supporter" for row in skyla)

    assert all(row["action_class"] == "Attack" for row in lead)
    assert all("Supporter card" in row["text"] for row in lead)

    print("Information/material separation premises")
    print("  Nest Ball: Item full-deck search -> Basic directly to Bench")
    print("  Quick Ball: Item full-deck search -> Basic to hand")
    print("  Tapu Lele-GX Wonder Tag: requires play from hand onto Bench")
    print("  Skyla: Supporter full-deck search")
    print("  Jigglypuff Lead: attack full-deck search for a Supporter")
    print()
    print("All information/material separation checks passed.")


if __name__ == "__main__":
    main()
