"""Source-bound attack-body coverage regression for Regidrago Apex Dragon."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from apex_dragon_payload_coverage import build_payload_coverage


def main() -> None:
    result = build_payload_coverage(ROOT / "resources")
    rows = result["rows"]
    indexed = {(row.print_id, row.attack_name): row for row in rows}
    assert result["dragon_card_prints"] > 100
    assert result["payload_attack_prints"] > 200
    assert result["unique_lexical_bodies"] < result["payload_attack_prints"]
    assert sum(result["kinds_per_print"].values()) == result["payload_attack_prints"]
    assert sum(result["kinds_per_body"].values()) == result["unique_lexical_bodies"]
    assert result["gx_attack_prints"] > 0
    assert result["nested_copy_prints"] > 0

    phantom = indexed[("sv6-130", "Phantom Dive")]
    assert phantom.text_coverage_kind == "exact_damage_counter_clause"
    assert phantom.raw_damage == "200"

    timeless = indexed[("sm5-100", "Timeless-GX")]
    assert timeless.text_coverage_kind == "exact_extra_turn"
    assert timeless.gx_attack
    assert "turn_boundary" in timeless.requires_handlers
    assert "gx_budget" in timeless.requires_handlers

    rolling = indexed[("swsh11-136", "Rolling Iron")]
    assert rolling.text_coverage_kind == "uncompiled_effect_text"
    assert rolling.raw_damage == "200"

    apex = indexed[("swsh12-136", "Apex Dragon")]
    assert apex.nested_copy
    assert apex.text_coverage_kind == "uncompiled_effect_text"

    jet = indexed[("sv6-130", "Jet Headbutt")]
    assert jet.text_coverage_kind == "plain_fixed_or_gx_rule"
    assert not jet.requires_handlers

    signature_list = [row.body_signature for row in result["signature_representatives"]]
    assert len(set(signature_list)) == len(signature_list)
    assert set(signature_list) == {row.body_signature for row in rows}

    print({
        "dragon_card_prints": result["dragon_card_prints"],
        "payload_attack_prints": result["payload_attack_prints"],
        "distinct_body_signatures": result["unique_lexical_bodies"],
        "coverage_by_print": result["kinds_per_print"],
        "coverage_by_body": result["kinds_per_body"],
        "verified_damage_only_prints": result["damage_only_verified_prints"],
        "verified_damage_only_bodies": result["damage_only_verified_bodies"],
        "gx_prints": result["gx_attack_prints"],
        "nested_copy_prints": result["nested_copy_prints"],
    })


if __name__ == "__main__":
    main()
