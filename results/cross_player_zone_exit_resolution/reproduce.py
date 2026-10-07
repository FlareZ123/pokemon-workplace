"""Reproduce simultaneous Active zone exits and effect-defined promotion order."""

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
from cross_player_zone_exit_resolution import (
    ZoneExitStage,
    advance_after_exit,
    choose_promotion,
    finalize_promotions,
    next_promotion_player,
    prepare_simultaneous_active_exit,
    promotion_order,
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


def build_player_a() -> tuple[IdentityLedger, StackBoardMaterialState]:
    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("tarountula", "hand"): 1,
                ("spidops", "hand"): 1,
                ("lechonk", "hand"): 1,
                ("ralts", "hand"): 1,
                ("grass-energy", "hand"): 1,
            }
        )
    )
    ledger = initial
    for card_class, card_name, instance_id, pokemon_id in (
        ("tarountula", "Tarountula", "a-tarountula", "a-active"),
        ("spidops", "Spidops", "a-spidops", "a-active"),
        ("lechonk", "Lechonk", "a-lechonk", "a-left"),
        ("ralts", "Ralts", "a-ralts", "a-right"),
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
                "a-active",
                (
                    PokemonCard("a-tarountula", "Tarountula"),
                    PokemonCard("a-spidops", "Spidops", "Tarountula"),
                ),
                retreat_cost=1,
            ),
            BoardPokemon(
                "a-left",
                (PokemonCard("a-lechonk", "Lechonk"),),
                retreat_cost=2,
            ),
            BoardPokemon(
                "a-right",
                (PokemonCard("a-ralts", "Ralts"),),
                retreat_cost=1,
            ),
        ),
        active_id="a-active",
    )
    state = StackBoardMaterialState(ledger, board)
    state = attach_from_hand(
        state,
        pokemon_id="a-active",
        card_class="grass-energy",
        instance_id="a-grass",
        card_name="Grass Energy",
        kind=AttachmentKind.ENERGY,
        retreat_units=1,
    )
    assert state is not None
    assert_conserved(initial, state.ledger)
    return initial, state


def build_player_b(
    *,
    with_bench: bool = True,
) -> tuple[IdentityLedger, StackBoardMaterialState]:
    counts = {
        ("charmander", "hand"): 1,
    }
    if with_bench:
        counts.update(
            {
                ("squirtle", "hand"): 1,
                ("bulbasaur", "hand"): 1,
            }
        )

    initial = IdentityLedger(ZoneCountState.from_mapping(counts))
    ledger = materialize_in_play(
        initial,
        card_class="charmander",
        card_name="Charmander",
        instance_id="b-charmander",
        pokemon_id="b-active",
    )

    pokemon = [
        BoardPokemon(
            "b-active",
            (PokemonCard("b-charmander", "Charmander"),),
            retreat_cost=1,
        )
    ]
    if with_bench:
        for card_class, card_name, instance_id, pokemon_id in (
            ("squirtle", "Squirtle", "b-squirtle", "b-left"),
            ("bulbasaur", "Bulbasaur", "b-bulbasaur", "b-right"),
        ):
            ledger = materialize_in_play(
                ledger,
                card_class=card_class,
                card_name=card_name,
                instance_id=instance_id,
                pokemon_id=pokemon_id,
            )
            pokemon.append(
                BoardPokemon(
                    pokemon_id,
                    (PokemonCard(instance_id, card_name),),
                    retreat_cost=1,
                )
            )

    board = make_state(tuple(pokemon), active_id="b-active")
    state = StackBoardMaterialState(ledger, board)
    assert_conserved(initial, state.ledger)
    return initial, state


def test_entangling_trap_order() -> None:
    initial_a, state_a = build_player_a()
    initial_b, state_b = build_player_b()

    context = prepare_simultaneous_active_exit(
        (("A", state_a), ("B", state_b)),
        pokemon_destination="deck",
        attachment_destination="deck",
        first_player_id="A",
    )
    assert context is not None
    assert context.stage == ZoneExitStage.AFTER_EXIT

    pending_a = context.state_for("A")
    pending_b = context.state_for("B")
    assert pending_a.active_id is None
    assert pending_b.active_id is None
    assert pending_a.promotion_candidates == ("a-left", "a-right")
    assert pending_b.promotion_candidates == ("b-left", "b-right")

    assert pending_a.ledger.exchangeable.count("tarountula", "deck") == 1
    assert pending_a.ledger.exchangeable.count("spidops", "deck") == 1
    assert pending_a.ledger.exchangeable.count("grass-energy", "deck") == 1
    assert pending_b.ledger.exchangeable.count("charmander", "deck") == 1

    assert next_promotion_player(context) is None
    assert choose_promotion(
        context,
        player_id="A",
        pokemon_id="a-left",
    ) is None

    context = advance_after_exit(context, game_continues=True)
    assert context is not None
    assert context.stage == ZoneExitStage.PROMOTION
    assert promotion_order(context) == ("A", "B")
    assert next_promotion_player(context) == "A"

    assert choose_promotion(
        context,
        player_id="B",
        pokemon_id="b-left",
    ) is None

    context = choose_promotion(
        context,
        player_id="A",
        pokemon_id="a-right",
    )
    assert context is not None
    assert context.state_for("A").active_id == "a-right"
    assert next_promotion_player(context) == "B"

    context = choose_promotion(
        context,
        player_id="B",
        pokemon_id="b-left",
    )
    assert context is not None
    assert context.state_for("B").active_id == "b-left"
    assert next_promotion_player(context) is None

    resolved = finalize_promotions(context)
    assert resolved is not None
    resolved_map = dict(resolved)
    assert resolved_map["A"].board is not None
    assert resolved_map["B"].board is not None
    assert resolved_map["A"].board.active_id == "a-right"
    assert resolved_map["B"].board.active_id == "b-left"
    assert_conserved(initial_a, resolved_map["A"].ledger)
    assert_conserved(initial_b, resolved_map["B"].ledger)


def test_terminal_gate() -> None:
    _, state_a = build_player_a()
    _, state_b = build_player_b(with_bench=False)

    context = prepare_simultaneous_active_exit(
        (("A", state_a), ("B", state_b)),
        pokemon_destination="deck",
        attachment_destination="deck",
        first_player_id="A",
    )
    assert context is not None
    assert context.state_for("B").pokemon == ()
    assert not context.state_for("B").requires_promotion

    terminal = advance_after_exit(context, game_continues=False)
    assert terminal is not None
    assert terminal.stage == ZoneExitStage.TERMINAL
    assert next_promotion_player(terminal) is None
    assert finalize_promotions(terminal) is None


def main() -> None:
    test_entangling_trap_order()
    test_terminal_gate()
    print("cross-player zone-exit resolution regressions passed")


if __name__ == "__main__":
    main()
