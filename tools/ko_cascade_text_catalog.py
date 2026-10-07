"""Find legal Ability texts that can create a second KO during KO handling."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from build_expanded_legality_baseline import classify_effective_legality


def normalize(text: str) -> str:
    return " ".join(text.split())


def normalized_knocked(text: str) -> str:
    return text.replace("Knocket Out", "Knocked Out")


def classify(text: str) -> str | None:
    value = normalized_knocked(text)
    lower = value.lower()
    if "is knocked out by damage" not in lower:
        return None
    if "attacking pokémon is knocked out" in lower:
        return "direct_attacker_ko"
    if (
        "damage counter" in lower
        and "attacking pokémon" in lower
        and ("put " in lower or "place " in lower)
    ):
        return "attacker_damage_counters"
    return None


def build(resources_root: Path) -> dict:
    sets = json.loads(
        (resources_root / "sets" / "en.json").read_text(encoding="utf-8")
    )
    expanded = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    rows = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded:
            continue
        cards = json.loads(path.read_text(encoding="utf-8"))
        for card in cards:
            if classify_effective_legality(card)[0] == "Banned":
                continue
            for ability in card.get("abilities") or []:
                text = normalize(ability.get("text") or "")
                category = classify(text)
                if category is None:
                    continue
                rows.append(
                    {
                        "card_id": card["id"],
                        "card_name": card["name"],
                        "ability_name": ability["name"],
                        "category": category,
                        "text": text,
                        "database_text_typo": "Knocket Out" in text,
                    }
                )

    counts = Counter(row["category"] for row in rows)
    return {
        "summary": {
            "matched_prints": len(rows),
            "matched_names": len({row["card_name"] for row in rows}),
            "prints_by_category": dict(sorted(counts.items())),
            "names_by_category": {
                category: sorted(
                    {
                        row["card_name"]
                        for row in rows
                        if row["category"] == category
                    }
                )
                for category in sorted(counts)
            },
            "database_text_typo_prints": sum(
                row["database_text_typo"] for row in rows
            ),
        },
        "rows": rows,
    }


def main() -> None:
    import sys

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
    print(json.dumps(build(root), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
