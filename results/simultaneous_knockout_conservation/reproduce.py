"""Reproduce simultaneous Knock Out conservation and survivor-only promotion."""

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
from simultaneous_knockout_conservation import (
    discard_pending_knock_out_batch,
    prepare_knock_out_batch,
)
from stack_knockout_conservation import (
    StackBoardMaterialState,
    attach_from_hand,
)


def put_pokemon(
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
                ("bulba", "hand"): 1,
                ("ivy", "hand"): 1,
                ("bidoof", "hand"): 1,
                ("squirtle", "hand"): 1,
                ("dce", "hand"): 1,
                ("band", "hand"): 1,
            }
        )
    )

    ledger = initial
    for card_class, card_name, instance_id, pokemon_id in (
        ("bulba", "Bulbasaur", "bulba-a", "a"),
        ("bidoof", "Bidoof", "bidoof-b", "b"),
        ("squirtle", "Squirtle", "squirtle-c", "c"),
    ):
        ledger = put_pokemon(
            ledger,
            card_class=card_class,
            card_name=card_name,
            instance_id=instance_id,
            pokemon_id=pokemon_id,
        )

    board = make_state(
        (
            BoardPokemon(
                "a",
                (PokemonCard("bulba-a", "Bulbasaur"),),
                retreat_cost=2,
            ),
            BoardPokemon(
                "b",
                (PokemonCard("bidoof-b", "Bidoof"),),
                retreat_cost=1,
            ),
            BoardPokemon(
                "c",
                (PokemonCard("squirtle-c", "Squirtle"),),
                retreat_cost=1,
            ),
        ),
        active_id="a",
    )
    state = StackBoardMaterialState(ledger, board)

    ledger = put_pokemon(
        state.ledger,
        card_class="ivy",
        card_name="Ivysaur",
        instance_id="ivy-a",
        pokemon_id="a",
    )
    evolved = normal_evolve(
        state.board,
        "a",
        PokemonCard("ivy-a", "Ivysaur", "Bulbasaur"),
        new_retreat_cost=3,
    )
    assert evolved is not None
    state = StackBoardMaterialState(ledger, evolved.state)

    state = attach_from_hand(
        state,
        pokemon_id="a",
        card_class="dce",
        instance_id="dce-a",
        card_name="Double Colorless Energy",
        kind=AttachmentKind.ENERGY,
        retreat_units=2,
    )
    assert state is not None
    state = attach_from_hand(
        state,
        pokemon_id="b",
        card_class="band",
        instance_id="band-b",
        card_name="Muscle Band",
        kind=AttachmentKind.TOOL,
    )
    assert state is not None
    assert_conserved(initial, state.ledger)

    pending = prepare_knock_out_batch(state, ("a", "b"))
    assert pending is not None

    # The pre-discard trigger phase still sees every knocked-out object and card.
    assert pending.state == state
    assert pending.state.board is not None
    assert {p.pokemon_id for p in pending.state.board.pokemon} == {"a", "b", "c"}
    assert [card.card_id for card in pending.state.board.get("a").stack] == [
        "bulba-a",
        "ivy-a",
    ]
    assert pending.state.board.get("b").attachments[0].card_id == "band-b"

    # Sequentially promoting B after A's KO would be illegal because B belongs
    # to the same simultaneous KO batch.
    assert discard_pending_knock_out_batch(
        pending,
        promote_id="b",
    ) is None

    resolved = discard_pending_knock_out_batch(
        pending,
        promote_id="c",
    )
    assert resolved is not None
    assert resolved.board is not None
    assert resolved.board.active_id == "c"
    assert resolved.board.bench_ids == ()
    assert [row.instance_id for row in resolved.ledger.instances] == [
        "squirtle-c"
    ]

    for card_class in ("bulba", "ivy", "bidoof", "dce", "band"):
        assert resolved.ledger.exchangeable.count(
            card_class,
            "discard",
        ) == 1
    assert resolved.ledger.instance(
        "squirtle-c"
    ).board_object_id == "c"
    assert_conserved(initial, resolved.ledger)

    # A later terminal batch can dispose the final survivor cleanly.
    final_pending = prepare_knock_out_batch(resolved, ("c",))
    assert final_pending is not None
    terminal = discard_pending_knock_out_batch(final_pending)
    assert terminal is not None
    assert terminal.board is None
    assert terminal.ledger.instances == ()
    assert terminal.ledger.exchangeable.count("squirtle", "discard") == 1
    assert_conserved(initial, terminal.ledger)

    print("simultaneous Knock Out conservation regressions passed")


if __name__ == "__main__":
    main()
