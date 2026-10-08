"""One-file regression for conservative whole-text coverage classification."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_text_coverage_inventory import build_coverage, classify_attack_text
from simple_attack_board_semantics import compile_legal_index


def main() -> None:
    index = compile_legal_index(ROOT / "resources")
    inventory = build_coverage(ROOT / "resources")
    by_id = {
        row.attack_id: row
        for row in inventory["rows"]
    }
    assert len(by_id) == inventory["total"] == 19992
    assert sum(inventory["counts"].values()) == inventory["total"]

    witnesses = (
        ("sv6-130", "Jet Headbutt", "plain_fixed_or_gx_rule"),
        ("sv6-130", "Phantom Dive", "exact_damage_counter_clause"),
        ("sm8-96", "Cursed Drop", "exact_damage_counter_clause"),
        ("sm8-94", "Mind Shock", "exact_type_modifier_bypass"),
        ("sm5-100", "Shred", "exact_defender_effect_bypass"),
        ("sm5-100", "Timeless-GX", "exact_extra_turn"),
        ("bw1-3", "Wrap", "uncompiled_effect_text"),
        ("bw1-5", "Leaf Storm", "uncompiled_effect_text"),
        ("bw1-17", "Flame Charge", "uncompiled_effect_text"),
        ("bw1-37", "Aqua Ring", "uncompiled_effect_text"),
        ("bw1-81", "Collect", "uncompiled_effect_text"),
    )
    for card_id, attack_name, expected in witnesses:
        matches = [
            row for row in index[card_id]
            if row.attack_name == attack_name
        ]
        assert len(matches) == 1
        classified = classify_attack_text(matches[0])
        assert classified.kind == expected, (card_id, attack_name, classified)
        assert classified == by_id[matches[0].attack_id]

    all_unguarded = tuple(
        source for entries in index.values() for source in entries
        if source.fixed_damage is not None
        and classify_attack_text(source).kind == "uncompiled_effect_text"
        and not (
            source.has_uncompiled_damage_text
            or source.has_uncompiled_knockout_text
            or source.has_uncompiled_attack_gate
        )
    )
    assert len(all_unguarded) == inventory["uncompiled_unguarded"]
    assert inventory["uncompiled_unguarded"] > 1000
    assert inventory["guarded_uncompiled"] > 500

    print({
        "legal_attack_rows": inventory["total"],
        "kinds": inventory["counts"],
        "uncompiled_effect_text_not_caught_by_specific_guards":
            inventory["uncompiled_unguarded"],
        "guarded_uncompiled_effect_text": inventory["guarded_uncompiled"],
        "real_card_witnesses": len(witnesses),
    })


if __name__ == "__main__":
    main()
