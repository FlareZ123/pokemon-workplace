"""Reproduce Aichi decklist-to-card-database resolution boundaries."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_card_name_resolution import load_card_names, resolve_counts
from aichi_setup_inference import (
    KAZUMA_IRON_NONBASIC_COUNTS,
    KOHEI_IRON_NONBASIC_COUNTS,
    RYOYA_IRON_NONBASIC_COUNTS,
    VILEPLUME_NONBASIC_COUNTS,
)


def main() -> None:
    cards = load_card_names(ROOT / "resources" / "cards" / "en")

    vileplume = resolve_counts(VILEPLUME_NONBASIC_COUNTS, cards)
    kazuma = resolve_counts(KAZUMA_IRON_NONBASIC_COUNTS, cards)
    ryoya = resolve_counts(RYOYA_IRON_NONBASIC_COUNTS, cards)
    kohei = resolve_counts(KOHEI_IRON_NONBASIC_COUNTS, cards)

    assert vileplume.missing_names == ()
    assert vileplume.aliased_names == ()

    assert kazuma.missing_names == (
        "Palace Belt",
        "Palace Book",
        "Player's Ceremony",
    )
    assert kazuma.missing_copies == 3

    assert ryoya.missing_names == (
        "Palace Book",
        "Player's Ceremony",
    )
    assert ryoya.missing_copies == 4

    assert kohei.aliased_names == (
        ("Target Whistle", "Target Whistle Team Flare Gear"),
    )
    assert kohei.missing_names == (
        "Palace Belt",
        "Player's Ceremony",
    )
    assert kohei.missing_copies == 3

    target_whistle = cards["Target Whistle Team Flare Gear"]
    assert any("Item" in card.get("subtypes", []) for card in target_whistle)

    print("aichi_card_name_resolution: all assertions passed")
    for name, result in (
        ("Vileplume", vileplume),
        ("Kazuma Iron Thorns", kazuma),
        ("Ryoya Iron Thorns", ryoya),
        ("Kohei Iron Thorns", kohei),
    ):
        print(
            name,
            f"aliases={result.aliased_names}",
            f"missing={result.missing_names}",
            f"missing_copies={result.missing_copies}",
        )


if __name__ == "__main__":
    main()
