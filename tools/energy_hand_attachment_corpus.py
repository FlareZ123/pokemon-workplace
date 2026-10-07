"""Census legal Expanded text that reacts to Energy attachment from hand."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

from build_expanded_legality_baseline import classify_effective_legality

TRIGGER = re.compile(
    r"(?:whenever [^.]*?\battach(?:es)?\b|when you attach\b|when your opponent attaches\b|when any player attaches\b).*?\bEnergy\b.*?\bfrom\b.*?\bhand\b",
    re.I,
)


def _texts(card: dict[str, Any]) -> Iterable[tuple[str, str | None, str]]:
    for row in card.get("attacks") or []:
        yield "attack", row.get("name"), " ".join(row.get("text", "").split())
    for row in card.get("abilities") or []:
        yield "ability", row.get("name"), " ".join(row.get("text", "").split())
    for text in card.get("rules") or []:
        yield "rule", None, " ".join(text.split())


def energy_hand_attachment_trigger_rows(root: Path) -> list[dict[str, str | None]]:
    sets = json.loads((root / "sets" / "en.json").read_text(encoding="utf-8"))
    legal_sets = {s["id"] for s in sets if (s.get("legalities") or {}).get("expanded") == "Legal"}
    rows = []
    for path in sorted((root / "cards" / "en").glob("*.json")):
        if path.stem not in legal_sets:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            if classify_effective_legality(card)[0] != "Legal":
                continue
            for source, effect_name, text in _texts(card):
                if TRIGGER.search(text):
                    rows.append({
                        "id": card["id"], "name": card["name"],
                        "source_class": source, "effect_name": effect_name, "text": text,
                    })
    return rows
