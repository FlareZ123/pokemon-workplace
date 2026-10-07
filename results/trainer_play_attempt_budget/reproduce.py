"""Reproduce quota timing around Seismitoad Quaking Fist."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from build_expanded_legality_baseline import classify_effective_legality
from trainer_play_attempt_budget import (
    QuotaTrainerKind,
    TrainerAttemptState,
    TrainerCard,
    begin_trainer_attempt,
    fail_quaking_fist_gate,
    pass_quaking_fist_gate,
)
from turn_action_budget import TurnAction, TurnActionBudget


def load_set(set_id: str) -> list[dict]:
    return json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )


def main() -> None:
    seismitoad = next(
        card for card in load_set("me55") if card["id"] == "me55-84"
    )
    status, _ = classify_effective_legality(seismitoad)
    assert status == "Legal"
    quaking = next(
        attack
        for attack in seismitoad["attacks"]
        if attack["name"] == "Quaking Fist"
    )
    assert quaking["text"] == (
        "During your opponent's next turn, whenever they try to use a Trainer "
        "card from their hand, they flip a coin. If tails, your opponent "
        "discards that Trainer card instead of using it."
    )

    supporter_a = TrainerCard(
        "supporter-a",
        "Supporter A",
        QuotaTrainerKind.SUPPORTER,
    )
    supporter_b = TrainerCard(
        "supporter-b",
        "Supporter B",
        QuotaTrainerKind.SUPPORTER,
    )
    stadium_a = TrainerCard(
        "stadium-a",
        "Stadium A",
        QuotaTrainerKind.STADIUM,
    )
    stadium_b = TrainerCard(
        "stadium-b",
        "Stadium B",
        QuotaTrainerKind.STADIUM,
    )
    old_stadium = TrainerCard(
        "stadium-old",
        "Old Stadium",
        QuotaTrainerKind.STADIUM,
    )

    # A failed Supporter attempt is discarded while the Supporter quota remains.
    state = TrainerAttemptState(
        budget=TurnActionBudget(),
        hand=(supporter_a, supporter_b),
    )
    attempt = begin_trainer_attempt(state, supporter_a.copy_id)
    assert attempt is not None
    assert attempt.budget.supporter_plays_used == 0
    failed = fail_quaking_fist_gate(attempt)
    assert failed is not None
    assert failed.discard == (supporter_a,)
    assert failed.budget.supporter_plays_used == 0
    assert failed.successful_supporters == 0
    assert failed.budget.can(TurnAction.SUPPORTER)

    # A second Supporter can be attempted and, on heads, commits the one use.
    retry = begin_trainer_attempt(failed, supporter_b.copy_id)
    assert retry is not None
    success = pass_quaking_fist_gate(retry)
    assert success is not None
    assert success.budget.supporter_plays_used == 1
    assert success.successful_supporters == 1
    assert not success.budget.can(TurnAction.SUPPORTER)

    # The same transactional rule applies to Stadium play. Tails discards the
    # attempted copy while the existing Stadium remains and quota stays open.
    stadium_state = TrainerAttemptState(
        budget=TurnActionBudget(),
        hand=(stadium_a, stadium_b),
        stadium_in_play=old_stadium,
    )
    stadium_attempt = begin_trainer_attempt(stadium_state, stadium_a.copy_id)
    assert stadium_attempt is not None
    stadium_failed = fail_quaking_fist_gate(stadium_attempt)
    assert stadium_failed is not None
    assert stadium_failed.discard == (stadium_a,)
    assert stadium_failed.stadium_in_play == old_stadium
    assert stadium_failed.budget.stadium_plays_used == 0
    assert stadium_failed.successful_stadium_plays == 0
    assert stadium_failed.budget.can(TurnAction.STADIUM_PLAY)

    stadium_retry = begin_trainer_attempt(
        stadium_failed,
        stadium_b.copy_id,
    )
    assert stadium_retry is not None
    stadium_success = pass_quaking_fist_gate(stadium_retry)
    assert stadium_success is not None
    assert stadium_success.stadium_in_play == stadium_b
    assert old_stadium in stadium_success.discard
    assert stadium_success.budget.stadium_plays_used == 1
    assert stadium_success.successful_stadium_plays == 1

    # Ordinary same-name Stadium legality is checked before entering the gate.
    same_name = TrainerCard(
        "stadium-same",
        old_stadium.name,
        QuotaTrainerKind.STADIUM,
    )
    same_state = TrainerAttemptState(
        budget=TurnActionBudget(),
        hand=(same_name,),
        stadium_in_play=old_stadium,
    )
    assert begin_trainer_attempt(same_state, same_name.copy_id) is None

    print("trainer_play_attempt_budget regression: PASS")


if __name__ == "__main__":
    main()
