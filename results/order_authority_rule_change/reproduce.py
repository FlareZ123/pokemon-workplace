"""Verify the 2025 ordering-rule migration against bundled v3.4 rules."""

import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from rulebook_order_authority_audit import audit_rulebook


def main() -> None:
    evidence = json.loads(
        (Path(__file__).with_name("evidence.json")).read_text(encoding="utf-8")
    )

    assert evidence["effective_date"] == "2025-08-01"

    changed = {
        row["case"]: (
            row["legacy_chooser_role"],
            row["current_chooser_role"],
        )
        for row in evidence["changed_cases"]
    }
    assert changed == {
        "multi_pokemon_ko_triggers": (
            "knocked_out_pokemon_owner",
            "current_turn_player",
        ),
        "energy_attachment_triggers": (
            "affected_pokemon_owner",
            "current_turn_player",
        ),
        "pokemon_checkup_effects": (
            "affected_pokemon_owner",
            "next_turn_player",
        ),
    }

    manual = (
        ROOT
        / "resources"
        / "manual"
        / "EN_advanced_manual-2025-transcription-structured.md"
    )
    rows = audit_rulebook(manual)
    current = {
        row.case: row.chooser_role
        for row in rows
        if row.case in changed
    }
    assert current == {
        case: current_role
        for case, (_legacy_role, current_role) in changed.items()
    }

    counts = Counter(row.case for row in rows if row.case in changed)
    assert counts == {
        "multi_pokemon_ko_triggers": 1,
        "energy_attachment_triggers": 1,
        "pokemon_checkup_effects": 2,
    }

    stale = evidence["stale_faq_witness"]
    assert stale["chooser_role"] == changed[
        "multi_pokemon_ko_triggers"
    ][0]
    assert stale["status"] == "superseded_for_generic_e04_ordering"

    print("Ordering rule-change regression passed")


if __name__ == "__main__":
    main()
