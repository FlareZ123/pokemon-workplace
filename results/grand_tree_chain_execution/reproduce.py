"""Regression: Grand Tree's two evolutions share one Stadium activation."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for location in (ROOT, ROOT / "tools"):
    if str(location) not in sys.path:
        sys.path.insert(0, str(location))

from tools.board_position_state import BoardPokemon, PokemonCard, make_state
from tools.effect_evolution_source_gate import SourceActionContext
from tools.effect_evolution_timing import build_profiles
from tools.grand_tree_chain_execution import execute_grand_tree_chain
from tools.stadium_effect_instance_usage import StadiumCard, StadiumEffectState, StadiumInPlay
from tools.turn_attack_window import fresh_turn
from turn_action_budget import TurnActionBudget


def make_grand_tree_context() -> SourceActionContext:
    budget = TurnActionBudget(stadium_plays_used=1)
    stadium = StadiumEffectState(
        budget=budget,
        in_play=StadiumInPlay(
            StadiumCard("grand-tree-1", "Grand Tree"),
            "grand-tree-entry-1",
        ),
    )
    return SourceActionContext(
        is_players_first_turn=False,
        went_first=True,
        window=fresh_turn(action_budget=budget),
        stadium_state=stadium,
    )


def make_bulbasaur(*, first_turn: bool = False, new_basic: bool = False):
    bulbasaur = BoardPokemon(
        "bulbasaur-object",
        (PokemonCard("bw5-1", "Bulbasaur"),),
        retreat_cost=1,
        evolution_eligible=not new_basic,
    )
    return make_state(
        (bulbasaur,),
        active_id="bulbasaur-object",
        evolution_allowed=not first_turn,
    )


def main() -> None:
    matches = [
        profile
        for profile in build_profiles(ROOT / "resources")
        if profile.card_id == "sv7-136"
    ]
    assert len(matches) == 1
    grand_tree = matches[0]
    assert grand_tree.timing_policy == "blocked"
    assert grand_tree.entry_turn_policy == "blocked"

    context = make_grand_tree_context()
    board = make_bulbasaur()
    ivysaur = PokemonCard("bw5-2", "Ivysaur", "Bulbasaur")
    venusaur = PokemonCard("bw5-3", "Venusaur", "Ivysaur")

    # Single activation evolves two stages and consumes no further Stadium
    # play bandwidth, even though it just evolved into the Stage 1.
    two_stage = execute_grand_tree_chain(
        grand_tree,
        context,
        board,
        "bulbasaur-object",
        ivysaur,
        stage1_retreat_cost=2,
        stage2=venusaur,
        stage2_retreat_cost=4,
    )
    assert two_stage is not None
    obj = two_stage.board.get("bulbasaur-object")
    assert [card.name for card in obj.stack] == [
        "Bulbasaur", "Ivysaur", "Venusaur"
    ]
    assert obj.retreat_cost == 4
    assert obj.evolution_eligible is False
    assert two_stage.budget.stadium_plays_used == 1
    assert two_stage.stadium_state is not None
    assert two_stage.stadium_state.used_effect_instances == {
        "grand-tree-entry-1"
    }
    assert context.stadium_state is not None
    assert not context.stadium_state.used_effect_instances

    # One Stage 1 evolution alone is also a valid use of the same effect.
    one_stage = execute_grand_tree_chain(
        grand_tree,
        context,
        board,
        "bulbasaur-object",
        ivysaur,
        stage1_retreat_cost=2,
    )
    assert one_stage is not None
    assert [card.name for card in one_stage.board.get("bulbasaur-object").stack] == [
        "Bulbasaur", "Ivysaur"
    ]

    # The source's one-use allowance belongs to this Stadium instance.
    spent_context = replace(context, stadium_state=two_stage.stadium_state)
    assert execute_grand_tree_chain(
        grand_tree,
        spent_context,
        make_bulbasaur(),
        "bulbasaur-object",
        ivysaur,
        stage1_retreat_cost=2,
        stage2=venusaur,
        stage2_retreat_cost=4,
    ) is None

    # Grand Tree itself forbids the first-turn Basic and newly entered Basic.
    for blocked_board in (
        make_bulbasaur(first_turn=True),
        make_bulbasaur(new_basic=True),
    ):
        assert execute_grand_tree_chain(
            grand_tree,
            context,
            blocked_board,
            "bulbasaur-object",
            ivysaur,
            stage1_retreat_cost=2,
            stage2=venusaur,
            stage2_retreat_cost=4,
        ) is None

    # Invalid target candidates do not partially evolve the caller board or
    # consume its Stadium effect-use allowance.
    bad_stage2 = PokemonCard("bad-candidate", "Blastoise", "Wartortle")
    assert execute_grand_tree_chain(
        grand_tree,
        context,
        board,
        "bulbasaur-object",
        ivysaur,
        stage1_retreat_cost=2,
        stage2=bad_stage2,
        stage2_retreat_cost=3,
    ) is None
    assert len(board.get("bulbasaur-object").stack) == 1
    assert not context.stadium_state.used_effect_instances

    print("Grand Tree one-activation two-stage regressions passed")


if __name__ == "__main__":
    main()
