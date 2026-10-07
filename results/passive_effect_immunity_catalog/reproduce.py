from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from passive_effect_immunity_catalog import (  # noqa: E402
    build_passive_effect_immunity_catalog,
)


def by_id(result, card_id: str):
    return next(row for row in result["rows"] if row["card_id"] == card_id)


def main() -> None:
    result = build_passive_effect_immunity_catalog(ROOT / "resources")
    assert result["print_rows"] == 49
    assert result["unique_names"] == 29
    assert result["rows_by_source_kind"] == {
        "ability": 43,
        "rule": 6,
    }
    assert result["rows_by_scope"] == {
        "attached_holder": 2,
        "multi_pokemon": 8,
        "player_hand": 1,
        "self": 38,
    }
    assert result["effects_only_rows"] == 27
    assert result["effects_and_damage_rows"] == 22

    parasol = by_id(result, "swsh3-157")
    assert parasol["card_name"] == "Big Parasol"
    assert parasol["scope"] == "multi_pokemon"
    assert not parasol["includes_damage"]

    mist = by_id(result, "sv5-161")
    assert mist["card_name"] == "Mist Energy"
    assert mist["scope"] == "attached_holder"
    assert not mist["includes_damage"]

    mew = by_id(result, "xy12-53")
    assert mew["card_name"] == "Mew"
    assert mew["scope"] == "self"
    assert mew["includes_damage"]

    skeledirge = by_id(result, "sv8-31")
    assert skeledirge["scope"] == "self"
    assert not skeledirge["includes_damage"]

    toedscruel = by_id(result, "sv3-22")
    assert toedscruel["scope"] == "multi_pokemon"
    assert not toedscruel["includes_damage"]

    print(
        {
            key: value
            for key, value in result.items()
            if key != "rows"
        }
    )


if __name__ == "__main__":
    main()
