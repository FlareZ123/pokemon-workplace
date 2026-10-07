from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_use_requirement_catalog import build


EXPECTED_COUNTS = {
    "attack_history": 7,
    "bench_types_grass_water_lightning": 1,
    "discard_lacks_supporter": 1,
    "lost_zone_count_at_least_10": 2,
    "opponent_active_special_condition": 1,
    "opponent_prizes_exact_1": 1,
    "opponent_prizes_exact_2": 1,
    "relative_prize_advantage": 2,
    "relative_prize_gap_at_least_3": 1,
    "self_has_damage": 1,
    "total_remaining_prizes_at_most_6": 1,
    "turn_order_first_turn": 10,
}


def row_by_name(result, name: str):
    matches = [
        row
        for row in result["signatures"]
        if row["attack_name"] == name
    ]
    if len(matches) != 1:
        raise AssertionError((name, len(matches)))
    return matches[0]


def main() -> None:
    result = build(ROOT / "resources")
    assert result["scope"] == {
        "format": "paper Expanded, Black & White onward",
        "print_rows": 44,
        "signatures": 29,
        "card_names": 29,
    }
    assert result["dependency_family_counts"] == EXPECTED_COUNTS
    assert all(
        row["dependency_family"] != "unclassified"
        for row in result["signatures"]
    )

    lost_mine = row_by_name(result, "Lost Mine")
    assert lost_mine["print_ids"] == ["swsh11-70"]
    assert (
        lost_mine["dependency_family"]
        == "lost_zone_count_at_least_10"
    )

    nightcap = row_by_name(result, "Nightcap")
    assert nightcap["dependency_family"] == "opponent_prizes_exact_2"

    follow_up = row_by_name(result, "Follow-Up Kerzap")
    assert follow_up["dependency_family"] == "attack_history"
    assert follow_up["attack_text"].endswith("during your last turn.")

    print(
        {
            "scope": result["scope"],
            "dependency_family_counts": result["dependency_family_counts"],
            "lost_mine_family": lost_mine["dependency_family"],
        }
    )


if __name__ == "__main__":
    main()
