"""One-file live card corpus regression for literal damage target geometry."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_damage_target_geometry import catalog
from simple_attack_board_semantics import compile_legal_index


def main() -> None:
    index = compile_legal_index(ROOT / "resources")
    result = catalog(ROOT / "resources")
    rows = {r.attack_id: r for r in result["rows"]}

    witnesses = (
        ("bw10-19", "Sharpshooting", 0, 30, "opponent_any", 1, None),
        ("bw11-43", "Glaciate", 0, 30, "opponent_all", None, None),
        ("bw11-19", "Split Bomb", 0, 40, "opponent_any", 2, None),
        ("bw5-63", "Night Spear", 90, 30, "opponent_bench", 1, None),
        ("bw7-89", "Hammerhead", 30, 30, "opponent_bench", 1, None),
        ("me1-81", "Stony Kick", 20, 20, "opponent_bench", 1, None),
        ("me55-64", "Photon Bullets", 0, 50, "opponent_all", None, "ex"),
        ("sm8-121", "Dusty Ruckus", 130, 30, "opponent_bench", None, "Basic"),
    )
    for card_id, attack_name, active, text_damage, scope, count, filter_name in witnesses:
        matched = [r for r in result["rows"] if r.card_id == card_id and r.attack_name == attack_name]
        assert len(matched) == 1, (card_id, attack_name, matched)
        row = matched[0]
        assert (
            row.printed_active_damage, row.text_damage, row.target_scope,
            row.target_count, row.target_filter,
        ) == (active, text_damage, scope, count, filter_name), row
        assert index[card_id][row.attack_index].has_uncompiled_damage_text

    excluded = (
        ("sv6-130", "Phantom Dive"),
        ("sm12-165", "Puffy Smashers-GX"),
    )
    for card_id, name in excluded:
        attack_ids = {
            f"{card_id}:attack:{i}"
            for i, row in enumerate(index[card_id])
            if row.attack_name == name
        }
        assert not attack_ids.intersection(rows), (card_id, name)

    assert result["total_rows"] > 100
    assert result["total_rows"] == result["effect_only_rows"] + result["supplemental_rows"]
    assert all(row.text_damage > 0 for row in result["rows"])
    assert all(
        (row.target_count is None or 1 <= row.target_count <= 6)
        for row in result["rows"]
    )
    print({
        "exact_full_text_rows": result["total_rows"],
        "effect_only_rows": result["effect_only_rows"],
        "supplemental_rows": result["supplemental_rows"],
        "shape_counts": result["shapes"],
        "witnesses_verified": len(witnesses),
        "excluded_conditional_or_counter_witnesses": len(excluded),
    })


if __name__ == "__main__":
    main()
