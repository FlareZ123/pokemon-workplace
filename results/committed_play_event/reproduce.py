"""Reproduce committed play-event bridging across action channels."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from committed_play_event import (
    PlayKind, from_forced_supporter, from_stadium_entry, from_supporter_execution,
    from_trainer_attempt, has_play_history,
)
from forced_supporter_execution import ForcedSupporterState, SupporterInstance, begin_hand_control
from stadium_entry_channels import StadiumCopy, StadiumEntryState, play_stadium_from_hand, use_teleport_room
from supporter_play_event_history import (
    SupporterExecutionState, SupporterIdentity, copy_supporter_effect_as_attack, play_supporter_from_hand,
)
from trainer_play_attempt_budget import (
    QuotaTrainerKind, TrainerAttemptState, TrainerCard, begin_trainer_attempt,
    fail_quaking_fist_gate, pass_quaking_fist_gate,
)
from turn_action_budget import TurnActionBudget


def main() -> None:
    ariana = SupporterIdentity("ariana-1", "Team Rocket's Ariana")
    base = SupporterExecutionState()
    direct = play_supporter_from_hand(base, ariana)
    assert direct is not None
    direct_event = from_supporter_execution(base, direct, player="A")
    assert direct_event is not None and direct_event.consumed_ordinary_quota
    assert has_play_history(
        (direct_event,), player="A", kind=PlayKind.SUPPORTER, name_contains="Team Rocket"
    )

    copied = copy_supporter_effect_as_attack(base, ariana)
    assert copied is not None
    assert from_supporter_execution(base, copied, player="A") is None

    card = TrainerCard("supporter-1", "Example Supporter", QuotaTrainerKind.SUPPORTER)
    attempt_base = TrainerAttemptState(budget=TurnActionBudget(), hand=(card,))
    pending = begin_trainer_attempt(attempt_base, card.copy_id)
    assert pending is not None
    failed = fail_quaking_fist_gate(pending)
    assert failed is not None
    assert from_trainer_attempt(pending, failed, player="A") is None

    pending = begin_trainer_attempt(attempt_base, card.copy_id)
    assert pending is not None
    passed = pass_quaking_fist_gate(pending)
    assert passed is not None
    assert from_trainer_attempt(pending, passed, player="A") is not None

    alpha = StadiumCopy("alpha-1", "Alpha")
    beta = StadiumCopy("beta-1", "Beta")
    gamma = StadiumCopy("gamma-1", "Gamma")
    stadium_base = StadiumEntryState(
        budget=TurnActionBudget(), hand=(beta,), discard=(gamma,),
        in_play=alpha, teleport_room_sources=frozenset({"goth-1"}),
    )
    teleported = use_teleport_room(stadium_base, "goth-1", "gamma-1")
    assert teleported is not None
    assert from_stadium_entry(stadium_base, teleported, player="A") is None

    played = play_stadium_from_hand(stadium_base, "beta-1")
    assert played is not None
    assert from_stadium_entry(stadium_base, played, player="A") is not None

    forced_card = SupporterInstance("forced-1", "Team Rocket's Ariana")
    forced_base = ForcedSupporterState(
        current_player="A", other_player="B", current_budget=TurnActionBudget(),
        other_budget=TurnActionBudget(), other_hand=(forced_card,),
    )
    forced = begin_hand_control(forced_base, forced_card.copy_id)
    assert forced is not None
    forced_event = from_forced_supporter(forced)
    assert forced_event is not None
    assert forced_event.out_of_turn and not forced_event.consumed_ordinary_quota
    assert has_play_history(
        (forced_event,), player="B", kind=PlayKind.SUPPORTER, name_contains="Team Rocket"
    )

    print("committed_play_event regression: PASS")


if __name__ == "__main__":
    main()
