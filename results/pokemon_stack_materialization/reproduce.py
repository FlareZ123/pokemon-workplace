"""Check materialized Pokemon-card identity across ordinary evolution."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_kernel import normal_evolve
from board_position_state import BoardPokemon, PokemonCard, make_state
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
    validate_board_position_stack_bindings,
)
from multicopy_zone_state import ZoneCountState


def main():
    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("bulba-class", "hand"): 1,
                ("ivy-class", "hand"): 1,
            }
        )
    )

    ledger = materialize(
        initial,
        card_class="bulba-class",
        card_name="Bulbasaur",
        source_zone="hand",
        instance_id="bulba-copy",
    )
    ledger = put_in_play_instance(ledger, "bulba-copy", "pokemon-a")

    bulba = BoardPokemon(
        "pokemon-a",
        (PokemonCard("bulba-copy", "Bulbasaur"),),
        retreat_cost=2,
    )
    board = make_state((bulba,), active_id="pokemon-a")
    validate_board_position_stack_bindings(ledger, board)

    before_evolution = ledger
    ledger = materialize(
        ledger,
        card_class="ivy-class",
        card_name="Ivysaur",
        source_zone="hand",
        instance_id="ivy-copy",
    )
    ledger = put_in_play_instance(ledger, "ivy-copy", "pokemon-a")

    evolved = normal_evolve(
        board,
        "pokemon-a",
        PokemonCard("ivy-copy", "Ivysaur", "Bulbasaur"),
        new_retreat_cost=3,
    )
    assert evolved is not None
    validate_board_position_stack_bindings(ledger, evolved.state)
    assert_conserved(initial, ledger)

    stack = evolved.state.get("pokemon-a").stack
    assert [card.card_id for card in stack] == ["bulba-copy", "ivy-copy"]
    assert [card.name for card in stack] == ["Bulbasaur", "Ivysaur"]
    assert ledger.instance("bulba-copy").board_object_id == "pokemon-a"
    assert ledger.instance("ivy-copy").board_object_id == "pokemon-a"

    wrong = put_in_play_instance(
        materialize(
            before_evolution,
            card_class="ivy-class",
            card_name="Ivysaur",
            source_zone="hand",
            instance_id="wrong-ivy",
        ),
        "wrong-ivy",
        "pokemon-a",
    )
    try:
        validate_board_position_stack_bindings(wrong, evolved.state)
    except ValueError:
        pass
    else:
        raise AssertionError("mismatched evolution-card instance was accepted")

    print("Pokemon stack materialization regressions passed")


if __name__ == "__main__":
    main()
