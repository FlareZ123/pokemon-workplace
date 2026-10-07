"""Reproduce cross-player promotion ordering after both Active Pokemon are KO'd."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import BoardPokemon, PokemonCard, make_state
from cross_player_knockout_resolution import (
    CrossPlayerKnockOutContext,
    choose_promotion,
    promotion_order,
    resolve_cross_player_knock_out,
)
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from simultaneous_knockout_conservation import prepare_knock_out_batch
from stack_knockout_conservation import StackBoardMaterialState


def make_player(
    prefix: str,
) -> tuple[IdentityLedger, StackBoardMaterialState]:
    active_class = f"{prefix}-active-class"
    bench_class = f"{prefix}-bench-class"
    active_instance = f"{prefix}-active-card"
    bench_instance = f"{prefix}-bench-card"
    active_object = f"{prefix}-active"
    bench_object = f"{prefix}-bench"

    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                (active_class, "hand"): 1,
                (bench_class, "hand"): 1,
            }
        )
    )
    ledger = materialize(
        initial,
        card_class=active_class,
        card_name=f"{prefix} Active Pokemon",
        source_zone="hand",
        instance_id=active_instance,
    )
    ledger = put_in_play_instance(
        ledger,
        active_instance,
        active_object,
    )
    ledger = materialize(
        ledger,
        card_class=bench_class,
        card_name=f"{prefix} Bench Pokemon",
        source_zone="hand",
        instance_id=bench_instance,
    )
    ledger = put_in_play_instance(
        ledger,
        bench_instance,
        bench_object,
    )

    state = StackBoardMaterialState(
        ledger,
        make_state(
            (
                BoardPokemon(
                    active_object,
                    (
                        PokemonCard(
                            active_instance,
                            f"{prefix} Active Pokemon",
                        ),
                    ),
                    retreat_cost=1,
                ),
                BoardPokemon(
                    bench_object,
                    (
                        PokemonCard(
                            bench_instance,
                            f"{prefix} Bench Pokemon",
                        ),
                    ),
                    retreat_cost=1,
                ),
            ),
            active_id=active_object,
        ),
    )
    assert_conserved(initial, state.ledger)
    return initial, state


def main() -> None:
    initial_a, state_a = make_player("a")
    initial_b, state_b = make_player("b")

    pending_a = prepare_knock_out_batch(state_a, ("a-active",))
    pending_b = prepare_knock_out_batch(state_b, ("b-active",))
    assert pending_a is not None
    assert pending_b is not None

    context = CrossPlayerKnockOutContext(
        (
            ("A", pending_a),
            ("B", pending_b),
        ),
        next_player_id="B",
    )

    assert promotion_order(context) == ("B", "A")

    # The player whose turn would not be next cannot promote first.
    assert choose_promotion(
        context,
        player_id="A",
        pokemon_id="a-bench",
    ) is None

    after_b = choose_promotion(
        context,
        player_id="B",
        pokemon_id="b-bench",
    )
    assert after_b is not None

    # A cannot choose B's survivor or a knocked-out Active.
    assert choose_promotion(
        after_b,
        player_id="A",
        pokemon_id="b-bench",
    ) is None
    assert choose_promotion(
        after_b,
        player_id="A",
        pokemon_id="a-active",
    ) is None

    ready = choose_promotion(
        after_b,
        player_id="A",
        pokemon_id="a-bench",
    )
    assert ready is not None

    resolved = resolve_cross_player_knock_out(ready)
    assert resolved is not None

    final_a = resolved.state_for("A")
    final_b = resolved.state_for("B")
    assert final_a.board is not None
    assert final_b.board is not None
    assert final_a.board.active_id == "a-bench"
    assert final_b.board.active_id == "b-bench"

    assert final_a.ledger.exchangeable.count(
        "a-active-class",
        "discard",
    ) == 1
    assert final_b.ledger.exchangeable.count(
        "b-active-class",
        "discard",
    ) == 1
    assert final_a.ledger.instance(
        "a-bench-card"
    ).board_object_id == "a-bench"
    assert final_b.ledger.instance(
        "b-bench-card"
    ).board_object_id == "b-bench"

    assert_conserved(initial_a, final_a.ledger)
    assert_conserved(initial_b, final_b.ledger)

    print("cross-player Knock Out promotion-order regressions passed")


if __name__ == "__main__":
    main()
