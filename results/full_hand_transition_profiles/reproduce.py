"""Reproduce the integrated typed hand-transition catalog from repository resources."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from compile_full_hand_transition_profiles import compile_full_hand_transition_profiles


def test_profiles(resources: Path) -> None:
    rows = compile_full_hand_transition_profiles(resources)
    assert len(rows) == 80, len(rows)
    assert sum(r.print_count for r in rows) == 227
    assert Counter(r.hand_destination for r in rows) == {
        "discard_all": 15, "shuffle_into_deck": 59, "bottom_deck": 6}
    assert {d: sum(r.print_count for r in rows if r.hand_destination == d)
        for d in ("discard_all", "shuffle_into_deck", "bottom_deck")} == {
        "discard_all": 80, "shuffle_into_deck": 128, "bottom_deck": 19}
    assert Counter(r.source_kind for r in rows) == {
        "supporter": 34, "attack": 33, "ability": 11, "stadium": 1, "item": 1}
    assert Counter(r.draw_mode for r in rows) == {
        "fixed": 40, "card_text_dependent": 40}
    assert sum(r.ends_turn for r in rows) == 37
    assert sum(r.supporter_cost for r in rows) == 34
    assert Counter(r.once_per_game_resource for r in rows) == {
        "none": 76, "gx_attack": 3, "vstar_power": 1}

    def one(name: str, destination: str):
        values = [r for r in rows if r.name == name and r.hand_destination == destination]
        assert values, (name, destination)
        return values[0]

    assert one("Cynthia", "shuffle_into_deck").fixed_draw_count == 6
    assert one("Judge", "shuffle_into_deck").fixed_draw_count == 4
    assert one("Iono", "bottom_deck").draw_mode == "card_text_dependent"
    assert one("N", "shuffle_into_deck").draw_mode == "card_text_dependent"
    assert one("Marnie", "bottom_deck").target_scope == "both"
    assert one("Hala", "shuffle_into_deck").once_per_game_resource == "none"
    assert one("Professor Juniper", "discard_all").source_gate == "supporter_from_hand"
    assert one("Dedenne-GX", "discard_all").source_gate == "hand_to_bench"
    assert one("Ingo & Emmet", "discard_all").draw_position_source == "top_or_bottom_choice"
    assert one("Jubilife Village", "shuffle_into_deck").ends_turn
    assert one("Jubilife Village", "shuffle_into_deck").source_gate == "stadium_activated_in_play"
    assert one("Thievul", "bottom_deck").source_gate == "hand_evolution_trigger"
    assert one("Kingdra", "bottom_deck").target_scope == "chosen"
    assert one("Venomoth-GX", "shuffle_into_deck").once_per_game_resource == "gx_attack"
    print("Unified catalog:", len(rows), "profiles,", sum(r.print_count for r in rows), "print records")
    print("Hand destinations: 15 discard-all, 59 shuffle-back, 6 bottom-deck variants")
    print("Typed properties: 40 fixed, 40 text-dependent draws; 37 turn-ending variants")
    print("Source/action/resource regression cases passed")


if __name__ == "__main__":
    test_profiles(ROOT / "resources")
