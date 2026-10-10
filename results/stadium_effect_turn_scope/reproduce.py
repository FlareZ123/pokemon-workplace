"""Once-per-player-turn Stadium effect use refreshes at real turn boundaries."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for location in (ROOT, ROOT / "tools"):
    if str(location) not in sys.path:
        sys.path.insert(0, str(location))

from tools.board_position_state import BoardPokemon, PokemonCard, make_state
from tools.effect_evolution_source_gate import SourceActionContext, source_action_available
from tools.effect_evolution_timing import build_profiles
from tools.grand_tree_chain_execution import execute_grand_tree_chain
from tools.stadium_effect_instance_usage import (
    StadiumCard,
    StadiumEffectState,
    StadiumInPlay,
    begin_stadium_turn,
    can_use_current_stadium_effect,
    use_current_stadium_effect,
)
from tools.turn_attack_window import fresh_turn
from turn_action_budget import TurnActionBudget, TurnAction


def make_board(owner: str):
    base = BoardPokemon(
        f"{owner}-pokemon",
        (PokemonCard(f"{owner}-bulba", "Bulbasaur"),),
        retreat_cost=1,
        evolution_eligible=True,
    )
    return make_state((base,), active_id=f"{owner}-pokemon", evolution_allowed=True)


def context(stadium: StadiumEffectState, *, went_first: bool) -> SourceActionContext:
    return SourceActionContext(
        is_players_first_turn=False,
        went_first=went_first,
        window=fresh_turn(action_budget=stadium.budget),
        stadium_state=stadium,
    )


def use_tree(profile, stadium: StadiumEffectState, owner: str, *, went_first: bool):
    turn = context(stadium, went_first=went_first)
    assert source_action_available(profile, turn)
    outcome = execute_grand_tree_chain(
        profile,
        turn,
        make_board(owner),
        f"{owner}-pokemon",
        PokemonCard(f"{owner}-ivy", "Ivysaur", "Bulbasaur"),
        stage1_retreat_cost=2,
    )
    assert outcome is not None
    assert outcome.stadium_state is not None
    assert outcome.stadium_state.in_play == stadium.in_play
    assert outcome.stadium_state.used_effect_instances == {"grand-entry-1"}
    return outcome.stadium_state


def main() -> None:
    profiles = [p for p in build_profiles(ROOT / "resources") if p.card_id == "sv7-136"]
    assert len(profiles) == 1
    grand_tree = profiles[0]

    original = StadiumEffectState(
        budget=TurnActionBudget(stadium_plays_used=1),
        in_play=StadiumInPlay(
            StadiumCard("grand-tree-physical-1", "Grand Tree"),
            "grand-entry-1",
        ),
    )

    # Player A used Grand Tree; the same in-play copy is now exhausted.
    a_used = use_tree(grand_tree, original, "A", went_first=True)
    assert not can_use_current_stadium_effect(a_used)
    assert not source_action_available(
        grand_tree,
        context(a_used, went_first=True),
    )

    # End player A's turn. The Stadium stays on the table, and the next
    # player's fresh action budget permits the same Stadium effect.
    closed_budget = a_used.budget.consume(TurnAction.END_TURN)
    assert closed_budget is not None
    closed = replace(a_used, budget=closed_budget)
    assert not can_use_current_stadium_effect(closed)
    b_fresh = begin_stadium_turn(closed, action_budget=TurnActionBudget())
    assert b_fresh.in_play is original.in_play
    assert not b_fresh.used_effect_instances
    assert b_fresh.budget.stadium_plays_used == 0

    # Player B gets their own once-per-turn use without replaying a Stadium.
    b_used = use_tree(grand_tree, b_fresh, "B", went_first=False)
    assert not source_action_available(
        grand_tree, context(b_used, went_first=False)
    )

    # On a later turn for player A, Grand Tree's existing instance can
    # activate again, even though that physical copy never left play.
    a_again = begin_stadium_turn(b_used, action_budget=TurnActionBudget())
    assert a_again.in_play is original.in_play
    assert can_use_current_stadium_effect(a_again)
    next_a_used = use_tree(grand_tree, a_again, "A2", went_first=True)
    assert not can_use_current_stadium_effect(next_a_used)

    # A granted extra turn for the same player is also a distinct turn.
    extra_turn = begin_stadium_turn(
        next_a_used,
        action_budget=TurnActionBudget(),
    )
    assert can_use_current_stadium_effect(extra_turn)

    # Prevent a spurious usage reset by rejecting already-ended budgets.
    ended_budget = TurnActionBudget(turn_ended=True)
    try:
        begin_stadium_turn(extra_turn, action_budget=ended_budget)
    except ValueError:
        pass
    else:
        raise AssertionError("new actor turn with ended budget was accepted")

    # Source context remains immutable: the original Stadium has not been
    # consumed through the fresh next-turn states.
    assert can_use_current_stadium_effect(original)
    assert original.budget.stadium_plays_used == 1

    print("Stadium effect turn-boundary refresh regressions passed")


if __name__ == "__main__":
    main()
