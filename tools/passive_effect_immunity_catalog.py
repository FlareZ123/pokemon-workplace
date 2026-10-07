"""Catalog passive Ability/attachment sources of attack-effect immunity."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from build_expanded_legality_baseline import classify_effective_legality


def _scope(text: str) -> str:
    lower = text.casefold()
    if "you or your hand" in lower:
        return "player_hand"
    if (
        "all of your pokémon" in lower
        or "your basic team rocket's pokémon" in lower
    ):
        return "multi_pokemon"
    if "the pokémon this card is attached to" in lower:
        return "attached_holder"
    return "self"


def build_passive_effect_immunity_catalog(
    resources_root: Path,
) -> dict[str, object]:
    sets = json.loads(
        (resources_root / "sets" / "en.json").read_text(encoding="utf-8")
    )
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    rows = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            if classify_effective_legality(card)[0] != "Legal":
                continue

            sources = [
                ("ability", ability.get("name"), ability.get("text") or "")
                for ability in (card.get("abilities") or ())
            ]
            sources.extend(
                ("rule", None, rule)
                for rule in (card.get("rules") or ())
            )

            for source_kind, source_name, text in sources:
                if "prevent all effects of attacks" not in text.casefold():
                    continue
                rows.append(
                    {
                        "card_id": card["id"],
                        "card_name": card["name"],
                        "source_kind": source_kind,
                        "source_name": source_name,
                        "scope": _scope(text),
                        "includes_damage": "including damage" in text.casefold(),
                        "text": text,
                    }
                )

    return {
        "print_rows": len(rows),
        "unique_names": len({row["card_name"] for row in rows}),
        "rows_by_source_kind": dict(
            sorted(Counter(row["source_kind"] for row in rows).items())
        ),
        "rows_by_scope": dict(
            sorted(Counter(row["scope"] for row in rows).items())
        ),
        "effects_only_rows": sum(
            not row["includes_damage"] for row in rows
        ),
        "effects_and_damage_rows": sum(
            row["includes_damage"] for row in rows
        ),
        "rows": rows,
    }
