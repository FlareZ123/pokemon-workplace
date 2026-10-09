"""Conservative inventory of Expanded-legal printed turn-ending effects.

Classify exact direct 'your/their turn ends' effect text by execution
channel. The catalogue is a reproducible audit of the bundled English
snapshot, not a semantic classifier of every imaginable wording or rule.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from collections import Counter
import json
import re

from build_expanded_legality_baseline import classify_effective_legality


_ENDING = re.compile(r"\b(?:your|their|his or her) turn ends\b", re.IGNORECASE)
_UNLABELED_MEGA = (
    "When 1 of your Pokémon becomes a Mega Evolution Pokémon, your turn ends."
)


@dataclass(frozen=True)
class TurnEndPrintSource:
    print_id: str
    name: str
    channel: str
    action_name: str
    text: str


def _classify(card: dict, group: str, text: str) -> str:
    if group == "abilities":
        if card["supertype"] != "Pokémon":
            raise ValueError("Ability source does not belong to Pokémon")
        return "ability_use"
    if group == "attacks":
        if card["supertype"] != "Pokémon":
            raise ValueError("Attack source does not belong to Pokémon")
        return "opponent_turn_attachment_reaction"

    if (
        group == "rules"
        and card["supertype"] == "Pokémon"
        and (
            text.startswith("Mega Evolution rule: When")
            or text.startswith("Primal Reversion rule: When")
            or text == _UNLABELED_MEGA
        )
    ):
        return "legacy_evolution"
    if group != "rules" or card["supertype"] != "Trainer":
        raise ValueError(f"unclassified turn end: {card['id']} / {group}")

    subtypes = set(card.get("subtypes") or ())
    for subtype, channel in (
        ("Item", "item_effect"),
        ("Supporter", "supporter_effect"),
        ("Stadium", "stadium_activation"),
    ):
        if subtype in subtypes:
            return channel
    raise ValueError(f"unsupported turn-ending Trainer kind: {card['id']}")


def audit_turn_end_sources(resources: Path) -> tuple[TurnEndPrintSource, ...]:
    sets = json.loads(
        (resources / "sets" / "en.json").read_text(encoding="utf-8")
    )
    legal_sets = {
        row["id"] for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }
    sources = []
    for path in sorted((resources / "cards" / "en").glob("*.json")):
        if path.stem not in legal_sets:
            continue
        cards = json.loads(path.read_text(encoding="utf-8"))
        for card in cards:
            if classify_effective_legality(card)[0] != "Legal":
                continue
            for group in ("rules", "abilities", "attacks"):
                for entry in card.get(group) or ():
                    text = entry if isinstance(entry, str) else entry.get("text", "")
                    if not _ENDING.search(text):
                        continue
                    if text.startswith("When your turn ends, discard this card"):
                        continue
                    sources.append(TurnEndPrintSource(
                        print_id=card["id"],
                        name=card["name"],
                        channel=_classify(card, group, text),
                        action_name=(
                            entry.get("name", "")
                            if isinstance(entry, dict) else card["name"]
                        ),
                        text=text,
                    ))
    return tuple(sorted(sources, key=lambda x: (x.channel, x.print_id)))


def channel_counts(sources: tuple[TurnEndPrintSource, ...]) -> dict[str, int]:
    return dict(sorted(Counter(row.channel for row in sources).items()))
