"""Catalog effectively legal Special Energy with end-of-turn self-discard."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from build_expanded_legality_baseline import classify_effective_legality


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build(resources_root: Path) -> dict[str, Any]:
    sets = _load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    rows: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in _load_json(path):
            if card.get("supertype") != "Energy":
                continue
            if "Special" not in (card.get("subtypes") or []):
                continue
            status, _reason = classify_effective_legality(card)
            if status == "Banned":
                continue

            text = " ".join(" ".join(card.get("rules") or []).split())
            lower = text.lower()
            if "discard" not in lower or "end of the turn" not in lower:
                continue

            rows.append({
                "card_id": card["id"],
                "card_name": card["name"],
                "attachment_turn_only": (
                    "end of the turn you attached it" in lower
                ),
                "text": text,
            })

    return {
        "print_rows": len(rows),
        "distinct_names": len({row["card_name"] for row in rows}),
        "rows": rows,
    }


def main() -> None:
    import sys

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
    print(json.dumps(build(root), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
