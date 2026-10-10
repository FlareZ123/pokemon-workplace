"""Grand Tree can search only deck cards; preserve two-stage identities."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for location in (ROOT, ROOT / "tools"):
    if str(location) not in sys.path:
        sys.path.insert(0, str(location))

from tools.board_position_state import BoardPokemon, PokemonCard, make_state
from tools.effect_evolution_source_gate import SourceActionContext
from tools.effect_evolution_timing import build_profiles
from tools.grand_tree_materialized_chain import materialized_grand_tree_chain
from tools.identity_materialization import (
    IdentityLedger,
    materialize,
    put_in_play_instance,
    validate_board_position_stack_bindings,
)
from tools.multicopy_zone_state import ZoneCountState
from tools.stadium_effect_instance_usage import StadiumCard, StadiumEffectState, StadiumInPlay
from tools.turn_attack_window import fresh_turn
from turn_action_budget import TurnActionBudget


GRAND_TREE = next(
    row for row in build_profiles(ROOT / "resources")
    if row.card_id == "sv7-136"
)


def setup(*, ivysaur_zone: str = "deck", venusaur_zone: str = "deck"):
    deck = IdentityLedger(
        ZoneCountState.from_mapping({
            ("Bulbasaur", "hand"): 1,
            ("Ivysaur", ivysaur_zone): 1,
            ("Venusaur", venusaur_zone): 1,
        })
    )
    ledger = materialize(
        deck, card_class="Bulbasaur", card_name="Bulbasaur",
        source_zone="hand", instance_id="bw5-1",
    )
    ledger = put_in_play_instance(ledger, "bw5-1", "pokemon-a")
    basic = BoardPokemon(
        "pokemon-a",
        (PokemonCard("bw5-1", "Bulbasaur"),),
        retreat_cost=1,
        evolution_eligible=True,
    )
    board = make_state(
        (basic,), active_id="pokemon-a", evolution_allowed=True,
    )
    validate_board_position_stack_bindings(ledger, board)

    budget = TurnActionBudget(stadium_plays_used=1)
    stadium = StadiumEffectState(
        budget=budget,
        in_play=StadiumInPlay(
            StadiumCard("stadium-copy-1", "Grand Tree"),
            "stadium-entry-1",
        ),
    )
    context = SourceActionContext(
        is_players_first_turn=False,
        went_first=True,
        window=fresh_turn(action_budget=budget),
        stadium_state=stadium,
    )
    return ledger, board, context


def invoke(ledger, board, context, *, stage2: bool):
    return materialized_grand_tree_chain(
        GRAND_TREE, context, ledger, board, "pokemon-a",
        PokemonCard("bw5-2", "Ivysaur", "Bulbasaur"),
        stage1_class="Ivysaur",
        stage1_retreat_cost=2,
        stage2=PokemonCard("bw5-3", "Venusaur", "Ivysaur") if stage2 else None,
        stage2_class="Venusaur" if stage2 else None,
        stage2_retreat_cost=4 if stage2 else None,
    )


def main() -> None:
    ledger, board, context = setup()
    result = invoke(ledger, board, context, stage2=True)
    assert result is not None
    validate_board_position_stack_bindings(result.ledger, result.evolution.board)
    assert result.ledger.totals() == ledger.totals()
    assert [
        card.card_id for card in result.evolution.board.get("pokemon-a").stack
    ] == ["bw5-1", "bw5-2", "bw5-3"]
    for instance_id in ("bw5-1", "bw5-2", "bw5-3"):
        card = result.ledger.instance(instance_id)
        assert card.zone == "in_play"
        assert card.board_object_id == "pokemon-a"
    assert result.ledger.exchangeable.count("Ivysaur", "deck") == 0
    assert result.ledger.exchangeable.count("Venusaur", "deck") == 0
    assert result.evolution.budget.stadium_plays_used == 1
    assert result.evolution.stadium_state is not None
    assert result.evolution.stadium_state.used_effect_instances == {"stadium-entry-1"}
    assert not context.stadium_state.used_effect_instances

    # A Prized Stage 2 cannot be searched from deck. Requesting it is an
    # impossible candidate, but choosing Stage 1 alone remains legal.
    prized_ledger, prized_board, prized_context = setup(venusaur_zone="prize")
    assert invoke(prized_ledger, prized_board, prized_context, stage2=True) is None
    assert prized_ledger.exchangeable.count("Ivysaur", "deck") == 1
    assert prized_ledger.exchangeable.count("Venusaur", "prize") == 1
    assert not prized_context.stadium_state.used_effect_instances
    stage1_only = invoke(prized_ledger, prized_board, prized_context, stage2=False)
    assert stage1_only is not None
    assert len(stage1_only.evolution.board.get("pokemon-a").stack) == 2
    assert stage1_only.ledger.exchangeable.count("Venusaur", "prize") == 1
    assert stage1_only.ledger.totals() == prized_ledger.totals()

    # A Prized Stage 1 closes the search, regardless of where Stage 2 sits.
    missing_stage1, blocked_board, blocked_context = setup(ivysaur_zone="prize")
    assert invoke(missing_stage1, blocked_board, blocked_context, stage2=True) is None
    assert invoke(missing_stage1, blocked_board, blocked_context, stage2=False) is None
    assert len(blocked_board.get("pokemon-a").stack) == 1
    assert not blocked_context.stadium_state.used_effect_instances

    # Selecting an invalid Stage 2 chain also rolls back all staged changes.
    wrong = materialized_grand_tree_chain(
        GRAND_TREE, context, ledger, board, "pokemon-a",
        PokemonCard("bw5-2", "Ivysaur", "Bulbasaur"),
        stage1_class="Ivysaur",
        stage1_retreat_cost=2,
        stage2=PokemonCard("wrong", "Blastoise", "Wartortle"),
        stage2_class="Venusaur",
        stage2_retreat_cost=3,
    )
    assert wrong is None
    assert len(board.get("pokemon-a").stack) == 1
    assert ledger.exchangeable.count("Ivysaur", "deck") == 1

    print("Grand Tree physical-deck and Prize collapse regressions passed")


if __name__ == "__main__":
    main()
