"""Audited printed ways a 2026 Aichi deck can bypass Snorlax Block.

Opening access is only a proxy. Board constraints, locks, action costs,
timing, alternative card uses, and search are not evaluated here.
"""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

SOURCES = {
    "Shadow Rider": "shadow-rider-calyrex",
    "Vileplume control": "vileplume-control",
    "Raichu/Electrode": "raichu-electrode-aichi-2026",
    "Mew/Genesect": "mew-genesect",
    "Iron Thorns English": "iron_thorns_aichi_english",
    "Mega Absol/Garbodor": "mega-absol-garbodor",
    "Regidrago VSTAR": "regidrago-vstar",
}

# name: (English print, exact effect fragment, resource class).
ROLES = {
    "Guzma": ("sm3-115", "switch your Active Pokémon", "conditional_gust"),
    "Prime Catcher": ("sv5-157", "switch your Active Pokémon", "conditional_gust"),
    "Escape Rope": ("swsh5-125", "Each player switches", "switch"),
    "Jet Energy": ("sv2-190", "switch that Pokémon", "switch"),
    "Penny": ("sv1-183", "Put 1 of your Basic Pokémon", "pickup"),
    "Cassius": ("xy1-115", "Shuffle 1 of your Pokémon", "pickup"),
    "Acerola": ("sm3-112", "has any damage counters", "pickup"),
    "Scoop Up Cyclone": ("sv6-162", "Put 1 of your Pokémon", "pickup"),
    "Articuno-GX": ("sm7-31", "Legendary Ascent", "ability_switch"),
    "Klefki": ("sv1-96", "Mischievous Lock", "ability_suppress"),
    "Wobbuffet": ("xy4-36", "Bide Barricade", "ability_suppress"),
    "Garbodor": ("bw11-68", "Garbotoxin", "ability_suppress"),
}

NONBASIC_ESCAPE = frozenset({"conditional_gust", "switch", "pickup"})


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def legal_opening(basics: int) -> Fraction:
    return Fraction(choose(60, 7) - choose(60 - basics, 7), choose(60, 7))


def nominal_escape_given_valid(basics: int, escape_copies: int) -> Fraction:
    """Chance of >=1 marked non-Basic escape card in Basic-valid first seven."""
    num = (
        choose(60, 7)
        - choose(60 - basics, 7)
        - choose(60 - escape_copies, 7)
        + choose(60 - basics - escape_copies, 7)
    )
    return Fraction(num, choose(60, 7)) / legal_opening(basics)


def parse_english_60(folder: str) -> tuple[tuple[str, int], ...]:
    readme = ROOT / "results/decks" / folder / "README.md"
    cards = []
    for line in readme.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        if len(cells) >= 3 and cells[0].isdigit() and "-" in cells[2]:
            cards.append((cells[2], int(cells[0])))
    assert sum(quantity for _, quantity in cards) == 60, folder
    return tuple(cards)


def load_manifest_60() -> tuple[tuple[str, int], ...]:
    path = ROOT / "results/decks/snorlax-stall-4block-english/manifest.json"
    rows = json.loads(path.read_text(encoding="utf-8"))["cards"]
    assert sum(row["quantity"] for row in rows) == 60
    return tuple((row["print_id"], row["quantity"]) for row in rows)


def card_text(card_id: str) -> tuple[dict, str]:
    prefix = card_id.rsplit("-", 1)[0]
    path = ROOT / "resources/cards/en" / (prefix + ".json")
    card = next(
        row for row in json.loads(path.read_text(encoding="utf-8"))
        if row["id"] == card_id
    )
    rules = card.get("rules") or []
    abilities = [row["name"] + " " + row["text"] for row in card.get("abilities") or []]
    attacks = [row["name"] + " " + row.get("text", "") for row in card.get("attacks") or []]
    return card, " ".join(rules + abilities + attacks)


def verify_printed_roles() -> None:
    for name, (card_id, snippet, _role) in ROLES.items():
        card, text = card_text(card_id)
        assert card["name"] == name, (card_id, name)
        assert snippet.casefold() in text.casefold(), (card_id, snippet)
    _, block = card_text("bw8-101")
    assert "your opponent's Active Pokémon can't retreat" in block
    _, float_stone = card_text("xy8-137")
    assert "has no Retreat Cost" in float_stone


def audit_one(rows: tuple[tuple[str, int], ...], records) -> dict:
    counts = Counter(dict(rows))
    basics = sum(
        qty for card_id, qty in rows if records[card_id].is_basic_pokemon
    )
    present = {
        name: counts[card_id]
        for name, (card_id, _snippet, _role) in ROLES.items()
        if counts[card_id] > 0
    }
    nominal = sum(
        copies for name, copies in present.items()
        if ROLES[name][2] in NONBASIC_ESCAPE
    )
    assert 1 <= basics <= 20 and nominal <= 60 - basics
    return {
        "basic": basics,
        "nominal": nominal,
        "probability": nominal_escape_given_valid(basics, nominal),
        "present": present,
    }
