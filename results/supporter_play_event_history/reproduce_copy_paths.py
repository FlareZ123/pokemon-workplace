from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from supporter_play_event_history import (
    SupporterExecutionState,
    SupporterIdentity,
    copy_supporter_effect_as_attack,
    play_supporter_from_hand,
    played_supporter_from_hand,
)


def main() -> None:
    ariana = SupporterIdentity("ariana-1", "Team Rocket's Ariana")
    sabrina = SupporterIdentity("sabrina-1", "Sabrina's Suggestion")

    copied_by_attack = copy_supporter_effect_as_attack(
        SupporterExecutionState(), ariana
    )
    assert copied_by_attack is not None
    assert not played_supporter_from_hand(copied_by_attack)
    assert copied_by_attack.budget.supporter_plays_used == 0

    copied_by_supporter = play_supporter_from_hand(
        SupporterExecutionState(),
        sabrina,
        delegated_body_source=ariana,
    )
    assert copied_by_supporter is not None
    assert played_supporter_from_hand(copied_by_supporter)
    assert not played_supporter_from_hand(
        copied_by_supporter,
        name_contains="Team Rocket",
    )
    assert copied_by_supporter.last_execution is not None
    assert copied_by_supporter.last_execution.body_source_name == "Team Rocket's Ariana"
    assert copied_by_supporter.last_execution.outer_played_name == "Sabrina's Suggestion"

    print("supporter_play_event_history copy-path regression: PASS")


if __name__ == "__main__":
    main()
