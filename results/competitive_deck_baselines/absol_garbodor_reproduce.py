"""Reproduce 2026 CL Aichi Open League eighth-place Mega Absol / Garbodor baseline.

Card-name source: https://limitlesstcg.com/tournaments/566/decklists
Exact English prints are a representative playable realization.
"""
from __future__ import annotations

from collections import Counter
from datetime import date
import json
from pathlib import Path

from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
MANIFEST = BASE / "absol_garbodor_kobayashi_2026.json"

# Independently transcribed source counts for every one of the published names.
# The 2026 site abbreviates "Battle Compressor Team Flare Gear".
PUBLISHED = {
    "Mega Absol ex": 2, "Trubbish": 2, "Garbodor": 2,
    "Tapu Koko ◇": 1, "Dedenne-GX": 1, "Crobat V": 1,
    "Squawkabilly ex": 1, "Tapu Lele-GX": 1, "Budew": 1,
    "Lillie's Determination": 1, "Carmine": 1, "Iono": 1,
    "Roxanne": 1, "Guzma": 1, "Crispin": 1, "Wally": 1,
    "Karen": 1, "Quick Ball": 4, "Dark Patch": 4,
    "VS Seeker": 3, "Battle Compressor Team Flare Gear": 2,
    "Ultra Ball": 2, "Battle VIP Pass": 2, "Boost Shake": 1,
    "Secret Box": 1, "Night Stretcher": 1, "Super Rod": 1,
    "Pokémon Communication": 1, "Hisuian Heavy Ball": 1,
    "Field Blower": 1, "Adventure Bag": 1, "Float Stone": 4,
    "Muscle Band": 1, "Forest Seal Stone": 1,
    "Temple of Sinnoh": 2, "Darkness Energy": 5,
    "Lightning Energy": 2,
}

CORE = {
    "me1-86": ("attacks", "Terminal Period"),
    "bw11-68": ("abilities", "Garbotoxin"),
    "sm9-51": ("abilities", "Dance of the Ancients"),
    "sm10-57": ("abilities", "Dedechange"),
    "swsh3-104": ("abilities", "Dark Asset"),
    "sv2-169": ("abilities", "Squawk and Seize"),
    "sm2-60": ("abilities", "Wonder Tag"),
    "sv8pt5-4": ("attacks", "Itchy Pollen"),
    "swsh12-156": ("abilities", "Star Alchemy"),
}


def verify() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source = data["source"]
    assert (
        source["event"], source["date"], source["place"], source["player"]
    ) == ("CL Aichi Open League", "2026-05-10", 8, "Yusuke Kobayashi")
    assert source["url"] == "https://limitlesstcg.com/tournaments/566/decklists"

    cards = data["cards"]
    assert len(cards) == 37
    assert len({card["name"] for card in cards}) == len(cards)
    assert len({card["print_id"] for card in cards}) == len(cards)
    assert all(
        type(card["quantity"]) is int and card["quantity"] > 0
        for card in cards
    )
    quantities = Counter({row["name"]: row["quantity"] for row in cards})
    assert quantities == PUBLISHED, quantities - PUBLISHED
    categories: Counter[str] = Counter()
    for row in cards:
        categories[row["category"]] += row["quantity"]
    assert categories == {"Pokémon": 12, "Trainer": 41, "Energy": 7}
    assert sum(categories.values()) == 60

    resources = ROOT / "resources"
    records = load_all_card_records(resources)
    basics = 0
    for row in cards:
        card = records[row["print_id"]]
        assert (card.name, card.supertype) == (row["name"], row["category"])
        assert card.effective_status == "Legal"
        if card.is_basic_pokemon:
            basics += row["quantity"]
    assert basics == 10
    assert quantities["Secret Box"] == 1
    assert quantities["Tapu Koko ◇"] == 1

    adjudication = adjudicate_deck(
        [DeckEntry(row["print_id"], row["quantity"]) for row in cards],
        resources,
        as_of=date(2026, 10, 12),
    )
    assert adjudication.construction.valid, adjudication.construction.issues
    assert adjudication.disposition == "eligible_snapshot", [
        (p.card_id, p.eligibility, p.reason)
        for p in adjudication.print_proofs if p.eligibility != "eligible"
    ]
    assert len(adjudication.print_proofs) == len(cards)
    assert all(p.eligibility == "eligible" for p in adjudication.print_proofs)

    # The tournament text's specific Garbotoxin / Terminal Period roles
    # cannot be replaced by any same-name print without rechecking.
    for card_id, (category, effect_name) in CORE.items():
        set_id = card_id.rsplit("-", 1)[0]
        raw_cards = json.loads(
            (resources / "cards" / "en" / f"{set_id}.json").read_text(
                encoding="utf-8"
            )
        )
        card = next(row for row in raw_cards if row["id"] == card_id)
        assert any(
            e["name"] == effect_name for e in (card.get(category) or ())
        ), (card_id, effect_name)
        if effect_name == "Terminal Period":
            move = next(
                a for a in card["attacks"] if a["name"] == effect_name
            )
            assert "exactly 6 damage counters" in move["text"]

    print("PASS: Aichi eighth place, 60 cards (12 / 41 / 7)")
    print("PASS: all 37 published name quantities")
    print("PASS: selected exact English print identities and 10 Basics")
    print("PASS: one ACE SPEC, one Prism Star, 9 critical attack/Ability roles")
    print("PASS: conservative paper Expanded snapshot construction and eligibility")
    print("LIMIT: tournament finish is evidence; matchups and win rate untested")


if __name__ == "__main__":
    verify()
