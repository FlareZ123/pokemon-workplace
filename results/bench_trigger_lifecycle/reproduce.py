from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_trigger_lifecycle import scan_bench_trigger_lifecycle  # noqa: E402


def main() -> None:
    result = scan_bench_trigger_lifecycle(ROOT / "resources")

    assert result["trigger_print_count"] == 123
    assert result["trigger_name_count"] == 48
    assert result["self_vacating_print_count"] == 22
    assert result["self_vacating_name_count"] == 6
    assert result["self_vacating_gameplay_variants"] == 7
    assert result["ability_cleanup_count"] == 0
    assert result["self_vacating_names"] == [
        "Dedenne-GX",
        "Eldegoss V",
        "Kartana-GX",
        "Liepard V",
        "Lumineon V",
        "Meowth ex",
    ]

    by_name = {}
    for row in result["variants"]:
        by_name.setdefault(row["name"], []).append(row)

    assert by_name["Dedenne-GX"][0]["gx_attack"] is True
    assert by_name["Dedenne-GX"][0]["destination"] == "hand"
    assert by_name["Lumineon V"][0]["destination"] == "deck"
    assert by_name["Meowth ex"][0]["destination"] == "hand"

    print(
        f"trigger prints={result['trigger_print_count']} "
        f"trigger names={result['trigger_name_count']}"
    )
    print(
        f"self-vacating prints={result['self_vacating_print_count']} "
        f"names={result['self_vacating_name_count']} "
        f"gameplay variants={result['self_vacating_gameplay_variants']}"
    )
    print(f"self-vacating Abilities={result['ability_cleanup_count']}")
    for row in result["variants"]:
        print(
            f"{row['name']}: {row['attack']} -> {row['destination']} "
            f"cost={','.join(row['attack_cost']) or 'none'} "
            f"optional={row['optional_cleanup']} gx={row['gx_attack']}"
        )


if __name__ == "__main__":
    main()
