"""Full source-text coverage audit for typed self/team free-Retreat Abilities."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from retreat_typed_energy_no_cost import SOURCES

SYMBOL = {
    "Grass": "G", "Fire": "R", "Water": "W",
    "Lightning": "L", "Psychic": "P",
    "Fighting": "F", "Darkness": "D", "Metal": "M",
}
PATTERN = re.compile(
    r"(Grass|Fire|Water|Lightning|Psychic|Fighting|Darkness|Metal) Energy attached",
    re.IGNORECASE,
)


def main() -> None:
    compiled = {s.print_id: s for s in SOURCES}
    assert len(compiled) == len(SOURCES) == 27
    observed = {}
    print_count = 0
    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json")):
        cards = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(cards, dict):
            cards = cards.get("data", [])
        for card in cards:
            if card.get("legalities", {}).get("expanded") != "Legal":
                continue
            print_count += 1
            for ability in card.get("abilities") or ():
                text = ability.get("text", "")
                match = PATTERN.search(text)
                if match is None or "no Retreat Cost" not in text:
                    continue
                scope = "self" if text.startswith("If this Pokémon") else "team"
                expected = (
                    card["name"], ability["name"],
                    SYMBOL[match.group(1).title()], scope,
                )
                assert card["id"] not in observed, card["id"]
                observed[card["id"]] = expected

    assert set(observed) == set(compiled), (
        sorted(set(observed) - set(compiled)),
        sorted(set(compiled) - set(observed)),
    )
    for print_id, item in compiled.items():
        assert observed[print_id] == (
            item.card_name, item.ability_name,
            item.energy_type, item.scope,
        ), (print_id, observed[print_id])
    assert sum(s.scope == "self" for s in SOURCES) == 14
    assert sum(s.scope == "team" for s in SOURCES) == 13
    print("Typed Energy self/team free-Retreat source audit: PASS")
    print({"expanded_labeled_prints": print_count,
           "source_prints": len(SOURCES),
           "self": 14, "team": 13})


if __name__ == "__main__":
    main()
