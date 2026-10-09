"""Pinned local card-text regression for opponent bonus capacity semantics.

This checks exact bundled print IDs and selective phrases. It is not a
general card-effect parser and does not decide card legality.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def card(set_id: str, print_id: str) -> dict:
    pool = json.loads((ROOT / "resources" / "cards" / "en" / (set_id + ".json")).read_text(encoding="utf-8"))
    matches = [row for row in pool if row["id"] == print_id]
    assert len(matches) == 1, (set_id, print_id)
    return matches[0]


def assert_text(print_id: str, set_id: str, name: str, subtypes: tuple[str, ...],
                phrases: tuple[str, ...]) -> str:
    row = card(set_id, print_id)
    assert row["name"] == name
    assert set(subtypes).issubset(row["subtypes"])
    printed = " ".join(row["rules"])
    for phrase in phrases:
        assert phrase in printed, (print_id, phrase)
    return printed


def main() -> None:
    one_output = {
        "bw7-137": assert_text(
            "bw7-137", "bw7", "Computer Search", ("Item", "ACE SPEC"),
            ("Discard 2 cards from your hand", "Search your deck for a card"),
        ),
        "swsh9-150": assert_text(
            "swsh9-150", "swsh9", "Ultra Ball", ("Item",),
            ("discard 2 other cards", "Search your deck for a Pokémon"),
        ),
    }
    exclusive_mode = assert_text(
        "swsh12-164", "swsh12", "Serena", ("Supporter",),
        ("Choose 1:", "Discard up to 3 cards", "Switch 1 of your opponent's Benched Pokémon V"),
    )
    simultaneous = {
        "sm12-193": assert_text(
            "sm12-193", "sm12", "Guzma & Hala", ("Supporter", "TAG TEAM"),
            ("Search your deck for a Stadium card", "discard 2 other cards",
             "a Pokémon Tool card and a Special Energy card"),
        ),
        "sv6-163": assert_text(
            "sv6-163", "sv6", "Secret Box", ("Item", "ACE SPEC"),
            ("discard 3 other cards", "an Item card, a Pokémon Tool card",
             "a Supporter card, and a Stadium card"),
        ),
        "sm12-206": assert_text(
            "sm12-206", "sm12", "Tag Call", ("Item",),
            ("up to 2 TAG TEAM cards",),
        ),
    }

    # Text-only role classification below is intentionally manual:
    # Search-for-a-card produces one choice; Choose 1 grants one mode;
    # conditional and plural searches can produce simultaneous outputs.
    assert len(one_output) == 2
    assert "Choose 1:" in exclusive_mode
    assert len(simultaneous) == 3
    for print_id in (*one_output, "swsh12-164", *simultaneous):
        print(print_id, "verified against bundled print rules")
    print("PASS: exact six-print text catalog with output and payment anchors")


if __name__ == "__main__":
    main()
