from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from delayed_ko_window import DelayedKoWindow, build_window_catalog  # noqa: E402


def main() -> None:
    window = DelayedKoWindow(first_damage=150, later_damage_counters=6)
    assert window.min_remaining_hp == 160
    assert window.max_remaining_hp == 210
    assert not window.qualifies(hp=150)
    assert window.qualifies(hp=160)
    assert window.qualifies(hp=210)
    assert not window.qualifies(hp=220)

    assert window.qualifies(hp=260, existing_damage_counters=5)
    assert not window.qualifies(hp=270, existing_damage_counters=5)

    result = build_window_catalog(ROOT / "resources", window)
    print(result)

    assert result["window"] == {
        "min_remaining_hp": 160,
        "max_remaining_hp": 210,
    }
    assert result["legal_pokemon_prints"] == 12504
    assert result["matching_prints"] == 1653
    assert result["matching_unique_names"] == 544
    assert result["matching_distinct_fingerprints"] == 858
    assert result["matching_prints_by_hp"] == {
        160: 258,
        170: 327,
        180: 350,
        190: 176,
        200: 201,
        210: 341,
    }
    assert result["matching_prints_by_prize_value"] == {
        1: 428,
        2: 1225,
    }
    assert result["matching_fingerprints_by_prize_value"] == {
        1: 338,
        2: 520,
    }


if __name__ == "__main__":
    main()
