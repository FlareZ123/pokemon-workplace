from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_kernel import devolve_top
from board_position_state import BoardPokemon, PokemonCard, make_state
from identity_materialization import (
    IdentityLedger, assert_conserved, dematerialize, materialize,
    move_instance, put_in_play_instance, validate_board_position_stack_bindings,
)
from multicopy_zone_state import ZoneCountState


def main():
    initial = IdentityLedger(ZoneCountState.from_mapping({
        ("bulba", "hand"): 1,
        ("ivy", "hand"): 1,
    }))
    ledger = initial
    for cls, name, copy_id in (
        ("bulba", "Bulbasaur", "bulba-copy"),
        ("ivy", "Ivysaur", "ivy-copy"),
    ):
        ledger = materialize(
            ledger, card_class=cls, card_name=name,
            source_zone="hand", instance_id=copy_id,
        )
        ledger = put_in_play_instance(ledger, copy_id, "pokemon-a")

    pokemon = BoardPokemon(
        "pokemon-a",
        (
            PokemonCard("bulba-copy", "Bulbasaur"),
            PokemonCard("ivy-copy", "Ivysaur", "Bulbasaur"),
        ),
        retreat_cost=3,
        evolution_eligible=False,
    )
    board = make_state((pokemon,), active_id="pokemon-a")
    validate_board_position_stack_bindings(ledger, board)

    result = devolve_top(board, "pokemon-a", new_retreat_cost=2)
    assert result is not None
    board, removed = result
    assert removed.card_id == "ivy-copy"
    assert [c.card_id for c in board.get("pokemon-a").stack] == ["bulba-copy"]
    assert not board.get("pokemon-a").evolution_eligible

    ledger = move_instance(ledger, "ivy-copy", "hand")
    ledger = dematerialize(ledger, "ivy-copy")
    validate_board_position_stack_bindings(ledger, board)
    assert_conserved(initial, ledger)
    assert ledger.exchangeable.count("ivy", "hand") == 1

    print("devolution materialization regressions passed")


if __name__ == "__main__":
    main()
