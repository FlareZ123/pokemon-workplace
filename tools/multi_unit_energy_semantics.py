from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

OFFICIAL_BAN_OVERLAY = {
    "swsh2-22",
    "swsh45sv-SV013",
    "swsh10tg-TG02",
    "swshp-SWSH022",
    "swsh7-83",
    "swsh7-185",
    "swsh7-186",
}
ENERGY_TYPES = (
    "Grass",
    "Fire",
    "Water",
    "Lightning",
    "Psychic",
    "Fighting",
    "Darkness",
    "Metal",
    "Fairy",
    "Colorless",
)
FIXED_DISCARD = re.compile(
    r"Discard (an|\d+) Energy (?:attached to|from) this Pokémon",
    re.IGNORECASE,
)
ALL_DISCARD = re.compile(
    r"Discard all Energy (?:attached to|from) this Pokémon",
    re.IGNORECASE,
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    return " ".join(text.split())


def maximum_units_from_text(text: str) -> int:
    maximum = 1
    for match in re.finditer(
        r"provides(?: only)? (\d+) Energy at a time",
        text,
        re.IGNORECASE,
    ):
        maximum = max(maximum, int(match.group(1)))

    for match in re.finditer(
        r"provides (\d+) in any combination",
        text,
        re.IGNORECASE,
    ):
        maximum = max(maximum, int(match.group(1)))

    for energy_type in ENERGY_TYPES:
        pattern = re.compile(rf"((?:{energy_type})+) Energy")
        for match in pattern.finditer(text):
            maximum = max(
                maximum,
                len(match.group(1)) // len(energy_type),
            )

    return maximum


def build(resources_root: Path) -> dict[str, Any]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    multi_unit_prints: list[dict[str, Any]] = []
    generic_discard_prints: list[dict[str, Any]] = []

    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue

        for card in load_json(path):
            database_status = (card.get("legalities") or {}).get("expanded")
            if card["id"] in OFFICIAL_BAN_OVERLAY or database_status == "Banned":
                continue

            if card.get("supertype") == "Energy":
                text = normalize(" ".join(card.get("rules") or []))
                maximum_units = maximum_units_from_text(text)
                if maximum_units > 1:
                    multi_unit_prints.append(
                        {
                            "card_id": card["id"],
                            "card_name": card["name"],
                            "maximum_units": maximum_units,
                            "text": text,
                        }
                    )

            for attack in card.get("attacks") or []:
                text = normalize(attack.get("text") or "")
                match = FIXED_DISCARD.search(text)
                if match:
                    token = match.group(1).lower()
                    count = 1 if token == "an" else int(token)
                    generic_discard_prints.append(
                        {
                            "card_id": card["id"],
                            "card_name": card["name"],
                            "attack_name": attack["name"],
                            "damage": attack.get("damage") or "",
                            "text": text,
                            "discard_units": count,
                        }
                    )
                elif ALL_DISCARD.search(text):
                    generic_discard_prints.append(
                        {
                            "card_id": card["id"],
                            "card_name": card["name"],
                            "attack_name": attack["name"],
                            "damage": attack.get("damage") or "",
                            "text": text,
                            "discard_units": "all",
                        }
                    )

    energy_signatures: dict[tuple[str, int, str], list[str]] = defaultdict(list)
    for row in multi_unit_prints:
        energy_signatures[
            (row["card_name"], row["maximum_units"], row["text"])
        ].append(row["card_id"])

    attack_signatures: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in generic_discard_prints:
        key = (row["attack_name"], row["damage"], row["text"])
        attack_signatures.setdefault(key, row)

    discard_counts = Counter(
        row["discard_units"] for row in attack_signatures.values()
    )
    energy_rows = [
        {
            "card_name": name,
            "maximum_units": maximum_units,
            "text": text,
            "print_ids": sorted(print_ids),
        }
        for (name, maximum_units, text), print_ids in energy_signatures.items()
    ]

    return {
        "multi_unit_energy": {
            "print_instances": len(multi_unit_prints),
            "distinct_names": len(
                {row["card_name"] for row in multi_unit_prints}
            ),
            "text_signatures": len(energy_rows),
            "rows": sorted(
                energy_rows,
                key=lambda row: (row["card_name"], row["text"]),
            ),
        },
        "generic_self_discard_attacks": {
            "print_instances": len(generic_discard_prints),
            "distinct_signatures": len(attack_signatures),
            "signature_counts_by_required_energy": {
                str(key): discard_counts[key]
                for key in sorted(
                    discard_counts,
                    key=lambda value: (value == "all", str(value)),
                )
            },
            "fixed_two_or_more_signatures": sum(
                count
                for key, count in discard_counts.items()
                if isinstance(key, int) and key >= 2
            ),
        },
    }


def main() -> None:
    import sys

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
    print(json.dumps(build(root), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
