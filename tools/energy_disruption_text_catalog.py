"""Inventory legal Expanded text that discards Energy from an opponent's Pokemon."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

from build_expanded_legality_baseline import classify_effective_legality


@dataclass(frozen=True)
class EnergyDisruptionText:
    card_id: str
    name: str
    source_kind: str
    source_name: str | None
    text: str


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _legal_expanded_cards(resources_root: Path) -> tuple[dict[str, Any], ...]:
    sets = _load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }
    cards: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in _load_json(path):
            if classify_effective_legality(card)[0] == "Legal":
                cards.append(card)
    return tuple(cards)


def _mentions_opponent_energy_discard(text: str) -> bool:
    lower = text.casefold()
    return (
        "discard" in lower
        and "energy" in lower
        and "opponent" in lower
        and "pokémon" in lower
    )


def catalog_energy_disruption_texts(
    resources_root: Path = Path("resources"),
) -> tuple[EnergyDisruptionText, ...]:
    rows: list[EnergyDisruptionText] = []
    for card in _legal_expanded_cards(resources_root):
        for rule in card.get("rules") or ():
            text = _normalized(rule)
            if _mentions_opponent_energy_discard(text):
                rows.append(EnergyDisruptionText(
                    card["id"], card["name"], "trainer", None, text
                ))
        for attack in card.get("attacks") or ():
            text = _normalized(attack.get("text") or "")
            if _mentions_opponent_energy_discard(text):
                rows.append(EnergyDisruptionText(
                    card["id"],
                    card["name"],
                    "attack",
                    attack.get("name"),
                    text,
                ))
    return tuple(sorted(
        rows,
        key=lambda row: (
            row.text,
            row.source_kind,
            row.name,
            row.card_id,
            row.source_name or "",
        ),
    ))


def text_summary(rows: tuple[EnergyDisruptionText, ...]) -> dict[str, object]:
    counts = Counter(row.text for row in rows)
    return {
        "profile_count": len(rows),
        "unique_names": len({row.name for row in rows}),
        "unique_texts": len(counts),
        "texts": tuple(
            (text, count)
            for text, count in sorted(counts.items())
        ),
    }
