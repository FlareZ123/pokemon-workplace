from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_release_catalog import scan_bench_release_catalog  # noqa: E402


def main() -> None:
    result = scan_bench_release_catalog(ROOT / "resources")

    assert result["print_count"] == 50
    assert result["signature_count"] == 22
    assert result["unique_names"] == 20
    assert result["gameplay_variants"] == 22
    assert result["names"] == [
        "Acerola",
        "Bellelba & Brycen-Man",
        "Cassius",
        "Cheren's Care",
        "Chimecho",
        "Cofagrigus",
        "Corviknight",
        "Dragapult",
        "Giovanni's Exile",
        "Hydreigon",
        "M Gardevoir-EX",
        "Pelipper",
        "Penny",
        "Professor Turo's Scenario",
        "Scoop Up Cyclone",
        "Super Scoop Up",
        "Swoobat",
        "Tsareena V",
        "Virizion-GX",
        "Volo",
    ]

    families: dict[str, set[str]] = {
        "Item": set(),
        "Supporter": set(),
        "Ability": set(),
        "Attack": set(),
    }
    for row in result["signatures"]:
        source = row["source_class"]
        if source.startswith("Trainer:Item"):
            family = "Item"
        elif source.startswith("Trainer:Supporter"):
            family = "Supporter"
        else:
            family = source
        families[family].add(row["name"])

    assert families == {
        "Item": {"Scoop Up Cyclone", "Super Scoop Up"},
        "Supporter": {
            "Acerola",
            "Bellelba & Brycen-Man",
            "Cassius",
            "Cheren's Care",
            "Giovanni's Exile",
            "Penny",
            "Professor Turo's Scenario",
            "Volo",
        },
        "Ability": {"Corviknight", "Hydreigon"},
        "Attack": {
            "Chimecho",
            "Cofagrigus",
            "Dragapult",
            "M Gardevoir-EX",
            "Pelipper",
            "Swoobat",
            "Tsareena V",
            "Virizion-GX",
        },
    }

    super_scoop = [row for row in result["signatures"] if row["name"] == "Super Scoop Up"]
    assert len(super_scoop) == 1
    assert super_scoop[0]["stochastic"] is True

    cyclone = [row for row in result["signatures"] if row["name"] == "Scoop Up Cyclone"]
    assert len(cyclone) == 3
    assert all(row["stochastic"] is False for row in cyclone)

    print(
        f"prints={result['print_count']} signatures={result['signature_count']} "
        f"names={result['unique_names']} variants={result['gameplay_variants']}"
    )
    for family in ("Item", "Ability", "Supporter", "Attack"):
        print(f"{family}: {len(families[family])} names -> {sorted(families[family])}")


if __name__ == "__main__":
    main()
