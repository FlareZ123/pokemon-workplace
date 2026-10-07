from __future__ import annotations

import json
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


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    return " ".join(text.split())


def classify(text: str) -> str:
    lower = text.lower()

    if (
        "discard" in lower
        and "opponent's active" in lower
        and "pokémon tool" in lower
        and "special energy" in lower
    ):
        return "opponent_tool_and_special_energy_removal"

    if (
        "discard" in lower
        and (
            "defending pokémon" in lower
            or "opponent's active" in lower
        )
        and "pokémon tool" in lower
    ):
        return "opponent_tool_removal"

    if (
        "discard" in lower
        and (
            "defending pokémon" in lower
            or "opponent's active" in lower
        )
        and "special energy" in lower
    ):
        return "opponent_special_energy_removal"

    if (
        "discard" in lower
        and "from your pokémon" in lower
        and "pokémon tool" in lower
    ):
        return "own_tool_variable_damage"

    if "discard all pokémon tools from this pokémon" in lower:
        return "self_tool_gate"

    if "attach any number of basic water energy" in lower:
        return "self_energy_attach_before_damage"

    if "switch" in lower and "opponent" in lower:
        return "opponent_switch_before_damage"

    if "flip a coin" in lower:
        return "coin_before_damage"

    return "other"


def build(resources_root: Path) -> dict[str, Any]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    print_rows = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue

        for card in load_json(path):
            database_status = (card.get("legalities") or {}).get("expanded")
            if card["id"] in OFFICIAL_BAN_OVERLAY or database_status == "Banned":
                continue

            for attack in card.get("attacks") or []:
                text = normalize(attack.get("text") or "")
                if "Before doing damage" not in text:
                    continue

                print_rows.append(
                    {
                        "card_id": card["id"],
                        "card_name": card["name"],
                        "types": card.get("types") or [],
                        "attack_name": attack["name"],
                        "damage": attack.get("damage") or "",
                        "text": text,
                        "category": classify(text),
                    }
                )

    signatures: dict[tuple[str, str, str], dict[str, Any]] = {}
    print_ids: dict[tuple[str, str, str], list[str]] = defaultdict(list)

    for row in print_rows:
        key = (row["attack_name"], row["damage"], row["text"])
        signatures.setdefault(key, row)
        print_ids[key].append(row["card_id"])

    rows = []
    for key, row in signatures.items():
        output = dict(row)
        output["print_ids"] = sorted(print_ids[key])
        rows.append(output)

    categories = Counter(row["category"] for row in rows)
    dragon_rows = [
        row for row in rows if "Dragon" in row["types"]
    ]

    return {
        "counts": {
            "print_instances": len(print_rows),
            "distinct_signatures": len(rows),
            "categories": dict(sorted(categories.items())),
            "dragon_signatures": len(dragon_rows),
        },
        "dragon_signatures": dragon_rows,
        "signatures": sorted(
            rows,
            key=lambda row: (
                row["category"],
                row["attack_name"],
                row["card_name"],
            ),
        ),
    }
