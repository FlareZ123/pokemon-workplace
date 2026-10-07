"""Reproduce whole-stack zone exits with independent attachment routing."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

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
)
from stack_zone_exit_conservation import leave_play_with_conservation


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


def build_state() -> tuple[IdentityLedger, StackBoardMaterialState]:
    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("bulba-class", "hand"): 1,
                ("ivy-class", "hand"): 1,
                ("bidoof-class", "hand"): 1,
                ("band-class", "hand"): 1,
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
        card_class="ivy-class",
        card_name="Ivysaur",
        instance_id="ivy-copy",
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
                (
                    PokemonCard("bulba-copy", "Bulbasaur"),
                    PokemonCard("ivy-copy", "Ivysaur", "Bulbasaur"),
                ),
                retreat_cost=2,
                damage_counters=7,
                special_conditions=frozenset({"Poisoned"}),
                evolution_eligible=False,
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

    state = attach_from_hand(
        state,
        pokemon_id="pokemon-a",
        card_class="band-class",
        instance_id="band-copy",
        card_name="Muscle Band",
        kind=AttachmentKind.TOOL,
    )
    assert state is not None

    state = attach_from_hand(
        state,
        pokemon_id="pokemon-a",
        card_class="dce-class",
        instance_id="dce-copy",
        card_name="Double Colorless Energy",
        kind=AttachmentKind.ENERGY,
        retreat_units=2,
    )
    assert state is not None
    assert_conserved(initial, state.ledger)
    return initial, state


def assert_zone_count(
    state: StackBoardMaterialState,
    card_class: str,
    zone: str,
    count: int,
) -> None:
    assert state.ledger.exchangeable.count(card_class, zone) == count


def test_scoop_up_cyclone_style() -> StackBoardMaterialState:
    initial, state = build_state()
    moved = leave_play_with_conservation(
        state,
        "pokemon-a",
        pokemon_destination="hand",
        attachment_destination="hand",
        promote_id="pokemon-b",
    )
    assert moved is not None
    assert moved.pokemon_card_ids == ("bulba-copy", "ivy-copy")
    assert moved.attachment_card_ids == ("band-copy", "dce-copy")

    next_state = moved.state
    assert next_state.board is not None
    assert next_state.board.active_id == "pokemon-b"
    assert next_state.board.bench_ids == ()
    for card_class in ("bulba-class", "ivy-class", "band-class", "dce-class"):
        assert_zone_count(next_state, card_class, "hand", 1)

    assert tuple(row.instance_id for row in next_state.ledger.instances) == (
        "bidoof-copy",
    )
    assert_conserved(initial, next_state.ledger)
    return next_state


def test_az_style() -> None:
    initial, state = build_state()
    moved = leave_play_with_conservation(
        state,
        "pokemon-a",
        pokemon_destination="hand",
        attachment_destination="discard",
        promote_id="pokemon-b",
    )
    assert moved is not None
    next_state = moved.state

    for card_class in ("bulba-class", "ivy-class"):
        assert_zone_count(next_state, card_class, "hand", 1)
    for card_class in ("band-class", "dce-class"):
        assert_zone_count(next_state, card_class, "discard", 1)
    assert_conserved(initial, next_state.ledger)


def test_cassius_style() -> None:
    initial, state = build_state()
    moved = leave_play_with_conservation(
        state,
        "pokemon-a",
        pokemon_destination="deck",
        attachment_destination="deck",
        promote_id="pokemon-b",
    )
    assert moved is not None
    next_state = moved.state

    for card_class in ("bulba-class", "ivy-class", "band-class", "dce-class"):
        assert_zone_count(next_state, card_class, "deck", 1)
    assert_conserved(initial, next_state.ledger)


def test_deferred_dematerialization() -> None:
    initial, state = build_state()
    moved = leave_play_with_conservation(
        state,
        "pokemon-a",
        pokemon_destination="hand",
        attachment_destination="hand",
        promote_id="pokemon-b",
        preserve_identity=True,
    )
    assert moved is not None

    for instance_id in ("bulba-copy", "ivy-copy", "band-copy", "dce-copy"):
        row = moved.state.ledger.instance(instance_id)
        assert row.zone == "hand"
        assert row.board_object_id is None
        assert row.attached_to is None

    assert_conserved(initial, moved.state.ledger)


def test_bench_exit_and_terminal_exit() -> None:
    initial, state = build_state()

    benched = leave_play_with_conservation(
        state,
        "pokemon-b",
        pokemon_destination="hand",
        attachment_destination="hand",
    )
    assert benched is not None
    assert benched.state.board is not None
    assert benched.state.board.active_id == "pokemon-a"
    assert benched.state.board.bench_ids == ()
    assert_zone_count(benched.state, "bidoof-class", "hand", 1)
    assert_conserved(initial, benched.state.ledger)

    promoted_only = test_scoop_up_cyclone_style()
    terminal = leave_play_with_conservation(
        promoted_only,
        "pokemon-b",
        pokemon_destination="hand",
        attachment_destination="hand",
    )
    assert terminal is not None
    assert terminal.state.board is None
    assert_zone_count(terminal.state, "bidoof-class", "hand", 1)


def test_rejections() -> None:
    _, state = build_state()

    missing_promotion = leave_play_with_conservation(
        state,
        "pokemon-a",
        pokemon_destination="hand",
        attachment_destination="hand",
    )
    assert missing_promotion is None

    wrong_promotion = leave_play_with_conservation(
        state,
        "pokemon-a",
        pokemon_destination="hand",
        attachment_destination="hand",
        promote_id="pokemon-a",
    )
    assert wrong_promotion is None

    try:
        leave_play_with_conservation(
            state,
            "pokemon-a",
            pokemon_destination="in_play",
            attachment_destination="hand",
            promote_id="pokemon-b",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("board relation zone was accepted as an exit destination")


def main() -> None:
    test_scoop_up_cyclone_style()
    test_az_style()
    test_cassius_style()
    test_deferred_dematerialization()
    test_bench_exit_and_terminal_exit()
    test_rejections()
    print("stack zone exit conservation regressions passed")


if __name__ == "__main__":
    main()
