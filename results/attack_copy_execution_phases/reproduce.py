from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_execution_phases import build


def row_for(result: dict, attack_name: str) -> dict:
    rows = [row for row in result["signatures"] if row["attack_name"] == attack_name]
    assert len(rows) == 1
    return rows[0]


def main() -> None:
    result = build(ROOT / "resources")

    assert result["scope"] == {
        "format": "paper Expanded, Black & White onward",
        "effectively_legal_cards_scanned": 14829,
        "copy_attack_print_rows": 64,
        "copy_attack_signatures": 30,
    }
    assert result["trailing_semantics_counts"] == {
        "explanatory_reminder": 1,
        "gx_usage_rule": 1,
        "none": 26,
        "post_copy_cleanup": 1,
        "selected_attack_energy_gate": 1,
    }

    assert {
        row["attack_name"]: row["selected_attack_energy_gate_position"]
        for row in result["energy_gate_rows"]
    } == {
        "Copy Anything": "after_copy_clause",
        "Imittack": "before_copy_clause",
    }

    assert {
        row["attack_name"]: row["source_lifetime_pattern"]
        for row in result["source_lifetime_rows"]
    } == {
        "Hypnotic Reign": "selected_source_discarded_from_opponent_hand_before_body",
        "Seek Inspiration": "top_card_discarded_before_eligibility_and_body",
    }

    assert row_for(result, "Haughty Order")["trailing_semantics"] == "post_copy_cleanup"
    assert row_for(result, "Trickster-GX")["trailing_semantics"] == "gx_usage_rule"
    assert row_for(result, "Seek Inspiration")["trailing_semantics"] == "explanatory_reminder"
    assert not any(
        row["trailing_semantics"] == "unclassified"
        for row in result["signatures"]
    )

    print("attack-copy execution phase regression: PASS")
    print(result["scope"])
    print(result["trailing_semantics_counts"])


if __name__ == "__main__":
    main()
