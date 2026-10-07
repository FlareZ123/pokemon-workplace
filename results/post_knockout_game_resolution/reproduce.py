"""Reproduce post-Knock-Out Prize and game-resolution mechanics."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import BoardPokemon, PokemonCard, make_state
from identity_materialization import IdentityLedger, materialize, put_in_play_instance
from knockout_phase_resolution import PlayerKnockOutBatch, TwoPlayerKnockOutPhase
from multicopy_zone_state import ZoneCountState
from post_knockout_game_resolution import (
    Outcome,
    resolve_post_knockout,
    resolve_prize_and_board_loss_conditions,
    resolve_start_of_turn_deck_out,
    resolve_tiebreaker_progress,
)
from simultaneous_knockout_conservation import prepare_knock_out_batch
from stack_knockout_conservation import StackBoardMaterialState


def build_side(prefix: str, *, bench_count: int) -> StackBoardMaterialState:
    counts = {(f"{prefix}-active-class", "hand"): 1}
    for index in range(bench_count):
        counts[(f"{prefix}-bench-{index}-class", "hand")] = 1
    ledger = IdentityLedger(ZoneCountState.from_mapping(counts))

    def put(
        current: IdentityLedger,
        *,
        card_class: str,
        name: str,
        instance_id: str,
        pokemon_id: str,
    ) -> IdentityLedger:
        current = materialize(
            current,
            card_class=card_class,
            card_name=name,
            source_zone="hand",
            instance_id=instance_id,
        )
        return put_in_play_instance(current, instance_id, pokemon_id)

    ledger = put(
        ledger,
        card_class=f"{prefix}-active-class",
        name=f"{prefix} Active",
        instance_id=f"{prefix}-active-copy",
        pokemon_id=f"{prefix}-active",
    )
    pokemon = [
        BoardPokemon(
            f"{prefix}-active",
            (PokemonCard(f"{prefix}-active-copy", f"{prefix} Active"),),
            retreat_cost=1,
        )
    ]
    for index in range(bench_count):
        pokemon_id = f"{prefix}-bench-{index}"
        instance_id = f"{prefix}-bench-{index}-copy"
        ledger = put(
            ledger,
            card_class=f"{prefix}-bench-{index}-class",
            name=f"{prefix} Bench {index}",
            instance_id=instance_id,
            pokemon_id=pokemon_id,
        )
        pokemon.append(
            BoardPokemon(
                pokemon_id,
                (PokemonCard(instance_id, f"{prefix} Bench {index}"),),
                retreat_cost=1,
            )
        )

    return StackBoardMaterialState(
        ledger,
        make_state(pokemon, active_id=f"{prefix}-active"),
    )


def check_rulebook_table() -> None:
    # Columns are: A took all Prizes, B took all Prizes,
    # A has no Pokemon, B has no Pokemon, result for A.
    rows = (
        (True, False, True, False, Outcome.TIE),
        (False, True, False, True, Outcome.TIE),
        (True, True, True, True, Outcome.TIE),
        (True, True, False, False, Outcome.TIE),
        (False, False, True, True, Outcome.TIE),
        (True, True, False, True, Outcome.WIN),
        (True, False, True, True, Outcome.WIN),
        (True, False, False, True, Outcome.WIN),
        (True, True, True, False, Outcome.LOSS),
        (False, True, True, True, Outcome.LOSS),
        (False, True, True, False, Outcome.LOSS),
    )
    for a_took_all, b_took_all, a_empty, b_empty, expected in rows:
        result = resolve_prize_and_board_loss_conditions(
            player_ids=("A", "B"),
            prizes_remaining={
                "A": 0 if a_took_all else 1,
                "B": 0 if b_took_all else 1,
            },
            pokemon_in_play={
                "A": 0 if a_empty else 1,
                "B": 0 if b_empty else 1,
            },
        )
        assert result.outcome("A") == expected
        if expected == Outcome.WIN:
            assert result.outcome("B") == Outcome.LOSS
        elif expected == Outcome.LOSS:
            assert result.outcome("B") == Outcome.WIN
        else:
            assert result.outcome("B") == Outcome.TIE

    single_condition_rows = (
        (0, 1, 1, 1, Outcome.WIN),
        (1, 0, 1, 1, Outcome.LOSS),
        (1, 1, 0, 1, Outcome.LOSS),
        (1, 1, 1, 0, Outcome.WIN),
    )
    for a_prizes, b_prizes, a_pokemon, b_pokemon, expected in single_condition_rows:
        result = resolve_prize_and_board_loss_conditions(
            player_ids=("A", "B"),
            prizes_remaining={"A": a_prizes, "B": b_prizes},
            pokemon_in_play={"A": a_pokemon, "B": b_pokemon},
        )
        assert result.outcome("A") == expected

    ongoing = resolve_prize_and_board_loss_conditions(
        player_ids=("A", "B"),
        prizes_remaining={"A": 2, "B": 3},
        pokemon_in_play={"A": 2, "B": 1},
    )
    assert not ongoing.terminal


def check_post_knockout_composition() -> None:
    # A loses its only Pokemon but also takes its last Prize. B survives.
    # Each side fulfills one loss condition, so the result is a tie.
    state_a = build_side("a", bench_count=0)
    state_b = build_side("b", bench_count=1)
    pending_a = prepare_knock_out_batch(state_a, ("a-active",))
    pending_b = prepare_knock_out_batch(state_b, ("b-active",))
    assert pending_a is not None
    assert pending_b is not None
    phase = TwoPlayerKnockOutPhase(
        (
            PlayerKnockOutBatch("A", pending_a),
            PlayerKnockOutBatch("B", pending_b),
        ),
        current_turn_player="A",
        next_turn_player="B",
    )
    tied = resolve_post_knockout(
        phase,
        prizes_remaining_before={"A": 1, "B": 3},
        prize_awards={"A": 2, "B": 0},
    )
    assert tied.player("A").prizes_taken == 1
    assert tied.player("A").prizes_remaining == 0
    assert tied.player("A").surviving_pokemon == 0
    assert tied.player("B").surviving_pokemon == 1
    assert tied.resolution.outcome("A") == Outcome.TIE
    assert tied.resolution.outcome("B") == Outcome.TIE

    # Both players take their final Prize, and B also loses its only Pokemon.
    # A fulfills one loss condition, while B fulfills two, so A wins.
    terminal_b = build_side("c", bench_count=0)
    pending_terminal_b = prepare_knock_out_batch(terminal_b, ("c-active",))
    assert pending_terminal_b is not None
    state_a_survives = build_side("d", bench_count=1)
    pending_a_survives = prepare_knock_out_batch(
        state_a_survives,
        ("d-active",),
    )
    assert pending_a_survives is not None
    phase2 = TwoPlayerKnockOutPhase(
        (
            PlayerKnockOutBatch("A", pending_a_survives),
            PlayerKnockOutBatch("B", pending_terminal_b),
        ),
        current_turn_player="A",
        next_turn_player="B",
    )
    won = resolve_post_knockout(
        phase2,
        prizes_remaining_before={"A": 1, "B": 1},
        prize_awards={"A": 1, "B": 1},
    )
    assert won.resolution.loss_count("A") == 1
    assert won.resolution.loss_count("B") == 2
    assert won.resolution.outcome("A") == Outcome.WIN
    assert won.resolution.outcome("B") == Outcome.LOSS


def check_other_game_resolution_rules() -> None:
    deck_out = resolve_start_of_turn_deck_out(
        player_ids=("A", "B"),
        current_turn_player="A",
        current_turn_player_could_draw=False,
    )
    assert deck_out.outcome("A") == Outcome.LOSS
    assert deck_out.outcome("B") == Outcome.WIN

    can_draw = resolve_start_of_turn_deck_out(
        player_ids=("A", "B"),
        current_turn_player="A",
        current_turn_player_could_draw=True,
    )
    assert not can_draw.terminal

    tied = resolve_tiebreaker_progress(
        player_ids=("A", "B"),
        prizes_remaining={"A": 6, "B": 6},
    )
    assert not tied.terminal
    a_ahead = resolve_tiebreaker_progress(
        player_ids=("A", "B"),
        prizes_remaining={"A": 5, "B": 6},
    )
    assert a_ahead.outcome("A") == Outcome.WIN
    assert a_ahead.outcome("B") == Outcome.LOSS


def main() -> None:
    check_rulebook_table()
    check_post_knockout_composition()
    check_other_game_resolution_rules()
    print("post-Knock-Out game-resolution regressions passed")


if __name__ == "__main__":
    main()
