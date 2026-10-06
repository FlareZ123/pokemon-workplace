"""Catalog representative Expanded routes that can access a Supporter.

This is a reproducible card-text census plus a curated timing classification.
It intentionally separates effects that can put a Supporter into hand before the
current Supporter play from effects that consume an attack or Supporter window.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from collections import defaultdict


ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "resources" / "cards" / "en"


def load_cards() -> list[dict]:
    cards: list[dict] = []
    for path in sorted(CARDS.glob("*.json")):
        cards.extend(json.loads(path.read_text(encoding="utf-8")))
    return cards


def effect_sources(card: dict) -> list[tuple[str, str, str]]:
    sources: list[tuple[str, str, str]] = []
    for ability in card.get("abilities") or []:
        sources.append(("Ability", ability.get("name", ""), ability.get("text", "")))
    for attack in card.get("attacks") or []:
        sources.append(("Attack", attack.get("name", ""), attack.get("text", "")))
    for rule in card.get("rules") or []:
        sources.append(("Rule", "", rule))
    return sources


def direct_supporter_search_source(card: dict) -> tuple[str, str, str] | None:
    for source in effect_sources(card):
        _, _, text = source
        lowered = text.lower()
        if (
            "search your deck for" in lowered
            and "supporter card" in lowered
            and ("put it into your hand" in lowered or "put them into your hand" in lowered)
        ):
            return source
    return None


def expanded_legal(card: dict) -> bool:
    return card.get("legalities", {}).get("expanded") == "Legal"


def main() -> None:
    cards = [card for card in load_cards() if expanded_legal(card)]

    names_by_source: dict[tuple[str, str], set[str]] = defaultdict(set)
    direct_rows: list[tuple[str, str, str, str, str]] = []

    for card in cards:
        source = direct_supporter_search_source(card)
        if source is None:
            continue
        source_kind, effect_name, text = source
        subtype = "/".join(card.get("subtypes") or [])
        names_by_source[(source_kind, subtype)].add(card["name"])
        direct_rows.append((card["name"], card["id"], source_kind, effect_name, text))

    print("Expanded-legal card names with direct deck -> Supporter-in-hand wording")
    for (source_kind, subtype), names in sorted(names_by_source.items()):
        print(f"{source_kind:7} {subtype:24} {len(names):2d}: {', '.join(sorted(names))}")

    representative_ids = [
        "sv8-165",   # Call Bell
        "sv6-163",   # Secret Box
        "bw7-137",   # Computer Search
        "bw3-96",    # Xtransceiver
        "bw10-60",   # Jirachi-EX
        "sm2-60",    # Tapu Lele-GX
        "swsh9-40",  # Lumineon V
        "me3-62",    # Meowth ex
        "swsh10-62", # Gallade
        "sm9-119",   # Dragonite
        "sm12-69",   # Magneton
        "swsh12-82", # Meowstic
        "sv2-159",   # Pelipper
        "me5-70",    # Silvally
        "xy4-92",    # Battle Compressor
        "xy4-109",   # VS Seeker
        "sv1-186",   # Pokegear 3.0
        "bw5-99",    # Random Receiver
        "xy7-100",   # Trainers' Mail
        "sm11-202",  # Misty's Favor
        "xy7-95",    # Steven
        "sv1-181",   # Nest Ball
        "swsh8-237", # Quick Ball
        "sv1-196",   # Ultra Ball
    ]
    by_id = {card["id"]: card for card in cards}
    missing = [card_id for card_id in representative_ids if card_id not in by_id]
    if missing:
        raise AssertionError(f"Expected Expanded-legal representative cards missing: {missing}")

    print("\nRepresentative card text")
    for card_id in representative_ids:
        card = by_id[card_id]
        print(f"\n{card_id} | {card['name']} | {'/'.join(card.get('subtypes') or [])}")
        for kind, name, text in effect_sources(card):
            if text:
                label = f"{kind} {name}".strip()
                print(f"{label}: {text}")

    # Semantic regression checks for the timing distinctions documented in the result.
    assert "put it onto your Bench" in " ".join(by_id["sv1-181"].get("rules") or [])
    assert "put it into your hand" in " ".join(by_id["swsh8-237"].get("rules") or [])
    assert "from your hand onto your Bench" in by_id["sm2-60"]["abilities"][0]["text"]
    assert "from your discard pile into your hand" in " ".join(by_id["xy4-109"].get("rules") or [])
    assert "discard them" in " ".join(by_id["xy4-92"].get("rules") or [])


if __name__ == "__main__":
    main()
