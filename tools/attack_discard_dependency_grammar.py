from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

IF_YOU_DO = re.compile(r"\bif you do\b(?!n)", re.IGNORECASE)
IF_YOU_DONT = re.compile(r"\bif you (?:don't|do not)\b", re.IGNORECASE)
THEN = re.compile(r"\bThen,", re.IGNORECASE)

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


def dependency_markers(text: str) -> tuple[str, ...]:
    markers: list[str] = []
    if IF_YOU_DO.search(text):
        markers.append("if_you_do")
    if IF_YOU_DONT.search(text):
        markers.append("if_you_dont")
    if "discarded in this way" in text.lower():
        markers.append("discarded_in_this_way")
    if THEN.search(text):
        markers.append("then")
    return tuple(markers) if markers else ("none",)


def build(resources_root: Path) -> dict[str, Any]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    groups: dict[str, dict[tuple[str, str, str], list[dict[str, str]]]] = {
        "mandatory_discard": defaultdict(list),
        "optional_discard": defaultdict(list),
    }
    print_counts = Counter()

    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            database_status = (card.get("legalities") or {}).get("expanded")
            if card["id"] in OFFICIAL_BAN_OVERLAY or database_status == "Banned":
                continue
            for attack in card.get("attacks") or []:
                text = normalize(attack.get("text") or "")
                if text.startswith("Discard "):
                    group = "mandatory_discard"
                elif text.startswith("You may discard "):
                    group = "optional_discard"
                else:
                    continue
                key = (attack["name"], attack.get("damage") or "", text)
                groups[group][key].append({"card_name": card["name"], "card_id": card["id"]})
                print_counts[group] += 1

    output: dict[str, Any] = {
        "scope": {
            "format": "paper Expanded",
            "families": [
                "attack text begins with 'Discard '",
                "attack text begins with 'You may discard '",
            ],
            "markers": ["if_you_do", "if_you_dont", "discarded_in_this_way", "then", "none"],
        },
        "groups": {},
    }

    for group_name, signatures in groups.items():
        combination_counts = Counter()
        marker_counts = Counter()
        rows = []
        for (attack_name, damage, text), sources in signatures.items():
            markers = dependency_markers(text)
            combination_counts["+".join(markers)] += 1
            for marker in markers:
                marker_counts[marker] += 1
            rows.append(
                {
                    "attack_name": attack_name,
                    "damage": damage,
                    "text": text,
                    "markers": list(markers),
                    "card_names": sorted({row["card_name"] for row in sources}),
                    "print_ids": sorted(row["card_id"] for row in sources),
                }
            )
        output["groups"][group_name] = {
            "print_instances": print_counts[group_name],
            "distinct_signatures": len(signatures),
            "marker_counts": dict(sorted(marker_counts.items())),
            "combination_counts": dict(sorted(combination_counts.items())),
            "signatures": sorted(rows, key=lambda row: (row["attack_name"], row["text"])),
        }

    return output


def main() -> None:
    resources_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
    result = build(resources_root)
    summary = {
        name: {key: value for key, value in group.items() if key != "signatures"}
        for name, group in result["groups"].items()
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
