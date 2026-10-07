from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from typed_energy_access import (  # noqa: E402
    Zone,
    dragon_claw_ready,
    make_state,
    shortest_dragon_claw_setup,
)


def load_cards() -> dict[str, dict]:
    cards: dict[str, dict] = {}
    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json")):
        for card in json.loads(path.read_text(encoding="utf-8")):
            cards[card["id"]] = card
    return cards


def base_state(**kwargs: object):
    return make_state(
        {
            "Bagon": Zone.ACTIVE.value,
            "Crispin": Zone.HAND.value,
            "Fire Energy": Zone.DECK.value,
            "Water Energy": Zone.DECK.value,
        },
        **kwargs,
    )


def main() -> None:
    cards = load_cards()
    bagon = cards["dv1-6"]
    crispin = cards["sv7-133"]
    assert bagon["legalities"]["expanded"] == "Legal"
    assert crispin["legalities"]["expanded"] == "Legal"
    assert bagon["attacks"][1]["name"] == "Dragon Claw"
    assert bagon["attacks"][1]["cost"] == ["Fire", "Water"]
    assert "Basic Energy cards of different types" in crispin["rules"][0]
    assert "put 1 of them into your hand" in crispin["rules"][0]
    assert "Attach the other to 1 of your Pokémon" in crispin["rules"][0]

    result = shortest_dragon_claw_setup(base_state())
    assert result is not None
    line, final = result
    assert len(line) == 2
    assert line[0].startswith("Play Crispin; attach")
    assert line[1].startswith("Attach")
    assert dragon_claw_ready(final)
    assert final.supporter_used
    assert final.manual_attachment_used
    assert sorted(final.attached_units) == ["R", "W"]

    # Crispin's effect attachment does not consume the normal attachment. The
    # two-channel line fails if that separate manual attachment was already spent.
    spent = shortest_dragon_claw_setup(base_state(manual_attachment_used=True))
    assert spent is None

    # Disabling only the normal attachment still allows Crispin's effect attach,
    # but leaves the second typed requirement unpaid.
    assert shortest_dragon_claw_setup(
        base_state(manual_attachment_allowed=False)
    ) is None

    # Supporter bandwidth is also a distinct gate.
    assert shortest_dragon_claw_setup(base_state(supporter_used=True)) is None
    assert shortest_dragon_claw_setup(base_state(supporters_allowed=False)) is None

    # Crispin needs two different Basic Energy types for this exact RW setup.
    missing = base_state()
    locations = dict(missing.locations)
    locations["Water Energy"] = Zone.HAND.value
    missing = make_state(locations)
    # With Water already in hand, the represented Crispin action requiring both
    # searched cards is unavailable. The manual attach alone leaves Fire unpaid.
    assert shortest_dragon_claw_setup(missing) is None

    # Either Crispin branch works: Fire by effect + Water manually, or vice versa.
    assert "Fire Energy" in line[0] or "Water Energy" in line[0]

    print(json.dumps({
        "baseline_actions": line,
        "baseline_length": len(line),
        "supporter_spent_reachable": False,
        "manual_attachment_spent_reachable": False,
        "manual_attachment_disabled_reachable": False,
        "missing_second_deck_type_reachable": False,
        "attached_units": sorted(final.attached_units),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
