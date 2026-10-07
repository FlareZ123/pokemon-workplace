from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_damage_notation_catalog import (  # noqa: E402
    DamageNotation,
    build_damage_notation_catalog,
    parse_damage_notation,
)


def main() -> None:
    result = build_damage_notation_catalog(ROOT / "resources")
    print({"total_attacks": result["total_attacks"], "counts": result["counts"]})

    assert result["total_attacks"] == 19992
    assert result["counts"] == {
        "blank": 3816,
        "fixed": 12312,
        "minus": 46,
        "plus": 2513,
        "times": 1305,
    }

    assert parse_damage_notation("200").notation == DamageNotation.FIXED
    assert parse_damage_notation("60+").notation == DamageNotation.PLUS
    assert parse_damage_notation("240-").notation == DamageNotation.MINUS
    assert parse_damage_notation("40×").notation == DamageNotation.TIMES
    assert parse_damage_notation("").notation == DamageNotation.BLANK

    minus = result["examples"]["minus"]
    assert minus["card_id"] == "bw10-51"
    assert minus["attack_name"] == "Shoulder Throw"
    assert minus["damage"] == "80-"

    print({"minus_example": minus})


if __name__ == "__main__":
    main()
