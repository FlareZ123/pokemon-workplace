"""Audit exact status-inflicting attack text in the legal Expanded corpus."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_status_text_contracts import catalog_attack_status_sources
from simple_attack_board_semantics import compile_legal_index


def main() -> None:
    index = compile_legal_index(ROOT / "resources")
    data = catalog_attack_status_sources(ROOT / "resources")
    rows = data["rows"]
    assert data["total"] == len(rows)
    assert data["unconditional"] + data["coin_gated"] == data["total"]
    assert sum(data["counts"].values()) == data["total"]
    assert data["total"] > 50

    witnesses = (
        ("bw1-39", "Water Pulse", "Asleep", None),
        ("bw1-53", "Poison Sting", "Poisoned", None),
        ("bw1-24", "Singe", "Burned", None),
        ("bw1-79", "Confuse Ray", "Confused", None),
        ("bw1-3", "Wrap", "Paralyzed", "heads"),
    )
    for card_id, name, status, coin_result in witnesses:
        found = [
            row for row in rows
            if row.print_id == card_id and row.attack_name == name
        ]
        assert len(found) == 1, (card_id, name)
        row = found[0]
        assert (row.special_condition, row.requires_coin_result) == (
            status, coin_result
        )
        assert row.target_scope == "opponent_active"
        matched = [
            attack for attack in index[card_id]
            if attack.attack_name == name
        ]
        assert len(matched) == 1
        assert row.attack_index == matched[0].attack_index

    # Complex or conditional text must not be promoted to full-text support.
    excluded = (
        ("bw1-4", "Wring Out"),
        ("sm11-54", "Tandem Shock"),
    )
    for card_id, name in excluded:
        assert not any(
            row.print_id == card_id and row.attack_name == name
            for row in rows
        )

    print({
        "exact_status_attack_prints": data["total"],
        "unconditional": data["unconditional"],
        "coin_gated": data["coin_gated"],
        "status_by_trigger": data["counts"],
        "real_card_witnesses": len(witnesses),
        "complex_clause_exclusions": len(excluded),
    })


if __name__ == "__main__":
    main()
