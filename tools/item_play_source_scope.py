"""Audit source-zone scope of direct Item-play prohibition effects."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re

from build_expanded_legality_baseline import classify_effective_legality

HAND_SOURCE_RE = re.compile(
    r"(?:from (?:his or her|their) hand|from hand)",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class ItemPlayRestriction:
    card_id: str
    card_name: str
    source: str
    text: str
    prohibited_source_zone: str


def _effect_rows(card: dict):
    for index, rule in enumerate(card.get("rules") or []):
        yield f"rule:{index}", rule
    for attack in card.get("attacks") or []:
        text = attack.get("text") or ""
        if text:
            yield f"attack:{attack.get('name', '')}", text
    for ability in card.get("abilities") or []:
        text = ability.get("text") or ""
        if text:
            yield f"ability:{ability.get('name', '')}", text


def build_item_play_restrictions(
    resources_root: Path,
) -> tuple[ItemPlayRestriction, ...]:
    """Return direct legal Item-play prohibitions with an explicit hand source."""

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
        cards = json.loads(path.read_text(encoding="utf-8"))
        for card in cards:
            status, _source = classify_effective_legality(card)
            if status != "Legal":
                continue

            for source, text in _effect_rows(card):
                lower = text.lower()
                if "can't play" not in lower or "item" not in lower:
                    continue
                if not HAND_SOURCE_RE.search(text):
                    raise ValueError(
                        "found direct Item-play prohibition without "
                        f"recognized source-zone wording: {card['id']} {text!r}"
                    )
                rows.append(
                    ItemPlayRestriction(
                        card["id"],
                        card["name"],
                        source,
                        text,
                        "hand",
                    )
                )

    return tuple(
        sorted(rows, key=lambda row: (row.card_id, row.source, row.text))
    )


def restriction_blocks_source(
    restriction: ItemPlayRestriction,
    source_zone: str,
) -> bool:
    if not source_zone:
        raise ValueError("source_zone must be non-empty")
    return restriction.prohibited_source_zone == source_zone
