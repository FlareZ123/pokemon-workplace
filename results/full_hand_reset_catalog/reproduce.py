"""Reproduce the Expanded full-hand discard-and-draw reset catalog."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from catalog_full_hand_resets import catalog_full_hand_resets


EXPECTED_NAMES = {
    "Carmine",
    "Dedenne-GX",
    "Hisuian Zoroark VSTAR",
    "Ingo & Emmet",
    "Professor Juniper",
    "Professor Sycamore",
    "Professor's Research",
    "Raging Bolt ex",
    "Rayquaza VMAX",
    "Rayquaza-GX",
    "Squawkabilly ex",
    "Talonflame V",
    "Tapu Koko",
    "Zamazenta V",
    "Zebstrika",
}


def main() -> None:
    families = catalog_full_hand_resets(ROOT / "resources")

    assert len(families) == 15
    assert sum(len(row.print_ids) for row in families) == 80
    assert {row.name for row in families} == EXPECTED_NAMES

    by_name = {row.name: row for row in families}

    assert by_name["Dedenne-GX"].source_kind == "ability"
    assert by_name["Dedenne-GX"].draw_count == 6
    assert not by_name["Dedenne-GX"].ends_turn

    assert by_name["Squawkabilly ex"].mentions_first_turn
    assert by_name["Hisuian Zoroark VSTAR"].once_per_game
    assert by_name["Rayquaza-GX"].once_per_game
    assert by_name["Rayquaza-GX"].ends_turn

    assert by_name["Professor Juniper"].supporter
    assert by_name["Professor Sycamore"].supporter
    assert by_name["Professor's Research"].supporter

    assert by_name["Ingo & Emmet"].position_sensitive
    assert by_name["Zamazenta V"].ends_turn
    assert by_name["Raging Bolt ex"].ends_turn

    print("Expanded full-hand reset catalog regression: PASS")


if __name__ == "__main__":
    main()
