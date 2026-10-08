"""Reproduce search-before-reset material-state dominance."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from pre_reset_search_dominance import (
    ResetState,
    reset_first,
    same_material_state,
    search_then_reset,
)


def _load_card(print_id: str) -> dict:
    set_id = print_id.split("-", 1)[0]
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(card for card in rows if card["id"] == print_id)


def main() -> None:
    quick_ball = _load_card("swsh8-237")
    dedenne = _load_card("sm10-57")
    squawk = _load_card("sv2-169")

    quick_text = " ".join(quick_ball["rules"])
    assert "discard another card from your hand" in quick_text
    assert "Search your deck for a Basic Pokémon" in quick_text
    assert quick_ball["legalities"]["expanded"] == "Legal"

    dede_text = dedenne["abilities"][0]["text"]
    assert "discard your hand and draw 6 cards" in dede_text
    assert dedenne["legalities"]["expanded"] == "Legal"

    squawk_text = squawk["abilities"][0]["text"]
    assert "Once during your first turn" in squawk_text
    assert "discard your hand and draw 6 cards" in squawk_text
    assert squawk["legalities"]["expanded"] == "Legal"

    deck = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")
    fresh_draw = ("A", "C", "D", "F", "H", "J")

    held_dedenne = ResetState(
        hand=(
            "Quick Ball",
            "Energy",
            "Dedenne-GX",
            "Gladion",
            "Ultra Ball",
            "X",
            "Y",
        ),
        deck=deck,
    )
    searched = search_then_reset(
        held_dedenne,
        resetter="Dedenne-GX",
        payment="Energy",
        fresh_draw=fresh_draw,
    )
    reset = reset_first(
        held_dedenne,
        resetter="Dedenne-GX",
        fresh_draw=fresh_draw,
    )
    assert same_material_state(searched, reset)
    assert searched.deck_searched
    assert not reset.deck_searched

    in_play_squawk = ResetState(
        hand=("Quick Ball", "Energy", "Gladion", "Ultra Ball", "X", "Y"),
        deck=deck,
        bench=("Squawkabilly ex",),
    )
    searched = search_then_reset(
        in_play_squawk,
        resetter="Squawkabilly ex",
        payment="Energy",
        fresh_draw=fresh_draw,
        resetter_already_in_play=True,
    )
    reset = reset_first(
        in_play_squawk,
        resetter="Squawkabilly ex",
        fresh_draw=fresh_draw,
        resetter_already_in_play=True,
    )
    assert same_material_state(searched, reset)
    assert searched.deck_searched
    assert not reset.deck_searched

    print("Search-before-reset material-state regression: PASS")


if __name__ == "__main__":
    main()
