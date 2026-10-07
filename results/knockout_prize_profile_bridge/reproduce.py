from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import BoardPokemon, PokemonCard, make_state
from identity_materialization import IdentityLedger, materialize, put_in_play_instance
from knockout_phase_resolution import PlayerKnockOutBatch, TwoPlayerKnockOutPhase
from knockout_prize_profile_bridge import printed_prize_awards, printed_prize_batches
from multicopy_zone_state import ZoneCountState
from pokemon_card_profile import build_pokemon_card_profile_index
from post_knockout_game_resolution import Outcome, resolve_post_knockout
from simultaneous_knockout_conservation import prepare_knock_out_batch
from stack_knockout_conservation import StackBoardMaterialState


def build_side(
    prefix: str,
    prints: tuple[tuple[str, str, str], ...],
) -> tuple[StackBoardMaterialState, dict[str, str]]:
    counts = {
        (f"{prefix}-class-{index}", "hand"): 1
        for index in range(len(prints))
    }
    ledger = IdentityLedger(ZoneCountState.from_mapping(counts))
    rows = []
    bindings: dict[str, str] = {}

    for index, (pokemon_id, print_id, name) in enumerate(prints):
        instance_id = f"{prefix}-instance-{index}"
        card_class = f"{prefix}-class-{index}"
        ledger = materialize(
            ledger,
            card_class=card_class,
            card_name=name,
            source_zone="hand",
            instance_id=instance_id,
        )
        ledger = put_in_play_instance(ledger, instance_id, pokemon_id)
        rows.append(
            BoardPokemon(
                pokemon_id,
                (PokemonCard(instance_id, name),),
                retreat_cost=1,
            )
        )
        bindings[pokemon_id] = print_id

    return (
        StackBoardMaterialState(
            ledger,
            make_state(rows, active_id=prints[0][0]),
        ),
        bindings,
    )


def main() -> None:
    profiles = build_pokemon_card_profile_index(ROOT / "resources")

    p1, p1_prints = build_side(
        "p1",
        (("p1-active", "bw9-81", "Dratini"),),
    )
    p2, p2_prints = build_side(
        "p2",
        (
            ("p2-active", "sv6-130", "Dragapult ex"),
            ("p2-bench", "cel25-7", "Flying Pikachu VMAX"),
        ),
    )

    assert profiles["bw9-81"].prize_value == 1
    assert profiles["sv6-130"].prize_value == 2
    assert profiles["cel25-7"].prize_value == 3

    pending_p1 = prepare_knock_out_batch(p1, ("p1-active",))
    pending_p2 = prepare_knock_out_batch(
        p2,
        ("p2-active", "p2-bench"),
    )
    assert pending_p1 is not None
    assert pending_p2 is not None

    phase = TwoPlayerKnockOutPhase(
        (
            PlayerKnockOutBatch("P1", pending_p1),
            PlayerKnockOutBatch("P2", pending_p2),
        ),
        current_turn_player="P1",
        next_turn_player="P2",
    )

    batches = printed_prize_batches(
        phase,
        profiles=profiles,
        current_print_ids={
            "P1": p1_prints,
            "P2": p2_prints,
        },
    )
    by_victim = {batch.victim_player_id: batch for batch in batches}
    assert by_victim["P1"].knocked_out_values == (("p1-active", 1),)
    assert by_victim["P1"].winner_player_id == "P2"
    assert by_victim["P2"].knocked_out_values == (
        ("p2-active", 2),
        ("p2-bench", 3),
    )
    assert by_victim["P2"].winner_player_id == "P1"

    awards = printed_prize_awards(
        phase,
        profiles=profiles,
        current_print_ids={
            "P1": p1_prints,
            "P2": p2_prints,
        },
    )
    assert awards == {"P1": 5, "P2": 1}

    resolved = resolve_post_knockout(
        phase,
        prizes_remaining_before={"P1": 4, "P2": 6},
        prize_awards=awards,
    )
    assert resolved.player("P1").prize_award == 5
    assert resolved.player("P1").prizes_taken == 4
    assert resolved.player("P1").prizes_remaining == 0
    assert resolved.player("P2").prizes_taken == 1
    assert resolved.player("P2").prizes_remaining == 5
    assert resolved.resolution.outcome("P1") == Outcome.WIN
    assert resolved.resolution.outcome("P2") == Outcome.LOSS

    print(
        {
            "printed_prize_awards": awards,
            "p1_prizes_taken_after_cap": resolved.player("P1").prizes_taken,
            "outcome": {
                "P1": resolved.resolution.outcome("P1").value,
                "P2": resolved.resolution.outcome("P2").value,
            },
        }
    )


if __name__ == "__main__":
    main()
