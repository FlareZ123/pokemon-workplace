"""Reproduce non-interrupting KO-trigger cascades with physical KO growth."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import BoardPokemon, PokemonCard, make_state
from build_expanded_legality_baseline import classify_effective_legality
from cross_player_knockout_resolution import (
    choose_promotion,
    resolve_cross_player_knock_out,
)
from growing_knockout_context import (
    begin_growing_knock_out_context,
    mark_additional_knock_out,
    to_cross_player_context,
)
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from stack_knockout_conservation import StackBoardMaterialState
from trigger_deferral_kernel import (
    make_trigger_state,
    record_trigger,
    resolve_next_step,
    start_ready_effect,
)


def load_card(set_id: str, card_id: str) -> dict:
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(card for card in cards if card["id"] == card_id)


def make_side(
    prefix: str,
    *,
    active_name: str,
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
        card_name=active_name,
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
        card_name=f"{prefix} Backup",
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
                    (PokemonCard(active_instance, active_name),),
                    retreat_cost=1,
                ),
                BoardPokemon(
                    bench_object,
                    (PokemonCard(bench_instance, f"{prefix} Backup"),),
                    retreat_cost=1,
                ),
            ),
            active_id=active_object,
        ),
    )
    assert_conserved(initial, state.ledger)
    return initial, state


def main() -> None:
    gastly = load_card("sm10", "sm10-67")
    gengar = load_card("me55", "me55-90")
    assert classify_effective_legality(gastly)[0] == "Legal"
    assert classify_effective_legality(gengar)[0] == "Legal"

    swelling = next(
        ability for ability in gastly["abilities"]
        if ability["name"] == "Swelling Spite"
    )
    fainting = next(
        ability for ability in gengar["abilities"]
        if ability["name"] == "Fainting Spell"
    )
    assert "When this Pokémon is Knocked Out" in swelling["text"]
    assert "Attacking Pokémon is Knocket Out" in fainting["text"]

    initial_a, state_a = make_side("a", active_name="Gastly")
    initial_b, state_b = make_side("b", active_name="Gengar ex")

    # Gastly attacks during A's turn and finishes a damaged Gengar ex.
    growing = begin_growing_knock_out_context(
        {"A": state_a, "B": state_b},
        next_player_id="B",
        initial_knockouts={"B": ("b-active",)},
    )
    assert growing is not None

    scheduler = make_trigger_state("gengar-fainting-spell")
    scheduler = start_ready_effect(
        scheduler,
        effect_id="gengar-fainting-spell",
        steps=("flip_coin_heads", "knock_out_attacking_gastly"),
    )
    assert scheduler is not None

    first = resolve_next_step(scheduler)
    assert first is not None
    step, scheduler = first
    assert step == "flip_coin_heads"
    assert scheduler.active is not None

    # Execute the second step while Fainting Spell is still the active effect.
    growing = mark_additional_knock_out(
        growing,
        player_id="A",
        pokemon_id="a-active",
    )
    assert growing is not None

    scheduler = record_trigger(
        scheduler,
        effect_id="gastly-swelling-spite",
    )
    assert scheduler is not None
    assert scheduler.deferred_effects == {"gastly-swelling-spite"}

    # A newly triggered effect cannot interrupt Fainting Spell.
    assert start_ready_effect(
        scheduler,
        effect_id="gastly-swelling-spite",
        steps=("put_haunter_on_bench", "shuffle_deck"),
    ) is None

    second = resolve_next_step(scheduler)
    assert second is not None
    step, scheduler = second
    assert step == "knock_out_attacking_gastly"
    assert scheduler.active is None
    assert scheduler.deferred_effects == frozenset()
    assert scheduler.ready_effects == {"gastly-swelling-spite"}
    assert scheduler.completed_effects == ("gengar-fainting-spell",)

    scheduler = start_ready_effect(
        scheduler,
        effect_id="gastly-swelling-spite",
        steps=("put_haunter_on_bench", "shuffle_deck"),
    )
    assert scheduler is not None

    for expected in ("put_haunter_on_bench", "shuffle_deck"):
        resolved = resolve_next_step(scheduler)
        assert resolved is not None
        step, scheduler = resolved
        assert step == expected

    assert scheduler.active is None
    assert scheduler.ready_effects == frozenset()
    assert scheduler.completed_effects == (
        "gengar-fainting-spell",
        "gastly-swelling-spite",
    )

    # Only after the trigger cascade is finished do we freeze physical KO
    # membership into the existing cross-player disposal protocol.
    context = to_cross_player_context(growing)
    assert context is not None

    after_b = choose_promotion(
        context,
        player_id="B",
        pokemon_id="b-bench",
    )
    assert after_b is not None
    ready = choose_promotion(
        after_b,
        player_id="A",
        pokemon_id="a-bench",
    )
    assert ready is not None

    final = resolve_cross_player_knock_out(ready)
    assert final is not None
    final_a = final.state_for("A")
    final_b = final.state_for("B")
    assert final_a.ledger.exchangeable.count(
        "a-active-class",
        "discard",
    ) == 1
    assert final_b.ledger.exchangeable.count(
        "b-active-class",
        "discard",
    ) == 1
    assert_conserved(initial_a, final_a.ledger)
    assert_conserved(initial_b, final_b.ledger)

    print("trigger deferral and KO cascade regressions passed")


if __name__ == "__main__":
    main()
