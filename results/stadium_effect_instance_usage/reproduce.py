"""Reproduce Brooklet Hill per-instance Stadium effect usage."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from build_expanded_legality_baseline import classify_effective_legality
from stadium_effect_instance_usage import (
    StadiumCard,
    StadiumEffectState,
    StadiumInPlay,
    can_use_current_stadium_effect,
    discard_current_stadium,
    play_stadium_from_hand,
    use_current_stadium_effect,
)
from turn_action_budget import TurnAction


def main() -> None:
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / "sm2.json").read_text(
            encoding="utf-8"
        )
    )
    brooklet = next(card for card in cards if card["id"] == "sm2-120")
    status, _ = classify_effective_legality(brooklet)
    assert status == "Legal"
    assert brooklet["name"] == "Brooklet Hill"
    assert brooklet["rules"][0].startswith("Once during each player's turn")

    first = StadiumCard("brooklet-a", "Brooklet Hill")
    second = StadiumCard("brooklet-b", "Brooklet Hill")

    state = StadiumEffectState(
        budget=__import__("turn_action_budget").TurnActionBudget(),
        hand=(second,),
        in_play=StadiumInPlay(first, "brooklet-instance-a"),
    )

    assert can_use_current_stadium_effect(state)
    after_first_use = use_current_stadium_effect(state)
    assert after_first_use is not None
    assert not can_use_current_stadium_effect(after_first_use)
    assert after_first_use.budget.stadium_plays_used == 0

    # Field Blower-like removal does not itself consume the Stadium-play quota.
    after_removal = discard_current_stadium(after_first_use)
    assert after_removal is not None
    assert after_removal.in_play is None
    assert after_removal.discard == (first,)
    assert after_removal.budget.can(TurnAction.STADIUM_PLAY)

    # A second physical copy with the same name enters as a fresh in-play
    # instance and can use its effect during the same turn.
    after_second_play = play_stadium_from_hand(
        after_removal,
        second.copy_id,
        instance_id="brooklet-instance-b",
    )
    assert after_second_play is not None
    assert after_second_play.budget.stadium_plays_used == 1
    assert can_use_current_stadium_effect(after_second_play)

    after_second_use = use_current_stadium_effect(after_second_play)
    assert after_second_use is not None
    assert not can_use_current_stadium_effect(after_second_use)
    assert after_second_use.used_effect_instances == frozenset(
        {"brooklet-instance-a", "brooklet-instance-b"}
    )

    print("stadium_effect_instance_usage regression: PASS")


if __name__ == "__main__":
    main()
