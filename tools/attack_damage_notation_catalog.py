"""Classify printed attack-damage notation in the legal Expanded snapshot."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import re

from build_expanded_legality_baseline import classify_effective_legality


class DamageNotation(str, Enum):
    BLANK = "blank"
    FIXED = "fixed"
    PLUS = "plus"
    MINUS = "minus"
    TIMES = "times"


@dataclass(frozen=True)
class ParsedDamageNotation:
    notation: DamageNotation
    base: int | None


_FIXED = re.compile(r"^(\d+)$")
_PLUS = re.compile(r"^(\d+)\+$")
_MINUS = re.compile(r"^(\d+)-$")
_TIMES = re.compile(r"^(\d+)[×xX]$")


def parse_damage_notation(damage: str) -> ParsedDamageNotation:
    value = damage.strip()
    if not value:
        return ParsedDamageNotation(DamageNotation.BLANK, None)

    for pattern, notation in (
        (_FIXED, DamageNotation.FIXED),
        (_PLUS, DamageNotation.PLUS),
        (_MINUS, DamageNotation.MINUS),
        (_TIMES, DamageNotation.TIMES),
    ):
        match = pattern.fullmatch(value)
        if match is not None:
            return ParsedDamageNotation(notation, int(match.group(1)))

    raise ValueError(f"unsupported printed attack damage notation: {damage!r}")


def build_damage_notation_catalog(resources_root: Path) -> dict[str, object]:
    sets = json.loads((resources_root / "sets" / "en.json").read_text(encoding="utf-8"))
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    counts: Counter[str] = Counter()
    examples: dict[str, dict[str, str]] = {}
    total = 0

    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        cards = json.loads(path.read_text(encoding="utf-8"))
        for card in cards:
            if classify_effective_legality(card)[0] != "Legal":
                continue
            for attack in card.get("attacks") or ():
                parsed = parse_damage_notation(attack.get("damage") or "")
                total += 1
                counts[parsed.notation.value] += 1
                examples.setdefault(
                    parsed.notation.value,
                    {
                        "card_id": card["id"],
                        "card_name": card["name"],
                        "attack_name": attack["name"],
                        "damage": attack.get("damage") or "",
                        "text": attack.get("text") or "",
                    },
                )

    return {
        "total_attacks": total,
        "counts": dict(sorted(counts.items())),
        "examples": examples,
    }
