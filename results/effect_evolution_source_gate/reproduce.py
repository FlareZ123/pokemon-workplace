from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT, ROOT / "tools"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from tools.board_position_state import BoardPokemon, PokemonCard, make_state
from tools.effect_evolution_source_gate import (
    SourceActionContext,
    execute_source_gated_evolution,
    source_action_available,
)
from tools.effect_evolution_timing import build_profiles
from tools.lock_state_kernel import PlayerChannels, apply_play_lock
from tools.stadium_effect_instance_usage import (
    StadiumCard,
    StadiumEffectState,
    StadiumInPlay,
)
from tools.turn_action_budget import TurnActionBudget
from tools.turn_attack_window import fresh_turn

PROFILES = build_profiles(ROOT / "resources")


def profile(card_id: str):
    rows = [row for row in PROFILES if row.card_id == card_id]
    assert len(rows) == 1, (card_id, rows)
    return rows[0]


def board_for(name: str, *, first_turn: bool, entered_this_turn: bool = False):
    pokemon = BoardPokemon(
        "pokemon-a",
        (PokemonCard("base-copy", name),),
        retreat_cost=1,
        evolution_eligible=not entered_this_turn,
    )
    return make_state(
        (pokemon,),
        active_id="pokemon-a",
        evolution_allowed=not first_turn,
    )


def main() -> None:
    first_player = SourceActionContext(is_players_first_turn=True, went_first=True)
    second_player = SourceActionContext(is_players_first_turn=True, went_first=False)

    salvatore = profile("sv5-160")
    assert not source_action_available(salvatore, first_player)
    assert source_action_available(salvatore, second_player)

    ivysaur = PokemonCard("ivy-copy", "Ivysaur", "Bulbasaur")
    first_turn_board = board_for("Bulbasaur", first_turn=True)
    assert execute_source_gated_evolution(
        salvatore,
        first_player,
        first_turn_board,
        "pokemon-a",
        ivysaur,
        new_retreat_cost=2,
    ) is None
    salvatore_line = execute_source_gated_evolution(
        salvatore,
        second_player,
        first_turn_board,
        "pokemon-a",
        ivysaur,
        new_retreat_cost=2,
    )
    assert salvatore_line is not None
    assert salvatore_line.budget.supporter_plays_used == 1

    supporter_lock = SourceActionContext(
        is_players_first_turn=True,
        went_first=False,
        channels=apply_play_lock(PlayerChannels(), "supporter"),
    )
    assert not source_action_available(salvatore, supporter_lock)

    spent_supporter = SourceActionContext(
        is_players_first_turn=True,
        went_first=False,
        budget=TurnActionBudget(supporter_plays_used=1),
    )
    assert not source_action_available(salvatore, spent_supporter)

    tm_evolution = profile("sv4-178")
    assert not source_action_available(tm_evolution, first_player)
    assert source_action_available(tm_evolution, second_player)

    exeggcute = profile("sv8-1")
    assert source_action_available(exeggcute, first_player)
    exeggutor = PokemonCard("exeggutor-copy", "Exeggutor", "Exeggcute")
    exeggcute_line = execute_source_gated_evolution(
        exeggcute,
        first_player,
        board_for("Exeggcute", first_turn=True),
        "pokemon-a",
        exeggutor,
        new_retreat_cost=3,
    )
    assert exeggcute_line is not None
    assert exeggcute_line.budget.turn_ended

    closed_attack = SourceActionContext(
        is_players_first_turn=True,
        went_first=True,
        attacks_allowed=False,
    )
    assert not source_action_available(exeggcute, closed_attack)

    eevee = profile("sm1-101")
    assert source_action_available(eevee, first_player)
    ability_lock = SourceActionContext(
        is_players_first_turn=True,
        went_first=True,
        abilities_allowed=False,
    )
    assert not source_action_available(eevee, ability_lock)

    boost_shake = profile("swsh7-142")
    assert source_action_available(boost_shake, first_player)
    item_lock = SourceActionContext(
        is_players_first_turn=True,
        went_first=True,
        channels=apply_play_lock(PlayerChannels(), "item"),
    )
    assert not source_action_available(boost_shake, item_lock)

    grand_tree = profile("sv7-136")
    # Grand Tree must already occupy the Stadium zone for activation.
    assert not source_action_available(grand_tree, first_player)
    grand_tree_state = StadiumEffectState(
        budget=TurnActionBudget(stadium_plays_used=1),
        in_play=StadiumInPlay(
            StadiumCard("grand-tree-copy", "Grand Tree"),
            "grand-tree-instance",
        ),
    )
    spent_play = replace(
        first_player,
        window=fresh_turn(
            action_budget=TurnActionBudget(stadium_plays_used=1)
        ),
        stadium_state=grand_tree_state,
    )
    assert source_action_available(grand_tree, spent_play)
    # Restricting play from hand does not suppress an in-play effect.
    assert source_action_available(
        grand_tree,
        replace(
            spent_play,
            channels=apply_play_lock(PlayerChannels(), "stadium"),
        ),
    )
    assert not source_action_available(
        grand_tree,
        replace(
            spent_play,
            stadium_state=replace(
                grand_tree_state,
                in_play=StadiumInPlay(
                    StadiumCard("different-copy", "Brooklet Hill"),
                    "different-instance",
                ),
            ),
        ),
    )

    # Grand Tree itself forbids evolving on the player's first turn.
    venusaur = PokemonCard("venusaur-copy", "Venusaur", "Bulbasaur")
    assert execute_source_gated_evolution(
        grand_tree,
        spent_play,
        board_for("Bulbasaur", first_turn=True),
        "pokemon-a",
        venusaur,
        new_retreat_cost=3,
    ) is None
    assert not grand_tree_state.used_effect_instances

    ivysaur_line = execute_source_gated_evolution(
        grand_tree,
        spent_play,
        board_for("Bulbasaur", first_turn=False),
        "pokemon-a",
        ivysaur,
        new_retreat_cost=2,
    )
    assert ivysaur_line is not None
    assert ivysaur_line.budget.stadium_plays_used == 1
    assert ivysaur_line.stadium_state is not None
    assert ivysaur_line.stadium_state.used_effect_instances == {
        "grand-tree-instance"
    }
    assert not source_action_available(
        grand_tree,
        replace(spent_play, stadium_state=ivysaur_line.stadium_state),
    )

    # A second in-play copy has separate effect-use history.
    another_grand_tree = replace(
        ivysaur_line.stadium_state,
        in_play=StadiumInPlay(
            StadiumCard("second-grand-tree-copy", "Grand Tree"),
            "second-grand-tree-instance",
        ),
    )
    assert source_action_available(
        grand_tree,
        replace(spent_play, stadium_state=another_grand_tree),
    )

    mismatch = execute_source_gated_evolution(
        salvatore,
        second_player,
        first_turn_board,
        "pokemon-a",
        PokemonCard("wrong-copy", "Ivysaur", "Pikachu"),
        new_retreat_cost=2,
    )
    assert mismatch is None
    assert second_player.budget.supporter_plays_used == 0

    print("effect evolution source-gate regressions passed")


if __name__ == "__main__":
    main()
