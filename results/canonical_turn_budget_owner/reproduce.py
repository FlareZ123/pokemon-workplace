"""Reproduce canonical ownership of per-turn action bandwidth."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from action_quota_effects import DUAL_BRAINS, derive_action_quotas
from board_object_kernel import EnergyAttachment, make_board, make_pokemon
from canonical_turn_budget_owner import (
    CanonicalCompositeTurnState,
    promote_composite_turn_budget,
    retreat_with_canonical_budget,
)
from legacy_turn_budget_bridge import (
    apply_budget_to_unified,
    project_unified_turn_budget,
)
from turn_action_budget import TurnAction, TurnActionBudget
from unified_state_kernel import (
    Zone,
    attach_dce_to_active,
    consume_turn_action,
    effective_turn_budget,
    make_state,
    play_gladion,
    play_thunder_mountain,
    quick_ball_for_tapu_lele,
)


def _dual_brains_supporter_regression() -> None:
    first_budget = derive_action_quotas(TurnActionBudget(), (DUAL_BRAINS,))
    first_budget = first_budget.consume(TurnAction.SUPPORTER)
    assert first_budget is not None
    assert first_budget.supporter_plays_used == 1
    assert first_budget.supporter_play_limit == 2
    assert first_budget.can(TurnAction.SUPPORTER)

    state = make_state(
        {"Gladion": Zone.HAND.value},
        turn_budget=first_budget,
    )
    state = replace(
        state,
        bench=replace(state.bench, supporter_used=True),
    )
    played = play_gladion(state)
    assert len(played) == 1
    after = played[0][1]
    assert after.turn_budget is not None
    assert after.turn_budget.supporter_plays_used == 2
    assert not after.turn_budget.can(TurnAction.SUPPORTER)
    assert after.bench.supporter_used

    suppressed = derive_action_quotas(first_budget, ())
    assert suppressed.supporter_plays_used == 1
    assert suppressed.supporter_play_limit == 1
    assert not suppressed.can(TurnAction.SUPPORTER)
    restored = derive_action_quotas(suppressed, (DUAL_BRAINS,))
    assert restored.supporter_plays_used == 1
    assert restored.supporter_play_limit == 2
    assert restored.can(TurnAction.SUPPORTER)

    synced = apply_budget_to_unified(state, restored)
    assert synced.turn_budget == restored
    assert project_unified_turn_budget(synced) == restored


def _canonical_overrides_stale_legacy_flags() -> None:
    fresh = TurnActionBudget()
    energy = make_state(
        {
            "Iron Thorns ex": Zone.ACTIVE.value,
            "Double Colorless Energy": Zone.HAND.value,
        },
        active_name="Iron Thorns ex",
        active_tags=frozenset({"Lightning", "Basic"}),
        turn_budget=fresh,
        manual_attachment_used=True,
    )
    attached = attach_dce_to_active(energy)
    assert attached is not None
    assert attached.turn_budget is not None
    assert attached.turn_budget.manual_energy_attachments_used == 1

    stadium = make_state(
        {
            "Iron Thorns ex": Zone.ACTIVE.value,
            "Thunder Mountain Prism Star": Zone.HAND.value,
        },
        active_name="Iron Thorns ex",
        active_tags=frozenset({"Lightning", "Basic"}),
        turn_budget=fresh,
        stadium_used=True,
    )
    played = play_thunder_mountain(stadium)
    assert played is not None
    assert played.turn_budget is not None
    assert played.turn_budget.stadium_plays_used == 1

    ended_budget = fresh.consume(TurnAction.END_TURN)
    assert ended_budget is not None
    ended = make_state(
        {
            "Quick Ball": Zone.HAND.value,
            "Fodder": Zone.HAND.value,
            "Tapu Lele-GX": Zone.DECK.value,
        },
        turn_budget=ended_budget,
    )
    ended = replace(ended, bench=replace(ended.bench, turn_ended=False))
    assert quick_ball_for_tapu_lele(ended) == []
    assert effective_turn_budget(ended).turn_ended


def _composite_retreat_regression() -> None:
    active = make_pokemon(
        "a",
        "Active A",
        energy=(EnergyAttachment("e1", "Basic Energy 1", ("C",)),),
    )
    bench_b = make_pokemon(
        "b",
        "Bench B",
        energy=(EnergyAttachment("e2", "Basic Energy 2", ("C",)),),
    )
    board = make_board(active, (bench_b,))
    unified = make_state({})
    state = promote_composite_turn_budget(unified, board, retreat_limit=2)
    assert isinstance(state, CanonicalCompositeTurnState)
    assert state.budget.retreat_limit == 2

    first = retreat_with_canonical_budget(
        state,
        "b",
        retreat_cost=1,
        discard_energy_ids=("e1",),
    )
    assert first is not None
    after_first, discarded_first = first
    assert tuple(card.instance_id for card in discarded_first) == ("e1",)
    assert after_first.budget.retreats_used == 1
    assert after_first.budget.can(TurnAction.RETREAT)
    assert after_first.board.retreat_used

    second = retreat_with_canonical_budget(
        after_first,
        "a",
        retreat_cost=1,
        discard_energy_ids=("e2",),
    )
    assert second is not None
    after_second, discarded_second = second
    assert tuple(card.instance_id for card in discarded_second) == ("e2",)
    assert after_second.budget.retreats_used == 2
    assert not after_second.budget.can(TurnAction.RETREAT)

    ordinary = promote_composite_turn_budget(
        make_state({}),
        make_board(active, (bench_b,)),
    )
    ordinary_first = retreat_with_canonical_budget(
        ordinary,
        "b",
        retreat_cost=1,
        discard_energy_ids=("e1",),
    )
    assert ordinary_first is not None
    ordinary_after, _ = ordinary_first
    assert not ordinary_after.budget.can(TurnAction.RETREAT)


def _generic_turn_close_regression() -> None:
    state = make_state({}, turn_budget=TurnActionBudget())
    closed = consume_turn_action(state, TurnAction.ATTACK)
    assert closed is not None
    assert closed.turn_budget is not None
    assert closed.turn_budget.turn_ended
    for action in TurnAction:
        assert not closed.turn_budget.can(action)


def main() -> None:
    _dual_brains_supporter_regression()
    _canonical_overrides_stale_legacy_flags()
    _composite_retreat_regression()
    _generic_turn_close_regression()
    print("canonical_turn_budget_owner regression: PASS")


if __name__ == "__main__":
    main()
