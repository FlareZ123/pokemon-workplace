"""Reproduce the source-zone scope audit for direct Item locks."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from before_hand_prize_profiles import build_before_hand_prize_profiles
from item_play_source_scope import (
    build_item_play_restrictions,
    restriction_blocks_source,
)

RESOURCES = ROOT / "resources"


def main() -> None:
    restrictions = build_item_play_restrictions(RESOURCES)

    assert len(restrictions) == 42
    assert len({row.text for row in restrictions}) == 15
    assert {row.prohibited_source_zone for row in restrictions} == {"hand"}

    ids = {row.card_id for row in restrictions}
    assert {"xy7-3", "xy1-55", "xy3-20", "sv8pt5-4"} <= ids

    for restriction in restrictions:
        assert restriction_blocks_source(restriction, "hand")
        assert not restriction_blocks_source(
            restriction,
            "prize_pending",
        )

    profiles = build_before_hand_prize_profiles(RESOURCES)
    item_profiles = {
        profile.card_id: profile
        for profile in profiles
        if profile.activation_family == "item_play"
    }
    assert set(item_profiles) == {"swsh7-146", "xy11-102"}

    print(
        "Item-play source-scope audit passed:",
        len(restrictions),
        "direct prohibition rows;",
        len({row.text for row in restrictions}),
        "unique text variants",
    )


if __name__ == "__main__":
    main()
