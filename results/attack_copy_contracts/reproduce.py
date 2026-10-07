from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_contracts import build


def contract_for(result: dict, attack_name: str) -> dict:
    rows = [row for row in result["contracts"] if row["attack_name"] == attack_name]
    assert len(rows) == 1
    return rows[0]


def main() -> None:
    result = build(ROOT / "resources")

    assert result["signature_count"] == 30
    assert result["simple_tail_copy_signature_count"] == 24
    assert result["non_tail_signature_count"] == 6
    assert result["non_tail_attack_names"] == [
        "Copy Anything",
        "Haughty Order",
        "Hypnotic Reign",
        "Imittack",
        "Seek Inspiration",
        "Trickster-GX",
    ]
    assert result["non_tail_semantics_counts"] == {
        "outer_gx_usage_rule": 1,
        "post_copy_continuation": 1,
        "preselection_source_zone_commit": 1,
        "selected_energy_gate": 2,
        "selected_source_zone_commit": 1,
    }

    assert contract_for(result, "Copy Anything")["non_tail_semantics"] == [
        "selected_energy_gate"
    ]
    assert contract_for(result, "Haughty Order")["non_tail_semantics"] == [
        "post_copy_continuation"
    ]
    assert contract_for(result, "Hypnotic Reign")["non_tail_semantics"] == [
        "selected_source_zone_commit"
    ]
    assert contract_for(result, "Imittack")["non_tail_semantics"] == [
        "selected_energy_gate"
    ]
    assert contract_for(result, "Seek Inspiration")["non_tail_semantics"] == [
        "preselection_source_zone_commit"
    ]
    assert contract_for(result, "Trickster-GX")["non_tail_semantics"] == [
        "outer_gx_usage_rule"
    ]

    print("attack-copy contract compiler regression: PASS")
    print({
        "signatures": result["signature_count"],
        "simple_tail": result["simple_tail_copy_signature_count"],
        "non_tail": result["non_tail_signature_count"],
    })


if __name__ == "__main__":
    main()
