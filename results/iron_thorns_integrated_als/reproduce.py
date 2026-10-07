from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from iron_thorns_integrated_als import (
    DCE, FODDER_A, FODDER_B, GUZMA_HALA, IRON_THORNS, TAG_CALL,
    THUNDER_MOUNTAIN, Zone, make_state, shortest_volt_cyclone_line,
    volt_cyclone_ready,
)


def load_cards() -> dict[str, dict]:
    cards: dict[str, dict] = {}
    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json")):
        for card in json.loads(path.read_text(encoding="utf-8")):
            cards[card["id"]] = card
    return cards


def contains_rule(card: dict, fragment: str) -> bool:
    return any(fragment in rule for rule in card.get("rules", []))


def baseline_locations() -> dict[str, str]:
    return {
        IRON_THORNS: Zone.ACTIVE.value,
        TAG_CALL: Zone.HAND.value,
        GUZMA_HALA: Zone.DECK.value,
        THUNDER_MOUNTAIN: Zone.DECK.value,
        DCE: Zone.DECK.value,
        FODDER_A: Zone.HAND.value,
        FODDER_B: Zone.HAND.value,
    }


def main() -> None:
    cards = load_cards()
    tag_call = cards["sm12-206"]
    assert tag_call["legalities"]["expanded"] == "Legal"
    assert contains_rule(tag_call, "up to 2 TAG TEAM cards")
    guzma_hala = cards["sm12-193"]
    assert guzma_hala["legalities"]["expanded"] == "Legal"
    assert contains_rule(guzma_hala, "discard 2 other cards from your hand")
    thunder = cards["sm8-191"]
    assert thunder["legalities"]["expanded"] == "Legal"
    assert contains_rule(thunder, "cost Lightning less")
    dce = cards["sm2-166"]
    assert dce["legalities"]["expanded"] == "Legal"
    assert contains_rule(dce, "provides ColorlessColorless Energy")
    thorns = cards["sv6-77"]
    assert thorns["legalities"]["expanded"] == "Legal"
    assert thorns["attacks"][0]["name"] == "Volt Cyclone"
    assert thorns["attacks"][0]["cost"] == ["Lightning", "Colorless", "Colorless"]

    baseline = make_state(baseline_locations())
    result = shortest_volt_cyclone_line(baseline)
    assert result is not None
    line, final_state = result
    assert len(line) == 5
    assert final_state.volt_cyclone_used

    complete_energy = make_state(
        {
            IRON_THORNS: Zone.ACTIVE.value,
            DCE: Zone.ATTACHED.value,
            THUNDER_MOUNTAIN: Zone.STADIUM.value,
        },
        stadium_played=True,
        manual_attachment_used=True,
    )
    assert volt_cyclone_ready(complete_energy)

    for key in ("items_allowed", "supporters_allowed", "stadiums_allowed",
                "attacks_allowed"):
        kwargs = {key: False}
        assert shortest_volt_cyclone_line(make_state(baseline_locations(), **kwargs)) is None
    assert shortest_volt_cyclone_line(
        make_state(baseline_locations(), manual_attachment_used=True)
    ) is None

    one_fodder = baseline_locations()
    one_fodder[FODDER_B] = Zone.DISCARD.value
    assert shortest_volt_cyclone_line(make_state(one_fodder)) is None

    prized_thunder = baseline_locations()
    prized_thunder[THUNDER_MOUNTAIN] = Zone.PRIZE.value
    assert shortest_volt_cyclone_line(make_state(prized_thunder)) is None

    prized_dce = baseline_locations()
    prized_dce[DCE] = Zone.PRIZE.value
    assert shortest_volt_cyclone_line(make_state(prized_dce)) is None

    natural = baseline_locations()
    natural[TAG_CALL] = Zone.DISCARD.value
    natural[GUZMA_HALA] = Zone.HAND.value
    natural_result = shortest_volt_cyclone_line(make_state(natural))
    assert natural_result is not None
    assert len(natural_result[0]) == 4

    print("iron_thorns_integrated_als: all assertions passed")
    for index, action in enumerate(line, start=1):
        print(f"{index}. {action}")


if __name__ == "__main__":
    main()
