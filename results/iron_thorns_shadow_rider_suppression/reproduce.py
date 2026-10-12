"""Paper Expanded Ability interaction: Iron Thorns ex vs Aichi Shadow Rider.

Source-text regression verifies that Active Iron Thorns ex Initialization
disables non-Future Rule Box Abilities, including Radiant Eternatus's
Climactic Gate and Shadow Rider VMAX's Underworld Door. Contrasts the
non-Rule-Box Vileplume Item lock from the second-place list.

This is an *active unnegated lock* conditional result, not an actual game
win-rate or probability that a given opponent has established that lock.
"""
from __future__ import annotations

import json
from pathlib import Path

from results.competitive_deck_baselines.shadow_rider_reproduce import POKEMON
from results.shadow_rider_radiant_launch.reproduce import exact


IRON_THORNS = "sv6-77"
RADIANT = "swsh12pt5-105"
SHADOW_VMAX = "swsh6-75"
TAPU_LELE = "sm2-60"
VILEPLUME = "xy7-3"
PIDGEOT_EX = "sv3-164"
FAN_ROTOM = "sv7-118"
JIRACHI = "sm9-99"


def read_print(card_id: str) -> dict:
    resources = Path(__file__).resolve().parents[2] / "resources"
    set_id = card_id.rsplit("-", 1)[0]
    cards = json.loads(
        (resources / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(c for c in cards if c["id"] == card_id)


def ability_names(card: dict) -> set[str]:
    return {ability["name"] for ability in card.get("abilities") or []}


def has_rule_box(card: dict) -> bool:
    return any(" Rule:" in rule or " rule:" in rule for rule in card["rules"])


def thorns_suppresses(target: dict, thorns_active: bool = True) -> bool:
    """Effect of a validated unnegated active Initialization source."""
    return (
        thorns_active
        and has_rule_box(target)
        and "Future" not in target["subtypes"]
    )


def main() -> None:
    cards = {
        card_id: read_print(card_id)
        for card_id in (
            IRON_THORNS, RADIANT, SHADOW_VMAX, TAPU_LELE,
            VILEPLUME, PIDGEOT_EX, FAN_ROTOM, JIRACHI
        )
    }
    thorns = cards[IRON_THORNS]
    assert thorns["name"] == "Iron Thorns ex"
    assert "Basic" in thorns["subtypes"]
    assert "Future" in thorns["subtypes"]
    assert "Initialization" in ability_names(thorns)
    text = next(a["text"] for a in thorns["abilities"]
                if a["name"] == "Initialization")
    assert "Active Spot" in text
    assert "Rule Box" in text
    assert "no Abilities" in text
    assert "except for Future Pokémon" in text
    assert has_rule_box(thorns)
    assert not thorns_suppresses(thorns)

    expected = {
        RADIANT: (True, "Climactic Gate"),
        SHADOW_VMAX: (True, "Underworld Door"),
        TAPU_LELE: (True, "Wonder Tag"),
        VILEPLUME: (False, "Irritating Pollen"),
        PIDGEOT_EX: (True, "Quick Search"),
        FAN_ROTOM: (False, "Fan Call"),
        JIRACHI: (False, "Stellar Wish"),
    }
    for card_id, (disabled, ability) in expected.items():
        card = cards[card_id]
        assert ability in ability_names(card), (card_id, ability)
        assert thorns_suppresses(card) is disabled
        assert not thorns_suppresses(card, thorns_active=False)
        print(
            f"{card['name']} ({ability}): "
            f"{'suppressed' if disabled else 'available'}"
        )

    assert POKEMON["Radiant Eternatus"] == 1
    assert POKEMON["Shadow Rider Calyrex VMAX"] == 4
    unlocked = sum(
        probability for label, probability in exact().items()
        if label.endswith("_2")
    )
    assert unlocked > 0
    assert thorns_suppresses(cards[RADIANT])
    locked = 0  # Climactic Gate cannot activate under this constant lock.
    assert locked == 0

    print(f"Unlocked direct/Treasure dual VMAX: {float(unlocked):.12%}")
    print("Same Ability-mediated endpoint under active Initialization: 0%")
    print("No inference about complete-match win rate or suppression counterplay")


if __name__ == "__main__":
    main()
