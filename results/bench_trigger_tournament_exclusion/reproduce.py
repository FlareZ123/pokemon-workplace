"""Audit banned promotional Pokémon in Bench-entry catalogs."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from build_expanded_legality_baseline import classify_effective_legality, load_json
from setup_trigger_role_contention import scan_literal_bench_trigger_basics
from bench_trigger_lifecycle import scan_bench_trigger_lifecycle
from bench_resource_catalog import bench_entry_rows, iter_legal_cards

RESOURCES = ROOT / "resources"
BANNED_PROMOS = {
    "swshp-SWSH132", "swshp-SWSH135", "swshp-SWSH136",
    "swshp-SWSH137", "swshp-SWSH138", "swshp-SWSH144", "xy12-112",
}


def main() -> None:
    greninja = next(
        card for card in load_json(RESOURCES / "cards" / "en" / "swshp.json")
        if card["id"] == "swshp-SWSH144"
    )
    assert "Basic" in greninja["subtypes"]
    assert greninja["abilities"][0]["name"] == "Shadow Knife"
    assert classify_effective_legality(greninja) == ("Banned", "card_text_tournament_ban")
    assert bench_entry_rows(greninja)

    trigger = scan_literal_bench_trigger_basics(RESOURCES)
    trigger_ids = {row["id"] for row in trigger["prints"]}
    assert trigger["print_count"] == 123
    assert trigger["unique_names"] == 48
    assert trigger["gameplay_variants"] == 51
    assert "swshp-SWSH144" not in trigger_ids
    assert "Greninja ★" not in trigger["names"]

    lifecycle = scan_bench_trigger_lifecycle(RESOURCES)
    assert lifecycle["trigger_print_count"] == 123
    assert lifecycle["trigger_name_count"] == 48
    assert lifecycle["self_vacating_print_count"] == 22
    assert lifecycle["self_vacating_name_count"] == 6
    assert lifecycle["self_vacating_gameplay_variants"] == 7
    assert "swshp-SWSH144" not in {row["id"] for row in lifecycle["prints"]}

    legal_bench_cards = tuple(iter_legal_cards(RESOURCES))
    assert len(legal_bench_cards) == 14829
    legal_bench_ids = {card["id"] for card in legal_bench_cards}
    assert not legal_bench_ids.intersection(BANNED_PROMOS)
    assert trigger_ids <= legal_bench_ids
    assert "swshp-SWSH144" not in {
        row["id"]
        for card in legal_bench_cards
        for row in bench_entry_rows(card)
    }
    print(
        "PASS: 14,829 legal prints; 123 Bench-trigger prints; "
        "48 names; 51 variants; unchanged 22 self-vacating prints"
    )


if __name__ == "__main__":
    main()
