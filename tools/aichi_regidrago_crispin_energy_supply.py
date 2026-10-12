"""Exact Crispin two-type deck-supply ceiling after Aichi Regidrago's Trifrost.

The 2026 Aichi tenth-place list has four Basic Grass and two Basic Fire.
One Double Dragon plus either Basic pays Apex Dragon. Copied Kyurem's
Trifrost discards all the actor's attached Energy. Conditionally fix the
DDE and one Basic of the stated type outside the unknown pool; then
randomly allocate Prizes and other non-deck cards from the remaining 58.
This models only presence of both Basic types in the deck, not Supporter
access, player choice, actual known hand, deck searches, or game outcomes.
"""
from __future__ import annotations

import json
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any


def both_types_in_deck(population: int, grass: int, fire: int, outside_deck: int) -> Fraction:
    """Exact chance that deck retains >=1 Grass and >=1 Fire after sampling.

    Among population physically distinct, initially unlocated cards, choose
    outside_deck cards uniformly without replacement. The other cards form
    the accessible deck. Basic Energy names are mutually exclusive categories.
    """
    if min(population, grass, fire, outside_deck) < 0 or grass + fire > population or outside_deck > population:
        raise ValueError("Invalid physical card partition")
    denom = comb(population, outside_deck)

    def all_outside(count: int) -> Fraction:
        if outside_deck < count:
            return Fraction(0)
        return Fraction(comb(population - count, outside_deck - count), denom)

    return 1 - all_outside(grass) - all_outside(fire) + all_outside(grass + fire)


def _load_card(resources_root: Path, card_id: str) -> dict[str, Any]:
    set_id = card_id.split("-")[0]
    cards = json.loads((resources_root / "cards" / "en" / f"{set_id}.json").read_text(encoding="utf-8"))
    return next(c for c in cards if c["id"] == card_id)


def build(repository_root: Path) -> dict[str, Any]:
    manifest = json.loads((repository_root / "results/regidrago_aichi_top10_playable/yoshioka_regidrago_2026.json").read_text(encoding="utf-8"))
    energy = {c["name"]: c["count"] for c in manifest["groups"]["Energy"]}
    assert energy == {"Double Dragon Energy": 4, "Grass Energy": 4, "Fire Energy": 2}
    assert any(c["name"] == "Kyurem" and c["print_id"] == "sv6pt5-47"
               for c in manifest["groups"]["Pokémon"])
    assert any(c["name"] == "Crispin" and c["count"] == 1
               for c in manifest["groups"]["Trainer"])

    resources = repository_root / "resources"
    regidrago = _load_card(resources, "swsh12-136")
    kyurem = _load_card(resources, "sv6pt5-47")
    crispin = _load_card(resources, "sv7-133")
    dde = _load_card(resources, "xy6-97")
    assert regidrago["types"] == ["Dragon"]
    assert any(a["name"] == "Apex Dragon" and a["cost"] == ["Grass", "Grass", "Fire"]
               for a in regidrago["attacks"])
    assert any(a["name"] == "Trifrost" and a["text"].startswith("Discard all Energy from this Pokémon.")
               for a in kyurem["attacks"])
    assert "2 Basic Energy cards of different types" in " ".join(crispin["rules"])
    assert "provides only 2 Energy at a time" in " ".join(dde["rules"])
    # One attached DDE + one Grass or Fire satisfies Apex's 3-unit cost.
    # The copied Trifrost then physically discards these two cards.
    unknown = sum(c["count"] for group in manifest["groups"].values() for c in group) - 2
    assert unknown == 58

    rows = []
    for additional_outside in (0, 3, 7, 10, 15):
        m = 6 + additional_outside
        grass_payment = both_types_in_deck(unknown, 3, 2, m)
        fire_payment = both_types_in_deck(unknown, 4, 1, m)
        rows.append({"additional_non_deck_cards": additional_outside,
                     "total_unknown_cards_outside_deck": m,
                     "attach_grass_before_trifrost": str(grass_payment),
                     "attach_fire_before_trifrost": str(fire_payment),
                     "grass_placement_advantage": str(grass_payment - fire_payment),
                     "grass_placement_advantage_pp": float((grass_payment - fire_payment) * 100)})

    exact_13 = rows[2]
    assert exact_13["attach_grass_before_trifrost"] == "10921/11571"
    assert exact_13["attach_fire_before_trifrost"] == "35845/46284"
    assert rows[0]["attach_grass_before_trifrost"] == "13039/13167"
    assert rows[0]["attach_fire_before_trifrost"] == "342329/381843"
    all_m = [both_types_in_deck(unknown, 3, 2, m) - both_types_in_deck(unknown, 4, 1, m)
             for m in range(unknown + 1)]
    assert all(x >= 0 for x in all_m)
    assert [m for m, x in enumerate(all_m) if x == 0] == [0, 57, 58]
    return {
        "source": manifest["source"],
        "source_prints": ["swsh12-136", "sv6pt5-47", "sv7-133", "xy6-97"],
        "fixed_known_outside": "one attached DDE and one attached Grass or Fire to be discarded",
        "unknown_population": unknown,
        "prizes": 6,
        "rows": rows,
        "grass_placement_weak_dominance_m": unknown + 1,
        "strict_advantage_m_count": sum(x > 0 for x in all_m),
        "tie_m_values": [m for m, x in enumerate(all_m) if x == 0],
        "claim_scope": "Crispin two-Basic-type presence in the remaining deck only",
    }


if __name__ == "__main__":
    print(json.dumps(build(Path(".")), indent=2))
