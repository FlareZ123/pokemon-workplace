"""Catalog paper-Expanded actions that can reveal exact Prize information.

Two mechanisms are mechanically sufficient in the bundled card pool:

* full remaining-deck inspection, because a player who knows the decklist and
  visible zones can infer the face-down Prize cards by elimination;
* direct inspection or face-up revelation of all of the player's remaining
  Prize cards.

The catalog deliberately separates partial top/bottom-deck and partial Prize
inspection effects. Those can update a belief state without necessarily
revealing the complete Prize composition.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from build_expanded_legality_baseline import OFFICIAL_BAN_OVERLAY


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _action_class(card: dict[str, Any], source: str) -> str:
    if source in {"Attack", "Ability"}:
        return source

    if card.get("supertype") == "Energy":
        return "Energy"

    subtypes = card.get("subtypes") or []
    for action_class in ("Supporter", "Stadium", "Pokémon Tool", "Item"):
        if action_class in subtypes:
            return action_class
    return card.get("supertype") or "Other"


def _effect_rows(card: dict[str, Any]) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for text in card.get("rules") or []:
        rows.append(("Rules", "", text))
    for ability in card.get("abilities") or []:
        rows.append(("Ability", ability.get("name") or "", ability.get("text") or ""))
    for attack in card.get("attacks") or []:
        rows.append(("Attack", attack.get("name") or "", attack.get("text") or ""))
    return rows


def _load_legal_cards(resources_root: Path) -> list[dict[str, Any]]:
    sets = json.loads((resources_root / "sets" / "en.json").read_text(encoding="utf-8"))
    legal_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    cards: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in legal_sets:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            if card["id"] in OFFICIAL_BAN_OVERLAY:
                continue
            if (card.get("legalities") or {}).get("expanded") == "Banned":
                continue
            cards.append(card)
    return cards


def _full_deck_inspection(text: str) -> bool:
    lowered = text.lower()
    return "search your deck" in lowered or "look through your deck" in lowered


def _exact_prize_inspection(text: str) -> bool:
    lowered = text.lower()
    if "look at your face-down prize cards" in lowered:
        return True
    if "turn all of your prize cards face up" in lowered:
        return True
    return bool(
        re.search(
            r"each player turns all of (?:his or her|their) prize cards face up",
            lowered,
        )
    )


def _partial_deck_inspection(text: str) -> bool:
    lowered = text.lower()
    if _full_deck_inspection(text):
        return False
    return (
        "look at the top" in lowered
        or "look at the bottom" in lowered
    ) and "deck" in lowered


def _partial_prize_inspection(text: str) -> bool:
    lowered = text.lower()
    if _exact_prize_inspection(text):
        return False
    if "prize" not in lowered:
        return False
    return any(
        phrase in lowered
        for phrase in (
            "look at 1 of your face-down prize",
            "turn 1 of your face-down prize",
            "look at the top card of your deck. you may switch that card with 1 of your face-down prize",
        )
    )


def _ability_timing_bucket(text: str) -> str:
    lowered = text.lower()
    if "once during your turn" in lowered or "as often as you like during your turn" in lowered:
        return "announced_during_turn"
    if "during your turn, you may search your deck" in lowered:
        return "announced_during_turn"
    if "when you play" in lowered and "from your hand" in lowered:
        return "play_from_hand_trigger"
    if "when " in lowered or "whenever " in lowered or lowered.startswith("if "):
        return "other_conditional_or_triggered"
    return "other"


def build_catalog(resources_root: Path) -> dict[str, Any]:
    """Return a deduplicated exact-information catalog and audit summaries."""
    legal_cards = _load_legal_cards(resources_root)

    variants: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    partial_variants: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}

    for card in legal_cards:
        for source, effect_name, raw_text in _effect_rows(card):
            text = _normalize(raw_text)
            if not text:
                continue

            action_class = _action_class(card, source)
            mechanisms: list[str] = []
            partial_mechanisms: list[str] = []

            if _full_deck_inspection(text):
                mechanisms.append("full_deck_inspection")
            if _exact_prize_inspection(text):
                mechanisms.append("exact_prize_inspection")
            if _partial_deck_inspection(text):
                partial_mechanisms.append("partial_deck_inspection")
            if _partial_prize_inspection(text):
                partial_mechanisms.append("partial_prize_inspection")

            for mechanism in mechanisms:
                key = (mechanism, action_class, card["name"], effect_name, text)
                row = variants.setdefault(
                    key,
                    {
                        "mechanism": mechanism,
                        "action_class": action_class,
                        "card_name": card["name"],
                        "effect_name": effect_name,
                        "text": text,
                        "print_ids": [],
                    },
                )
                row["print_ids"].append(card["id"])
                if source == "Ability":
                    row["ability_timing_bucket"] = _ability_timing_bucket(text)

            for mechanism in partial_mechanisms:
                key = (mechanism, action_class, card["name"], effect_name, text)
                row = partial_variants.setdefault(
                    key,
                    {
                        "mechanism": mechanism,
                        "action_class": action_class,
                        "card_name": card["name"],
                        "effect_name": effect_name,
                        "text": text,
                        "print_ids": [],
                    },
                )
                row["print_ids"].append(card["id"])

    exact_rows = sorted(
        variants.values(),
        key=lambda row: (
            row["mechanism"],
            row["action_class"],
            row["card_name"],
            row["effect_name"],
            row["text"],
        ),
    )
    partial_rows = sorted(
        partial_variants.values(),
        key=lambda row: (
            row["mechanism"],
            row["action_class"],
            row["card_name"],
            row["effect_name"],
            row["text"],
        ),
    )

    exact_counts = Counter((row["mechanism"], row["action_class"]) for row in exact_rows)
    partial_counts = Counter((row["mechanism"], row["action_class"]) for row in partial_rows)

    return {
        "legal_print_count": len(legal_cards),
        "exact_variant_count": len(exact_rows),
        "exact_counts": {
            f"{mechanism}|{action_class}": count
            for (mechanism, action_class), count in sorted(exact_counts.items())
        },
        "partial_variant_count": len(partial_rows),
        "partial_counts": {
            f"{mechanism}|{action_class}": count
            for (mechanism, action_class), count in sorted(partial_counts.items())
        },
        "exact_variants": exact_rows,
        "partial_variants": partial_rows,
    }
