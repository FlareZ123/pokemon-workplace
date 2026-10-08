"""Official Venomoth Q&A: tails discard, no Supporter use; second attempt legal."""
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon
from causal_event_journal import append_boundary, begin_journal, replay_journal
from committed_play_event import PlayKind
from dizzying_wind_attempt_event import (
    failed_trainer_attempt_event, resolve_dizzying_wind_supporter,
)
from tools.trainer_play_attempt_budget import (
    QuotaTrainerKind, TrainerAttemptState, TrainerCard,
    begin_trainer_attempt, fail_quaking_fist_gate,
)
from tools.turn_action_budget import TurnAction, TurnActionBudget


def fails(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def main():
    venoms = json.loads(
        (ROOT / "resources" / "cards" / "en" / "xy4.json").read_text(encoding="utf-8")
    )
    venomoth = next(row for row in venoms if row["id"] == "xy4-2")
    assert any(
        attack["name"] == "Dizzying Wind"
        and "that card has no effect" in attack["text"]
        for attack in venomoth["attacks"]
    )

    a = TrainerCard("supp-a", "Professor Sycamore", QuotaTrainerKind.SUPPORTER)
    b = TrainerCard("supp-b", "Colress", QuotaTrainerKind.SUPPORTER)
    before = TrainerAttemptState(TurnActionBudget(), hand=(a, b))
    own = make_board(make_pokemon("own", "Own Active", tags={"Basic"}))
    opponent = make_board(make_pokemon("opponent", "Venomoth", tags={"Stage1"}))
    journal = begin_journal(own, opponent)

    tails = resolve_dizzying_wind_supporter(
        before, copy_id="supp-a", heads=False, player="A",
    )
    assert tails is not None
    assert tails.failed_attempt is not None
    assert tails.committed_play is None
    assert tails.after.discard == (a,)
    assert tails.after.budget.supporter_plays_used == 0
    assert tails.after.successful_supporters == 0
    assert tails.after.budget.can(TurnAction.SUPPORTER)
    journal = append_boundary(
        journal, expected_revision=journal.revision,
        event_id="sycamore-tails", description="Dizzying Wind failed Supporter attempt",
        player_board=own, opponent_board=opponent, failed_attempt=tails.failed_attempt,
    )
    assert journal.committed_plays == ()
    assert journal.failed_trainers == (tails.failed_attempt,)
    assert journal.queried_play(player="A", kind=PlayKind.SUPPORTER) is False

    heads = resolve_dizzying_wind_supporter(
        tails.after, copy_id="supp-b", heads=True, player="A",
    )
    assert heads is not None
    assert heads.committed_play is not None
    assert heads.failed_attempt is None
    assert heads.after.discard == (a, b)
    assert heads.after.successful_supporters == 1
    assert heads.after.budget.supporter_plays_used == 1
    assert not heads.after.budget.can(TurnAction.SUPPORTER)
    journal = append_boundary(
        journal, expected_revision=journal.revision,
        event_id="colress-heads", description="second Supporter succeeds",
        player_board=own, opponent_board=opponent,
        committed_play=heads.committed_play,
    )
    assert journal.committed_plays == (heads.committed_play,)
    assert journal.failed_trainers == (tails.failed_attempt,)
    assert journal.queried_play(
        player="A", kind=PlayKind.SUPPORTER, name_contains="Colress",
    ) is True
    assert journal.queried_play(
        player="A", kind=PlayKind.SUPPORTER, name_contains="Sycamore",
    ) is False
    assert replay_journal(journal) == journal

    # A failed card's proof cannot be reclassified as successful, and vice versa.
    attempt = begin_trainer_attempt(before, "supp-a")
    assert attempt is not None
    after_fail = fail_quaking_fist_gate(attempt)
    assert after_fail is not None
    fails(lambda: failed_trainer_attempt_event(
        attempt, heads.after, player="A", gate_source="dizzying_wind",
    ))
    fails(lambda: append_boundary(
        journal, expected_revision=journal.revision,
        event_id="contradiction", description="illegal dual classification",
        player_board=own, opponent_board=opponent,
        failed_attempt=tails.failed_attempt,
        committed_play=heads.committed_play,
    ))
    assert resolve_dizzying_wind_supporter(
        heads.after, copy_id="supp-a", heads=True, player="A",
    ) is None
    print(
        "dizzying_wind_attempt_event regression: PASS; "
        "failed Supporter discarded without quota, second Supporter succeeds; "
        "failed and committed action histories remain distinguishable"
    )


if __name__ == "__main__":
    main()
