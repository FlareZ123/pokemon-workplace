"""Reproduce paper Expanded Snorlax Block escape inventory for 8 Aichi 60s."""

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

from audit import (
    SOURCES,
    audit_one,
    load_manifest_60,
    parse_english_60,
    verify_printed_roles,
)
from tools.deck_validator import load_all_card_records


def main() -> None:
    verify_printed_roles()
    records = load_all_card_records(ROOT / "resources")

    results = {
        name: audit_one(parse_english_60(folder), records)
        for name, folder in SOURCES.items()
    }
    results["Snorlax 4Block"] = audit_one(load_manifest_60(), records)

    for name, category, expected in (
        ("Shadow Rider", "Guzma", 1),
        ("Vileplume control", "Jet Energy", 2),
        ("Raichu/Electrode", "Escape Rope", 3),
        ("Raichu/Electrode", "Klefki", 1),
        ("Mew/Genesect", "Guzma", 2),
        ("Mew/Genesect", "Escape Rope", 1),
        ("Iron Thorns English", "Guzma", 3),
        ("Mega Absol/Garbodor", "Garbodor", 2),
        ("Regidrago VSTAR", "Wobbuffet", 1),
        ("Regidrago VSTAR", "Prime Catcher", 1),
        ("Snorlax 4Block", "Articuno-GX", 1),
    ):
        assert results[name]["present"][category] == expected, (
            name, category, expected,
        )

    assert results["Vileplume control"]["nominal"] == 5
    assert results["Shadow Rider"]["nominal"] == 2
    assert results["Raichu/Electrode"]["nominal"] == 3
    assert results["Mew/Genesect"]["nominal"] == 3
    assert results["Iron Thorns English"]["nominal"] == 3
    assert results["Mega Absol/Garbodor"]["nominal"] == 1
    assert results["Regidrago VSTAR"]["nominal"] == 3
    assert results["Snorlax 4Block"]["nominal"] == 3

    for name, row in results.items():
        print(name)
        print(f"  starting Basic count: {row['basic']}")
        print(f"  reviewed non-Basic escape resources: {row['nominal']}")
        print(f"  conditional valid-hand nominal access: {float(row['probability'])*100:.6f}%")
        print(f"  printed effect counts: {row['present']}")

    print("PASS: eight printed paper Expanded 60-card inventories")
    print("LIMIT: printed resource presence is not an executable switch or match win")


if __name__ == "__main__":
    main()
