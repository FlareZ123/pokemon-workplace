from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_catalog import OFFICIAL_BAN_OVERLAY, build


def get_signature(result: dict, attack_name: str) -> dict:
    matches = [row for row in result["signatures"] if row["attack_name"] == attack_name]
    assert len(matches) == 1, (attack_name, len(matches))
    return matches[0]


def main() -> None:
    result = build(ROOT / "resources")
    counts = result["counts"]

    assert result["scope"]["legal_prints_scanned"] == 14836
    assert counts["copy_attack_prints"] == 64
    assert counts["unique_copy_attack_signatures"] == 30
    assert counts["unique_card_names"] == 30
    assert counts["signatures_with_direct_non_gx_filter"] == 3
    assert counts["signatures_with_structural_same_attack_reentry"] == 25

    chain = result["notable_chain"]
    assert chain["outer"]["card_id"] == "smp-SM99"
    assert chain["middle"]["card_id"] == "swsh12-136"
    assert chain["endpoint"]["card_id"] == "sm5-100"
    assert chain["text_filter_checks"]["all_pass"] is True

    apex = get_signature(result, "Apex Dragon")
    assert apex["source_classes"] == ["own_discard_dragon"]
    assert apex["direct_non_gx_filter"] is False
    assert apex["structural_same_attack_reentry"] is True

    cross_fusion = get_signature(result, "Cross Fusion Strike")
    assert cross_fusion["source_classes"] == ["own_bench_fusion_strike"]
    assert cross_fusion["structural_same_attack_reentry"] is True

    catalog_print_ids = {print_id for row in result["signatures"] for print_id in row["print_ids"]}
    assert catalog_print_ids.isdisjoint(OFFICIAL_BAN_OVERLAY)

    print(counts)
    print(chain["text_filter_checks"])


if __name__ == "__main__":
    main()
