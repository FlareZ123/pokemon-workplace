"""Verify current multi-Pokemon KO ordering against the dated rule change."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from rulebook_order_authority_audit import audit_rulebook


def main() -> None:
    evidence = json.loads(
        (Path(__file__).with_name("evidence.json")).read_text(encoding="utf-8")
    )

    assert evidence["legacy_official_faq"]["chooser_role"] == (
        "knocked_out_pokemon_owner"
    )
    assert evidence["legacy_official_faq"]["status"] == (
        "superseded_by_2025_rule_change"
    )
    assert evidence["rule_change"]["effective_date"] == "2025-08-01"
    assert evidence["rule_change"]["chooser_role"] == "current_turn_player"

    manual = (
        ROOT
        / "resources"
        / "manual"
        / "EN_advanced_manual-2025-transcription-structured.md"
    )
    rows = audit_rulebook(manual)
    current = [
        row
        for row in rows
        if row.case == "multi_pokemon_ko_triggers"
    ]
    assert len(current) == 1
    assert current[0].chooser_role == "current_turn_player"
    assert evidence["current_rulebook"]["chooser_role"] == (
        current[0].chooser_role
    )

    print("Rule-change precedence regression passed")


if __name__ == "__main__":
    main()
