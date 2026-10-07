"""Scan legal Expanded text that depends on Supporter hand play."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from build_expanded_legality_baseline import classify_effective_legality

HISTORY = re.compile(r"\bif (?:you|they) played\b.*supporter card.*from (?:your|their) hand.*\b(?:this turn|during this turn)\b", re.I)
REACTION = re.compile(r"\bwhenever\b.*\bplays?\b.*supporter card.*from .*hand", re.I)
LOCK = re.compile(r"\bcan.?t play any supporter cards from .*hand", re.I)


def _texts(card: dict[str, Any]) -> Iterable[tuple[str, str | None, str]]:
    for row in card.get("attacks") or []:
        yield "attack", row.get("name"), " ".join(row.get("text", "").split())
    for row in card.get("abilities") or []:
        yield "ability", row.get("name"), " ".join(row.get("text", "").split())
    for text in card.get("rules") or []:
        yield "rule", None, " ".join(text.split())


def _legal_cards(root: Path) -> Iterable[dict[str, Any]]:
    sets = json.loads((root / "sets" / "en.json").read_text(encoding="utf-8"))
    legal_sets = {s["id"] for s in sets if (s.get("legalities") or {}).get("expanded") == "Legal"}
    for path in sorted((root / "cards" / "en").glob("*.json")):
        if path.stem not in legal_sets:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            if classify_effective_legality(card)[0] == "Legal":
                yield card


def _qualifier(text: str) -> str:
    low = text.lower()
    if "team rocket" in low:
        return "team_rocket_name"
    for label in ("ancient", "future", "tag team", "single strike", "rapid strike"):
        if f"{label} supporter" in low:
            return label.replace(" ", "_")
    return "any_supporter"


def supporter_play_sensitive_rows(root: Path) -> list[dict[str, Any]]:
    rows = []
    for card in _legal_cards(root):
        for source, effect, text in _texts(card):
            low = text.lower()
            if "supporter card" not in low or "hand" not in low:
                continue
            if HISTORY.search(text):
                category, qualifier = "history_gate", _qualifier(text)
            elif REACTION.search(text):
                category, qualifier = "play_reaction", None
            elif LOCK.search(text):
                category, qualifier = "play_lock", None
            else:
                continue
            rows.append({
                "id": card["id"], "name": card["name"],
                "source_class": source, "effect_name": effect,
                "category": category, "qualifier": qualifier, "text": text,
            })
    return rows


def summarize_sensitive_rows(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(rows)
    categories = Counter(r["category"] for r in rows)
    qualifiers = Counter(r["qualifier"] for r in rows if r["category"] == "history_gate")
    return {
        "print_rows": len(rows),
        "unique_card_names": len({r["name"] for r in rows}),
        "categories": dict(sorted(categories.items())),
        "history_qualifiers": dict(sorted(qualifiers.items())),
    }
