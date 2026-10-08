"""Audited English Expanded text surface reacting to Trainer plays.

This is a bounded phrase catalog, not an oracle for triggered-effect timing.
Import the repository's existing effective print legality classifier.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re

from tools.build_expanded_legality_baseline import (
    classify_effective_legality, load_json,
)


_REACTION = re.compile(
    r"\bwhenever\b.*?\bplays?\b.*?\b(?:Item|Supporter|Trainer)\b",
    re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True)
class TrainerPlayReaction:
    card_id: str
    card_name: str
    source: str
    label: str
    text: str
    classification: str


def _text_parts(card: dict) -> tuple[tuple[str, str, str], ...]:
    parts = [
        (zone, row.get("name", ""), row.get("text", ""))
        for zone in ("abilities", "attacks")
        for row in card.get(zone, [])
    ]
    parts.extend(("rules", "rule", text) for text in card.get("rules", []))
    return tuple(parts)


def catalog(
    resources_root: Path,
    *,
    as_of: date = date(2026, 10, 8),
) -> tuple[TrainerPlayReaction, ...]:
    """Only English print records from eligible Expanded sets released by as_of."""
    sets = {
        row["id"]: row
        for row in load_json(resources_root / "sets" / "en.json")
        if row.get("legalities", {}).get("expanded") == "Legal"
        and date.fromisoformat(row["releaseDate"].replace("/", "-")) <= as_of
    }
    out = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in sets:
            continue
        for card in load_json(path):
            status, _reason = classify_effective_legality(card)
            if status != "Legal":
                continue
            for source, label, text in _text_parts(card):
                if not _REACTION.search(text):
                    continue
                if "prevent all effects of that card" in text.lower():
                    cls = "deterministic_card_effect_protection"
                elif "flips a coin" in text.lower() and "no effect" in text.lower():
                    cls = "coin_gated_card_nullification"
                else:
                    cls = "uncategorized"
                out.append(TrainerPlayReaction(
                    card_id=card["id"],
                    card_name=card["name"],
                    source=source,
                    label=label,
                    text=text,
                    classification=cls,
                ))
    return tuple(sorted(out, key=lambda row: (row.card_id, row.source, row.label)))
