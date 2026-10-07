"""Reproduce atomic multi-Pokemon zone exits with physical conservation."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from batch_zone_exit_conservation import leave_play_batch_before_promotion
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
                ("tarountula", "hand"): 1,
                ("spidops", "hand"): 1,
                ("bidoof", "hand"): 1,
                ("ralts", "hand"): 1,
                ("lechonk", "hand"): 1,
                ("grass-energy", "hand"): 1,
            }
        )
    )

    ledger = initial
    for card_class, card_name, instance_id, pokemon_id in (
        ("tarountula", "Tarountula", "tarountula-copy", "active"),
        ("spidops", "Spidops", "spidops-copy", "active"),
        ("bidoof", "Bidoof", "bidoof-copy", "left"),
        ("ralts", "Ralts", "ralts-copy", "middle"),
        ("lechonk", "Lechonk", "lechonk-copy", "right"),
    ):
        ledger = materialize_in_play(
            ledger,
            card_class=card_class,
            card_name=card_name,
            instance_id=instance_id,
            pokemon_id=pokemon_id,
        )

    board = make_state(
        (
            BoardPokemon(
                "active",
                (
                    PokemonCard("tarountula-copy", "Tarountula"),
                    PokemonCard(
                        "spidops-copy",
                        "Spidops",
                        "Tarountula",
                    ),
                ),
                retreat_cost=1,
            ),
            BoardPokemon(
                "left",
                (PokemonCard("bidoof-copy", "Bidoof"),),
                retreat_cost=1,
            ),
            BoardPokemon(
                "middle",
                (PokemonCard("ralts-copy", "Ralts"),),
                retreat_cost=1,
            ),
            BoardPokemon(
                "right",
                (PokemonCard("lechonk-copy", "Lechonk"),),
                retreat_cost=1,
            ),
        ),
        active_id="active",
    )
    state = StackBoardMaterialState(ledger, board)
    state = attach_from_hand(
        state,
        pokemon_id="active",
        card_class="grass-energy",
        instance_id="grass-copy",
        card_name="Grass Energy",
        kind=AttachmentKind.ENERGY,
        retreat_units=1,
    )
    assert state is not None
    assert_conserved(initial, state.ledger)
    return initial, state


def test_variable_own_board_exit() -> None:
    initial, state = build_state()

    moved = leave_play_batch_before_promotion(
        state,
        ("active", "left", "middle"),
        pokemon_destination="hand",
        attachment_destination="hand",
    )
    assert moved is not None
    assert moved.pokemon_ids == ("active", "left", "middle")
    assert moved.pokemon_card_ids == (
        "tarountula-copy",
        "spidops-copy",
        "bidoof-copy",
        "ralts-copy",
    )
    assert moved.attachment_card_ids == ("grass-copy",)

    pending = moved.state
    assert pending.active_id is None
    assert pending.promotion_candidates == ("right",)

    for card_class in (
        "tarountula",
        "spidops",
        "bidoof",
        "ralts",
        "grass-energy",
    ):
        assert pending.ledger.exchangeable.count(
            card_class,
            "hand",
        ) == 1

    promoted = pending.with_active("right")
    assert promoted is not None
    stable = promoted.to_stack_state()
    assert stable is not None
    assert stable.board is not None
    assert stable.board.active_id == "right"
    assert_conserved(initial, stable.ledger)


def test_bench_batch_preserves_active() -> None:
    initial, state = build_state()

    moved = leave_play_batch_before_promotion(
        state,
        ("left", "middle"),
        pokemon_destination="deck",
        attachment_destination="deck",
    )
    assert moved is not None
    pending = moved.state
    assert pending.active_id == "active"
    assert not pending.requires_promotion

    stable = pending.to_stack_state()
    assert stable is not None
    assert stable.board is not None
    assert stable.board.active_id == "active"
    assert stable.board.bench_ids == ("right",)
    assert stable.ledger.exchangeable.count("bidoof", "deck") == 1
    assert stable.ledger.exchangeable.count("ralts", "deck") == 1
    assert_conserved(initial, stable.ledger)


def test_zero_and_invalid_batches() -> None:
    initial, state = build_state()

    unchanged = leave_play_batch_before_promotion(
        state,
        (),
        pokemon_destination="hand",
        attachment_destination="hand",
    )
    assert unchanged is not None
    assert unchanged.pokemon_ids == ()
    assert unchanged.state.active_id == "active"
    assert unchanged.state.to_stack_state() == state
    assert_conserved(initial, unchanged.state.ledger)

    assert leave_play_batch_before_promotion(
        state,
        ("left", "left"),
        pokemon_destination="hand",
        attachment_destination="hand",
    ) is None

    assert leave_play_batch_before_promotion(
        state,
        ("missing",),
        pokemon_destination="hand",
        attachment_destination="hand",
    ) is None


def main() -> None:
    test_variable_own_board_exit()
    test_bench_batch_preserves_active()
    test_zero_and_invalid_batches()
    print("batch zone-exit conservation regressions passed")


if __name__ == "__main__":
    main()
