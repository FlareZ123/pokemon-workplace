"""Auditable catalog of paper Expanded full-hand deck-return/redraw effects.

Complements catalog_full_hand_resets.py, which covers discard-all draw effects.
A match is a syntactic candidate, not a full legality or timing interpreter.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re

from build_expanded_legality_baseline import classify_effective_legality


# Restrict to explicit full-hand returns. Deliberately exclude partial-hand cards
# (Caitlin, Maintenance, Kofu) and opponent-only effects (Reset Stamp).
_PATTERNS = (
    ("shuffle_into_deck", "self", re.compile(r"\bshuffle your hand into your deck\b", re.I)),
    ("shuffle_into_deck", "both", re.compile(r"\b(?:each player|both players) shuffles? (?:their|his or her) hand into (?:their|his or her) deck\b", re.I)),
    ("shuffle_into_deck", "chosen", re.compile(r"\bthat player (?:may )?shuffles? (?:their|his or her) hand into (?:their|his or her) deck\b", re.I)),
    ("bottom_deck", "self", re.compile(r"\bshuffle your hand and put it on the bottom of your deck\b", re.I)),
    ("bottom_deck", "both", re.compile(r"\b(?:each player|both players) shuffles? (?:their|his or her) hand and puts? it on the bottom of (?:their|his or her) deck\b", re.I)),
    ("bottom_deck", "chosen", re.compile(r"\b(?:that player|either player) shuffles? (?:their|his or her) hand and puts? it on the bottom of (?:their|his or her) deck\b", re.I)),
)


@dataclass(frozen=True)
class HandReplacementFamily:
    name: str
    source_kind: str
    effect_name: str
    hand_destination: str
    target_scope: str
    ends_turn: bool
    print_ids: tuple[str, ...]
    example_text: str


def _entries(card: dict):
    subtypes = set(card.get("subtypes") or [])
    if "Supporter" in subtypes:
        trainer_kind = "supporter"
    elif "Stadium" in subtypes:
        trainer_kind = "stadium"
    elif "Item" in subtypes:
        trainer_kind = "item"
    else:
        trainer_kind = "trainer"
    for rule in card.get("rules") or []:
        yield trainer_kind, "", rule
    for ability in card.get("abilities") or []:
        yield "ability", ability.get("name") or "", ability.get("text") or ""
    for attack in card.get("attacks") or []:
        yield "attack", attack.get("name") or "", attack.get("text") or ""


def catalog_full_hand_replacements(resources_root: Path = Path("resources")) -> tuple[HandReplacementFamily, ...]:
    sets = json.loads((resources_root / "sets" / "en.json").read_text(encoding="utf-8"))
    expanded_sets = {entry["id"] for entry in sets if (entry.get("legalities") or {}).get("expanded") == "Legal"}
    grouped: dict[tuple, set[str]] = {}
    examples: dict[tuple, str] = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            if classify_effective_legality(card)[0] != "Legal":
                continue
            for kind, effect, text in _entries(card):
                if not re.search(r"\bdraws?\b", text, re.I):
                    continue
                matches = [(dest, scope) for dest, scope, rx in _PATTERNS if rx.search(text)]
                if not matches:
                    continue
                destinations = {dest for dest, _ in matches}
                if len(destinations) != 1:
                    raise ValueError(f"ambiguous replacement for {card['id']}: {matches}")
                dest = next(iter(destinations))
                normalized = " ".join(text.split())
                scope = "both" if any(s == "both" for _, s in matches) else "chosen" if any(s == "chosen" for _, s in matches) else "self"
                if scope == "chosen" and "once during each player's turn" in normalized.lower():
                    scope = "turn_player"
                # Keep condition/draw variants distinct rather than asserting
                # gameplay equivalence from the same card name.
                key = (card["name"], kind, effect, dest, scope, kind == "attack" or "your turn ends" in normalized.lower(), normalized)
                grouped.setdefault(key, set()).add(card["id"])
                examples[key] = normalized
    return tuple(sorted((
        HandReplacementFamily(
            name=k[0], source_kind=k[1], effect_name=k[2], hand_destination=k[3],
            target_scope=k[4], ends_turn=k[5], print_ids=tuple(sorted(ids)), example_text=examples[k],
        ) for k, ids in grouped.items()
    ), key=lambda x: (x.hand_destination, x.name, x.source_kind, x.effect_name, x.example_text)))


def main() -> None:
    families = catalog_full_hand_replacements()
    print(json.dumps({"effect_variants": len(families), "prints": sum(len(x.print_ids) for x in families),
                      "families": [asdict(x) for x in families]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
