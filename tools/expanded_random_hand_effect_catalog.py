"""Conservative Expanded English random opponent-hand destination catalog."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from collections import Counter

from build_expanded_legality_baseline import classify_effective_legality

RANDOM_CARD = re.compile(
    r"random (?:card|cards)|(?:card|cards) at random",
    re.IGNORECASE,
)
OPPONENT_HAND = re.compile(
    r"opponent(?:'s)? hand",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class RandomHandEffectRow:
    card_id: str
    card_name: str
    source: str
    destination_family: str
    text: str


def classify_random_hand_text(text: str) -> str | None:
    """Identify random opponent-hand operations by destination semantics."""

    if not RANDOM_CARD.search(text) or not OPPONENT_HAND.search(text):
        return None

    lower = text.lower()
    if "lost zone" in lower:
        return "lost_zone"
    if "bottom of their deck" in lower or "bottom of your opponent's deck" in lower:
        return "deck_bottom"
    if "switch those cards" in lower and "prize" in lower:
        return "prize_swap"
    if "discard" in lower:
        return "discard"
    if "shuffle" in lower and "deck" in lower:
        return "shuffle_deck"
    return "unclassified"


def _effect_texts(card: dict):
    for index, text in enumerate(card.get("rules") or []):
        yield f"rule:{index}", text
    for attack in card.get("attacks") or []:
        text = attack.get("text") or ""
        if text:
            yield f"attack:{attack.get('name', '')}", text
    for ability in card.get("abilities") or []:
        text = ability.get("text") or ""
        if text:
            yield f"ability:{ability.get('name', '')}", text


def build_random_hand_effect_catalog(resources: Path) -> tuple[RandomHandEffectRow, ...]:
    sets = json.loads((resources / "sets" / "en.json").read_text(encoding="utf-8"))
    expanded = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    found = []
    for path in sorted((resources / "cards" / "en").glob("*.json")):
        if path.stem not in expanded:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            status, _reason = classify_effective_legality(card)
            if status != "Legal":
                continue
            for source, text in _effect_texts(card):
                family = classify_random_hand_text(text)
                if family is not None:
                    found.append(
                        RandomHandEffectRow(
                            card["id"], card["name"], source, family, text,
                        )
                    )
    return tuple(sorted(found, key=lambda x: (x.card_id, x.source)))


def count_effect_families(
    rows: tuple[RandomHandEffectRow, ...],
) -> dict[str, dict[str, int]]:
    grouped = {}
    for family in sorted({row.destination_family for row in rows}):
        selected = [row for row in rows if row.destination_family == family]
        grouped[family] = {
            "print_effect_rows": len(selected),
            "unique_card_names": len({row.card_name for row in selected}),
        }
    return grouped


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    rows = build_random_hand_effect_catalog(repo_root / "resources")
    print(json.dumps({
        "total_effect_rows": len(rows),
        "unique_card_names": len({row.card_name for row in rows}),
        "destination_families": count_effect_families(rows),
    }, indent=2))
