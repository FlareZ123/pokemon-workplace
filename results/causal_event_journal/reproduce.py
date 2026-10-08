"""Reproduce the cross-domain causal event journal with real kernels."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ability_lock_dependency_graph import AbilityLockSourceRef
from board_object_kernel import ToolAttachment, make_board, make_pokemon
from causal_event_journal import append_boundary, begin_journal, replay_journal
from committed_play_event import (
    PlayKind, from_forced_supporter, from_supporter_execution, has_play_history,
)
from forced_supporter_execution import (
    ForcedSupporterState, SupporterInstance, begin_hand_control,
)
from supporter_play_event_history import (
    SupporterExecutionState, SupporterIdentity,
    copy_supporter_effect_as_attack, play_supporter_from_hand,
)
from turn_action_budget import TurnActionBudget


def add(journal, event_id, description, player, opponent, event=None):
    return append_boundary(
        journal, expected_revision=journal.revision, event_id=event_id,
        description=description, player_board=player, opponent_board=opponent,
        committed_play=event,
    )


def fails(call, error):
    try:
        call()
    except error:
        return
    raise AssertionError(f"expected {error.__name__}")


def main() -> None:
    empoleon = make_pokemon(
        "emp", "Empoleon V", print_id="swsh5-40",
        tags={"Basic", "Water", "RuleBox"},
    )
    wobbuffet = make_pokemon(
        "wob", "Wobbuffet", print_id="xy4-36",
        tags={"Basic", "Psychic"},
    )
    filler = make_pokemon(
        "fill", "Filler", print_id="synthetic-fill", tags={"Basic"},
    )
    player, opponent = make_board(empoleon), make_board(wobbuffet)
    j = begin_journal(player, opponent, first_player_owner="player")
    assert j.lock_state.basis == "setup_first_player"

    supporter = SupporterIdentity("supp-1", "Team Rocket's Ariana")
    support_base = SupporterExecutionState()
    support_played = play_supporter_from_hand(support_base, supporter)
    assert support_played is not None
    normal = from_supporter_execution(support_base, support_played, player="A")
    assert normal is not None and normal.consumed_ordinary_quota
    copied = copy_supporter_effect_as_attack(support_base, supporter)
    assert copied is not None
    assert from_supporter_execution(support_base, copied, player="A") is None

    j = add(j, "normal-play", "normal Supporter play", player, opponent, normal)
    assert j.lock_state.basis == "setup_first_player"
    assert has_play_history(
        j.committed_plays, player="A", kind=PlayKind.SUPPORTER,
        name_contains="Team Rocket",
    )

    forced_card = SupporterInstance("supp-2", "Team Rocket's Ariana")
    forced_base = ForcedSupporterState(
        current_player="A", other_player="B",
        current_budget=TurnActionBudget(), other_budget=TurnActionBudget(),
        other_hand=(forced_card,),
    )
    forced_state = begin_hand_control(forced_base, forced_card.copy_id)
    assert forced_state is not None
    forced = from_forced_supporter(forced_state)
    assert forced is not None

    j = add(j, "forced-play", "out-of-turn forced Supporter", player, opponent, forced)
    assert j.committed_plays == (normal, forced)
    assert forced.out_of_turn and not forced.consumed_ordinary_quota

    interrupted_board = make_board(filler, (wobbuffet,))
    restored_board = make_board(wobbuffet, (filler,))
    direct = add(j, "direct", "sample later endpoint only", player, restored_board)
    assert direct.lock_state.resolved
    assert direct.lock_state.basis == "setup_first_player"

    interrupted = add(
        j, "move-away", "Wobbuffet leaves Active", player, interrupted_board,
    )
    assert interrupted.lock_state.resolved
    assert interrupted.lock_state.basis == "snapshot"
    restored = add(
        interrupted, "move-back", "Wobbuffet returns Active",
        player, restored_board,
    )
    assert not restored.lock_state.resolved
    assert restored.lock_state.basis == "unresolved"
    assert restored.lock_state.resolution.active_sources is None
    assert restored.boundaries[-1].opponent_board == direct.boundaries[-1].opponent_board
    assert direct.lock_state != restored.lock_state
    assert direct.committed_plays == restored.committed_plays
    assert replay_journal(restored) == restored

    fails(
        lambda: append_boundary(
            restored, expected_revision=0, event_id="stale", description="stale",
            player_board=player, opponent_board=restored_board,
        ),
        ValueError,
    )
    fails(
        lambda: add(
            restored, "normal-play", "duplicate", player, restored_board,
        ),
        ValueError,
    )
    corrupted = replace(
        restored.boundaries[-1], lock_state=direct.lock_state,
    )
    corrupted_journal = replace(
        restored, boundaries=restored.boundaries[:-1] + (corrupted,),
    )
    fails(lambda: replay_journal(corrupted_journal), AssertionError)

    ting_lu = make_pokemon(
        "ting", "Ting-Lu ex", print_id="sv2-127",
        tags={"Basic", "Fighting", "ex", "RuleBox"},
    )
    opponent_active = make_pokemon(
        "other", "Opponent Active", print_id="synthetic-active", tags={"Basic"},
    )
    garbodor = make_pokemon(
        "garb", "Garbodor", print_id="xy9-57",
        tags={"Stage1", "Psychic"},
        tool=ToolAttachment("float-1", "Float Stone"),
    )
    t_player = make_board(ting_lu)
    t_opponent = make_board(opponent_active, (garbodor,))
    t = begin_journal(t_player, t_opponent)
    assert t.lock_state.resolution.active_sources == (
        AbilityLockSourceRef("opponent", "garb"),
    )
    damaged = replace(garbodor, damage_counters=1)
    t = add(
        t, "damage", "Cursed Land reverse edge becomes eligible",
        t_player, make_board(opponent_active, (damaged,)),
    )
    assert t.lock_state.basis == "verified_established"
    assert t.lock_state.resolution.active_sources == (
        AbilityLockSourceRef("opponent", "garb"),
    )
    t = add(t, "heal", "remove reverse edge", t_player, t_opponent)
    assert t.lock_state.basis == "snapshot"
    assert replay_journal(t) == t

    print(
        "causal_event_journal regression: PASS; "
        "same physical endpoint, distinct continuous precedence; "
        "ordinary and forced plays remain distinct; "
        "revision/replay guards pass"
    )


if __name__ == "__main__":
    main()
