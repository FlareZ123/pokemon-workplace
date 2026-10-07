from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_fixture_compiler import build


def fixture(result: dict, attack_name: str) -> dict:
    rows = [row for row in result["fixtures"] if row["attack_name"] == attack_name]
    assert len(rows) == 1
    return rows[0]


def main() -> None:
    result = build(ROOT / "resources")
    assert result["signature_count"] == 30
    assert result["source_class_count"] == 15

    copy_anything = fixture(result, "Copy Anything")
    assert copy_anything["selector"]["source"] == "opponent_in_play"
    assert copy_anything["selector"]["require_selected_energy"]

    hypnotic = fixture(result, "Hypnotic Reign")
    assert hypnotic["selector"]["source"] == "opponent_hand"
    assert hypnotic["selector"]["require_non_gx"]
    assert hypnotic["selector"]["optional_selection"]
    assert hypnotic["selector"]["move_selected_source_to"] == "discard"
    assert hypnotic["pre_event"] == "reveal_hand"

    seek = fixture(result, "Seek Inspiration")
    assert seek["selector"]["source"] == "own_deck_top"
    assert seek["selector"]["require_no_rule_box"]
    assert seek["selector"]["precommit_source_to"] == "discard"
    assert seek["pre_event"] == "discard_top_card"

    haughty = fixture(result, "Haughty Order")
    assert haughty["selector"]["source"] == "opponent_revealed"
    assert haughty["selector"]["optional_selection"]
    assert haughty["pre_event"] == "reveal_top_10"
    assert haughty["post_event"] == "shuffle_revealed"

    mimed = fixture(result, "Mimed Games")
    assert mimed["selector"]["chooser"] == "opponent"

    night = fixture(result, "Night Joker")
    assert night["selector"]["required_name_prefix"] == "N's "

    recall_rows = [
        row for row in result["fixtures"] if row["attack_name"] == "Recall"
    ]
    assert len(recall_rows) == 2
    assert all(
        row["selector"]["source"] == "self_previous_evolution"
        for row in recall_rows
    )

    trickster = fixture(result, "Trickster-GX")
    assert trickster["is_gx"]

    print("attack-copy fixture compiler regression: PASS")
    print({
        "signatures": result["signature_count"],
        "source_classes": result["source_class_count"],
    })


if __name__ == "__main__":
    main()
