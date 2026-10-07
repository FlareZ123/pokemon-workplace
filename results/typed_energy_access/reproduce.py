from __future__ import annotations

import json
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from typed_energy_access import (  # noqa: E402
    Zone,
    make_state,
    shortest_volt_cyclone_setup,
    volt_cyclone_ready,
)


def load_cards() -> dict[str, dict]:
    cards: dict[str, dict] = {}
    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json")):
        for card in json.loads(path.read_text(encoding="utf-8")):
            cards[card["id"]] = card
    return cards


def base_state(**kwargs: object):
    locations = {
        "Iron Thorns ex": Zone.ACTIVE.value,
        "Tag Call": Zone.HAND.value,
        "Guzma & Hala": Zone.DECK.value,
        "Double Colorless Energy": Zone.DECK.value,
        "Thunder Mountain Prism Star": Zone.DECK.value,
        "Fodder A": Zone.HAND.value,
        "Fodder B": Zone.HAND.value,
    }
    return make_state(locations, **kwargs)


def main() -> None:
    cards = load_cards()
    assert "Search your deck for up to 2 TAG TEAM cards" in cards["sm12-206"]["rules"][0]
    assert "may discard 2 other cards" in cards["sm12-193"]["rules"][1]
    assert "Special Energy card" in cards["sm12-193"]["rules"][1]
    assert "provides ColorlessColorless Energy" in cards["sm2-166"]["rules"][0]
    assert "cost Lightning less" in cards["sm8-191"]["rules"][0]
    assert cards["sv6-77"]["attacks"][0]["cost"] == [
        "Lightning", "Colorless", "Colorless"
    ]
    for card_id in ("sm12-206", "sm12-193", "sm2-166", "sm8-191", "sv6-77"):
        assert cards[card_id]["legalities"]["expanded"] == "Legal"

    result = shortest_volt_cyclone_setup(base_state())
    assert result is not None
    line, final = result
    assert len(line) == 4
    assert line[0].startswith("Tag Call")
    assert "discard 2" in line[1]
    assert set(line[2:]) == {
        "Play Thunder Mountain Prism Star",
        "Attach Double Colorless Energy to Iron Thorns ex",
    }
    assert volt_cyclone_ready(final)

    # The optional discard search is strategically mandatory for this represented
    # zero-Energy start. One missing discardable card removes DCE access.
    missing_fodder = base_state()
    loc = dict(missing_fodder.locations)
    loc["Fodder B"] = Zone.DECK.value
    missing_fodder = make_state(loc)
    assert shortest_volt_cyclone_setup(missing_fodder) is None

    # Item lock removes the Tag Call edge before the Supporter is accessible.
    assert shortest_volt_cyclone_setup(base_state(items_allowed=False)) is None

    # Supporter lock leaves Tag Call live but removes the G&H transition.
    assert shortest_volt_cyclone_setup(base_state(supporters_allowed=False)) is None

    # Stadium denial preserves DCE access but prevents the Lightning reduction.
    assert shortest_volt_cyclone_setup(base_state(stadiums_allowed=False)) is None

    # A consumed manual attachment prevents DCE from reaching the attacker.
    assert shortest_volt_cyclone_setup(
        base_state(manual_attachment_used=True)
    ) is None

    # Attack readiness is separate from board construction.
    no_attack = shortest_volt_cyclone_setup(base_state(attacks_allowed=False))
    assert no_attack is None

    # If DCE is already attached, Thunder Mountain alone can finish the Energy
    # condition after the G&H access line, and the manual attachment is irrelevant.
    preattached = base_state(manual_attachment_used=True)
    loc = dict(preattached.locations)
    loc["Double Colorless Energy"] = Zone.ATTACHED.value
    preattached = make_state(
        loc,
        manual_attachment_used=True,
        attached_units=("C", "C"),
    )
    assert not volt_cyclone_ready(preattached)
    prior = shortest_volt_cyclone_setup(preattached)
    assert prior is not None
    assert len(prior[0]) == 3
    assert volt_cyclone_ready(prior[1])

    print(json.dumps({
        "baseline_actions": line,
        "baseline_length": len(line),
        "missing_fodder_reachable": False,
        "item_lock_reachable": False,
        "supporter_lock_reachable": False,
        "stadium_denial_reachable": False,
        "manual_attachment_spent_reachable": False,
        "preattached_length": len(prior[0]),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
