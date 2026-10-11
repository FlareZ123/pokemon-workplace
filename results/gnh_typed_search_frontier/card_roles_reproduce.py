"""SFT: verify typed Aichi G&H search categories from the bundled card pool."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from tools.aichi_post_gnh_prize_reset import DECK_COUNTS
from tools.gnh_typed_search_frontier import STADIUMS, TOOLS, SPECIAL_ENERGY


def main() -> None:
    root = Path(__file__).resolve().parents[2] / "resources" / "cards" / "en"
    categories = {
        "Stadium": STADIUMS,
        "Pokémon Tool": TOOLS,
        "Special": SPECIAL_ENERGY,
        "Supporter": frozenset({"Guzma & Hala"}),
        "Item": frozenset({"Tag Call"}),
    }
    expected = set().union(*categories.values())
    printings: dict[str, list[dict]] = defaultdict(list)
    for filename in root.glob("*.json"):
        for card in json.loads(filename.read_text(encoding="utf-8")):
            if card["name"] in expected:
                printings[card["name"]].append(card)
    assert set(printings) == expected, set(expected)-set(printings)
    for category, names in categories.items():
        for name in sorted(names):
            assert name in DECK_COUNTS and DECK_COUNTS[name] > 0, name
            cards = printings[name]
            supertype = "Energy" if category == "Special" else "Trainer"
            assert all(c["supertype"] == supertype
                       and category in c["subtypes"] for c in cards), name
            print(name, len(cards), category, cards[0]["id"])

    assert all("TAG TEAM" in c["subtypes"]
               and any("discard 2 other cards" in text
                       for text in c.get("rules",()))
               for c in printings["Guzma & Hala"])
    assert all(any("up to 2 TAG TEAM" in text
                   for text in c.get("rules",()))
               for c in printings["Tag Call"])
    print("PASS: every typed search name appears in actual Aichi counts")
    print("PASS: exact card pool confirms Stadium, Tool, Special Energy, G&H and Tag Call roles")


if __name__ == "__main__":
    main()
