"""Catalog post-damage reaction text that explicitly survives Knock Out."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re

from build_expanded_legality_baseline import classify_effective_legality


_FIXED = re.compile(
    r"(?:put|place) (\d+) damage counters? on the Attacking Pokémon",
    re.IGNORECASE,
)
_MIRROR = re.compile(
    r"damage counters on the Attacking Pokémon equal to the damage done",
    re.IGNORECASE,
)


def classify_reaction_text(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    lower = normalized.casefold()

    if _MIRROR.search(normalized):
        return "mirror_damage_counters"
    if _FIXED.search(normalized) and "for each" not in lower:
        return "fixed_damage_counters"
    if _FIXED.search(normalized) and "for each" in lower:
        return "scaled_damage_counters"
    if "attacking pokémon is now " in lower:
        return "special_condition"
    if "discard an energy from the attacking pokémon" in lower:
        return "discard_attacker_energy"
    if "put an energy attached to the attacking pokémon" in lower:
        return "return_attacker_energy"
    if "move an energy from the attacking pokémon" in lower:
        return "move_attacker_energy"
    if "draw " in lower:
        return "draw"
    if "search your deck" in lower:
        return "search"
    if "opponent discards a card from their hand" in lower:
        return "discard_opponent_hand"
    return "other"


def build_damage_reaction_catalog(resources_root: Path) -> dict[str, object]:
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

            sources = []
            for ability in card.get("abilities") or ():
                sources.append(("ability", ability.get("name"), ability.get("text") or ""))
            for attack in card.get("attacks") or ():
                sources.append(("attack", attack.get("name"), attack.get("text") or ""))
            for rule in card.get("rules") or ():
                sources.append(("rule", None, rule))

            for source_kind, source_name, text in sources:
                lower = text.casefold()
                if "is damaged by an attack" not in lower:
                    continue
                if "knocked out" not in lower or "even if" not in lower:
                    continue
                rows.append(
                    {
                        "card_id": card["id"],
                        "card_name": card["name"],
                        "source_kind": source_kind,
                        "source_name": source_name,
                        "category": classify_reaction_text(text),
                        "text": re.sub(r"\s+", " ", text).strip(),
                    }
                )

    categories = Counter(row["category"] for row in rows)
    signatures = {
        (row["category"], row["text"])
        for row in rows
    }
    signature_categories = Counter(category for category, _ in signatures)

    return {
        "print_rows": len(rows),
        "unique_text_signatures": len(signatures),
        "rows_by_category": dict(sorted(categories.items())),
        "signatures_by_category": dict(sorted(signature_categories.items())),
        "unclassified": [
            row for row in rows if row["category"] == "other"
        ],
    }
