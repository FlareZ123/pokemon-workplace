"""Independently audit exact-print conditional no-Retreat-Cost Abilities."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from retreat_conditional_self_free_cost import SOURCES


def source_type(text: str) -> str | None:
    lower = text.lower()
    if "no retreat cost" not in lower:
        return None
    if "if this pokémon has any energy attached" in lower:
        return "any_energy"
    if "if this pokémon has any damage counters on it" in lower:
        return "damaged"
    if re.search(
        r"if (there is any stadium card|you have a stadium card|a stadium is|a stadium card is)",
        lower,
    ):
        return "stadium"
    if "if your opponent has any pokémon v in play" in lower:
        return "opponent_v"
    if "if your opponent has any pokémon-gx or pokémon-ex in play" in lower:
        return "opponent_gx_ex"
    return None


def main() -> None:
    compiled = {source.print_id: source for source in SOURCES}
    assert len(compiled) == len(SOURCES) == 21
    discovered = {}
    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json")):
        cards = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(cards, dict):
            cards = cards.get("data", [])
        for card in cards:
            # This is a source-coverage filter, not a live tournament-ban oracle.
            if card.get("legalities", {}).get("expanded") != "Legal":
                continue
            for ability in card.get("abilities") or ():
                trigger = source_type(ability.get("text", ""))
                if trigger is None:
                    continue
                assert card["id"] not in discovered
                discovered[card["id"]] = (
                    card["name"], ability["name"], trigger,
                )

    assert set(discovered) == set(compiled), (
        sorted(set(discovered) - set(compiled)),
        sorted(set(compiled) - set(discovered)),
    )
    for print_id, source in compiled.items():
        assert discovered[print_id] == (
            source.card_name, source.ability_name, source.trigger,
        )
    assert len({(x.card_name, x.ability_name) for x in SOURCES}) == 13
    print("Conditional self free-retreat print-source audit: PASS")
    print({"exact_prints": 21, "ability_families": 13})


if __name__ == "__main__":
    main()
