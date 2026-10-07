"""Catalog fixed Retreat Cost delta text in effective paper Expanded cards."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

from build_expanded_legality_baseline import classify_effective_legality
from retreat_cost_semantics import parse_fixed_retreat_cost_deltas


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _effect_rows(card: dict[str, Any]):
    for ability in card.get("abilities") or []:
        yield "ability", ability.get("name") or "", ability.get("text") or ""
    for attack in card.get("attacks") or []:
        yield "attack", attack.get("name") or "", attack.get("text") or ""
    for index, rule in enumerate(card.get("rules") or []):
        yield "rule", str(index), rule


def build(resources_root: Path) -> dict[str, Any]:
    sets = _load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    fixed_rows: list[dict[str, Any]] = []
    variable_rows: list[dict[str, Any]] = []

    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue

        for card in _load_json(path):
            status, _reason = classify_effective_legality(card)
            if status == "Banned":
                continue

            for source_kind, source_name, text in _effect_rows(card):
                if "Retreat Cost" not in text:
                    continue
                normalized = " ".join(text.split())
                parsed = parse_fixed_retreat_cost_deltas(
                    f"{card['id']}:{source_kind}:{source_name}",
                    normalized,
                )

                for modifier in parsed.modifiers:
                    fixed_rows.append({
                        "card_id": card["id"],
                        "card_name": card["name"],
                        "source_kind": source_kind,
                        "source_name": source_name,
                        "delta": modifier.delta,
                        "text": normalized,
                    })

                if parsed.variable_matches:
                    variable_rows.append({
                        "card_id": card["id"],
                        "card_name": card["name"],
                        "source_kind": source_kind,
                        "source_name": source_name,
                        "matches": parsed.variable_matches,
                        "text": normalized,
                    })

    by_source_kind = Counter(row["source_kind"] for row in fixed_rows)
    by_delta = Counter(row["delta"] for row in fixed_rows)

    return {
        "fixed": {
            "print_effect_rows": len(fixed_rows),
            "distinct_texts": len({row["text"] for row in fixed_rows}),
            "by_source_kind": dict(sorted(by_source_kind.items())),
            "by_delta": dict(sorted(by_delta.items())),
            "rows": fixed_rows,
        },
        "variable": {
            "print_effect_rows": len(variable_rows),
            "distinct_texts": len({row["text"] for row in variable_rows}),
            "rows": variable_rows,
        },
    }


def main() -> None:
    import sys

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
    print(json.dumps(build(root), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
