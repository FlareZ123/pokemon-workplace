"""Inventory literal Weakness and Resistance modifiers in legal Expanded cards."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import re

from build_expanded_legality_baseline import classify_effective_legality


class TypeModifierKind(str, Enum):
    MULTIPLY = "multiply"
    ADD = "add"
    SUBTRACT = "subtract"


@dataclass(frozen=True)
class ParsedTypeModifier:
    kind: TypeModifierKind
    amount: int


_MULTIPLY = re.compile(r"^[×xX](\d+)$")
_ADD = re.compile(r"^\+(\d+)$")
_SUBTRACT = re.compile(r"^-(\d+)$")


def parse_type_modifier(value: str) -> ParsedTypeModifier:
    for pattern, kind in (
        (_MULTIPLY, TypeModifierKind.MULTIPLY),
        (_ADD, TypeModifierKind.ADD),
        (_SUBTRACT, TypeModifierKind.SUBTRACT),
    ):
        match = pattern.fullmatch(value.strip())
        if match is not None:
            return ParsedTypeModifier(kind, int(match.group(1)))
    raise ValueError(f"unsupported type modifier: {value!r}")


def build_type_modifier_catalog(resources_root: Path) -> dict[str, object]:
    sets = json.loads(
        (resources_root / "sets" / "en.json").read_text(encoding="utf-8")
    )
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    weakness_counts: Counter[str] = Counter()
    resistance_counts: Counter[str] = Counter()
    unusual_weaknesses = []
    unusual_resistances = []

    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            if classify_effective_legality(card)[0] != "Legal":
                continue
            if card.get("supertype") != "Pokémon":
                continue

            for row in card.get("weaknesses") or ():
                value = row["value"]
                parse_type_modifier(value)
                weakness_counts[value] += 1
                if value != "×2":
                    unusual_weaknesses.append(
                        {
                            "card_id": card["id"],
                            "name": card["name"],
                            "type": row["type"],
                            "value": value,
                        }
                    )

            for row in card.get("resistances") or ():
                value = row["value"]
                parse_type_modifier(value)
                resistance_counts[value] += 1
                if value not in {"-20", "-30"}:
                    unusual_resistances.append(
                        {
                            "card_id": card["id"],
                            "name": card["name"],
                            "type": row["type"],
                            "value": value,
                        }
                    )

    return {
        "weakness_counts": dict(sorted(weakness_counts.items())),
        "resistance_counts": dict(sorted(resistance_counts.items())),
        "unusual_weaknesses": unusual_weaknesses,
        "unusual_resistances": unusual_resistances,
    }
