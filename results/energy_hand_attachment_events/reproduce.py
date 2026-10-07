"""Reproduce Energy-from-hand event versus manual-quota semantics."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from energy_hand_attachment_corpus import energy_hand_attachment_trigger_rows
from energy_hand_attachment_events import (
    AttachmentChannel, EnergyAttachmentState, EnergyCard, attach_from_hand,
    hand_attachment_events,
)
from turn_action_budget import TurnAction, TurnActionBudget


def main() -> None:
    rows = energy_hand_attachment_trigger_rows(ROOT / "resources")
    assert len(rows) == 55
    assert len({row["name"] for row in rows}) == 33

    sv8 = json.loads((ROOT / "resources" / "cards" / "en" / "sv8.json").read_text(encoding="utf-8"))
    exeggutor = next(card for card in sv8 if card["id"] == "sv8-133")
    tropical = next(a for a in exeggutor["attacks"] if a["name"] == "Tropical Frenzy")
    assert tropical["text"] == (
        "You may attach any number of Basic Energy cards from your hand to your "
        "Pokémon in any way you like."
    )

    fire = EnergyCard("fire-1", "Basic Fire Energy")
    water = EnergyCard("water-1", "Basic Water Energy")
    grass = EnergyCard("grass-1", "Basic Grass Energy")
    base = EnergyAttachmentState(
        budget=TurnActionBudget(), hand=(fire, water, grass)
    )

    effect = attach_from_hand(
        base, ((fire.copy_id, "p1"), (water.copy_id, "p1")),
        player="A", channel=AttachmentChannel.EFFECT,
    )
    assert effect is not None
    assert len(hand_attachment_events(effect, player="A")) == 2
    assert effect.budget.manual_energy_attachments_used == 0
    assert effect.budget.can(TurnAction.MANUAL_ENERGY_ATTACHMENT)

    manual = attach_from_hand(
        effect, ((grass.copy_id, "p1"),),
        player="A", channel=AttachmentChannel.MANUAL,
    )
    assert manual is not None
    assert len(hand_attachment_events(manual, player="A")) == 3
    assert manual.budget.manual_energy_attachments_used == 1
    assert not manual.budget.can(TurnAction.MANUAL_ENERGY_ATTACHMENT)

    assert attach_from_hand(
        base, ((fire.copy_id, "p1"), (water.copy_id, "p1")),
        player="A", channel=AttachmentChannel.MANUAL,
    ) is None

    print("energy_hand_attachment_events regression: PASS")
    print("trigger print rows:", len(rows))


if __name__ == "__main__":
    main()
