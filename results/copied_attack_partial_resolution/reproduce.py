from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.copied_attack_partial_resolution import build  # noqa: E402


def get_signature(result: dict, attack_name: str) -> dict:
    matches = [row for row in result["signatures"] if row["attack_name"] == attack_name]
    assert len(matches) == 1, (attack_name, len(matches))
    return matches[0]


def main() -> None:
    result = build(ROOT / "resources")
    assert result["counts"] == {
        "matching_prints": 145,
        "distinct_attack_signatures": 70,
        "discard_count_dependent_signatures": 12,
        "independent_output_signatures": 58,
        "independent_specific_type_signatures": 11,
        "independent_discard_scopes": {
            "all_energy": 47,
            "fire": 4,
            "lightning": 6,
            "psychic": 1,
        },
    }

    crimson = get_signature(result, "Crimson Blaster")
    assert crimson["discard_scope"] == "fire"
    assert crimson["independent_output"] is True
    assert crimson["damage"] == ""
    assert "180 damage" in crimson["text"]

    fulgurite = get_signature(result, "Fulgurite")
    assert fulgurite["discard_scope"] == "all_energy"
    assert fulgurite["independent_output"] is True
    assert "can't play any Item" in fulgurite["text"]

    onyx = get_signature(result, "Onyx")
    assert onyx["independent_output"] is True
    assert "take a Prize card" in onyx["text"]

    photon = get_signature(result, "Photon Geyser")
    assert photon["output_depends_on_discard_count"] is True
    assert photon["independent_output"] is False

    print(result["counts"])


if __name__ == "__main__":
    main()
