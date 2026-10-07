from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from type_modifier_catalog import build_type_modifier_catalog, parse_type_modifier  # noqa: E402


def main() -> None:
    result = build_type_modifier_catalog(ROOT / "resources")
    assert result["weakness_counts"] == {"+20": 1, "×2": 12171}
    assert result["resistance_counts"] == {
        "-20": 1769,
        "-30": 1515,
        "×2": 1,
    }
    weak = result["unusual_weaknesses"]
    resist = result["unusual_resistances"]
    assert len(weak) == 1
    assert weak[0]["card_id"] == "me55c-43"
    assert weak[0]["value"] == "+20"
    assert len(resist) == 1
    assert resist[0]["card_id"] == "me55-93"
    assert resist[0]["value"] == "×2"
    assert parse_type_modifier("×2").amount == 2
    assert parse_type_modifier("+20").amount == 20
    assert parse_type_modifier("-30").amount == 30
    print(result)


if __name__ == "__main__":
    main()
