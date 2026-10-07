"""Reproduce whole-stack and attachment conservation through Knock Out."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_kernel import normal_evolve
from board_position_state import (
    AttachmentKind,
    BoardPokemon,
    PokemonCard,
    make_state,
)
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from stack_knockout_conservation import (
    StackBoardMaterialState,
    attach_from_hand,
    knock_out_with_conservation,
)


def materialize_in_play(
    ledger: IdentityLedger,
    *,
    card_class: str,
    card_name: str,
    instance_id: str,
    pokemon_id: str,
) -> IdentityLedger:
    ledger = materialize(
        ledger,
        card_class=card_class,
        card_name=card_name,
        source_zone="hand",
        instance_id=instance_id,
    )
    return put_in_play_instance(ledger, instance_id, pokemon_id)


def main() -> None:
    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("bulba-class", "hand"): 1,
                ("ivy-class", "hand"): 1,
                ("bidoof-class", "hand"): 1,
                ("band-class", "hand"): 2,
                ("dce-class", "hand"): 1,
            }
        )
    )

    ledger = materialize_in_play(
        initial,
        card_class="bulba-class",
        card_name="Bulbasaur",
        instance_id="bulba-copy",
        pokemon_id="pokemon-a",
    )
    ledger = materialize_in_play(
        ledger,
        card_class="bidoof-class",
        card_name="Bidoof",
        instance_id="bidoof-copy",
        pokemon_id="pokemon-b",
    )

    board = make_state(
        (
            BoardPokemon(
                "pokemon-a",
                (PokemonCard("bulba-copy", "Bulbasaur"),),
                retreat_cost=2,
            ),
            BoardPokemon(
                "pokemon-b",
                (PokemonCard("bidoof-copy", "Bidoof"),),
                retreat_cost=1,
            ),
        ),
        active_id="pokemon-a",
    )
    state = StackBoardMaterialState(ledger, board)

    ledger = materialize_in_play(
        state.ledger,
        card_class="ivy-class",
        card_name="Ivysaur",
        instance_id="ivy-copy",
        pokemon_id="pokemon-a",
    )
    evolved = normal_evolve(
        state.board,
        "pokemon-a",
        PokemonCard("ivy-copy", "Ivysaur", "Bulbasaur"),
        new_retreat_cost=3,
    )
    assert evolved is not None
    state = StackBoardMaterialState(ledger, evolved.state)
    assert_conserved(initial, state.ledger)

    state = attach_from_hand(
        state,
        pokemon_id="pokemon-a",
        card_class="band-class",
        instance_id="band-a",
        card_name="Muscle Band",
        kind=AttachmentKind.TOOL,
    )
    assert state is not None

    rejected = attach_from_hand(
        state,
        pokemon_id="pokemon-a",
        card_class="band-class",
        instance_id="band-b",
        card_name="Muscle Band",
        kind=AttachmentKind.TOOL,
    )
    assert rejected is None
    assert state.ledger.exchangeable.count("band-class", "hand") == 1

    state = attach_from_hand(
        state,
        pokemon_id="pokemon-a",
        card_class="dce-class",
        instance_id="dce-a",
        card_name="Double Colorless Energy",
        kind=AttachmentKind.ENERGY,
        retreat_units=2,
    )
    assert state is not None
    assert_conserved(initial, state.ledger)

    active = state.board.get("pokemon-a")
    assert [card.card_id for card in active.stack] == [
        "bulba-copy",
        "ivy-copy",
    ]
    assert {card.card_id for card in active.attachments} == {
        "band-a",
        "dce-a",
    }

    knocked_out = knock_out_with_conservation(
        state,
        "pokemon-a",
        promote_id="pokemon-b",
    )
    assert knocked_out is not None
    assert knocked_out.board is not None
    assert knocked_out.board.active_id == "pokemon-b"
    assert knocked_out.board.bench_ids == ()

    for card_class in (
        "bulba-class",
        "ivy-class",
        "band-class",
        "dce-class",
    ):
        assert knocked_out.ledger.exchangeable.count(
            card_class,
            "discard",
        ) == 1

    assert knocked_out.ledger.exchangeable.count(
        "band-class",
        "hand",
    ) == 1
    assert [row.instance_id for row in knocked_out.ledger.instances] == [
        "bidoof-copy"
    ]
    assert knocked_out.ledger.instance(
        "bidoof-copy"
    ).board_object_id == "pokemon-b"
    assert_conserved(initial, knocked_out.ledger)

    terminal = knock_out_with_conservation(
        knocked_out,
        "pokemon-b",
    )
    assert terminal is not None
    assert terminal.board is None
    assert terminal.ledger.instances == ()
    assert terminal.ledger.exchangeable.count(
        "bidoof-class",
        "discard",
    ) == 1
    assert_conserved(initial, terminal.ledger)

    print("stack Knock Out conservation regressions passed")


if __name__ == "__main__":
    main()
