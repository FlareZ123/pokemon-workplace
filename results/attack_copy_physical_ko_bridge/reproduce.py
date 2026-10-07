from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (
    AttackDef,
    CopySelector,
    PokemonRef,
    State,
    choose_exact,
    resolve_attack,
)
from attack_copy_physical_ko_bridge import (
    PhysicalBoardEventProgram,
    prepare_physical_knockouts,
    replay_copy_attack_physical_board,
)
from board_position_state import (
    AttachmentKind,
    BoardPokemon,
    PokemonCard,
    make_state,
)
from damage_board_bridge import EffectCounterPlacement
from damage_calculation_kernel import AttackDamage, DamageContext
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from simultaneous_knockout_conservation import discard_pending_knock_out_batch
from stack_knockout_conservation import StackBoardMaterialState, attach_from_hand

HAUGHTY = "persian:haughty-order"
PHANTOM = "dragapult:phantom-dive"
PHANTOM_EVENT = "body:phantom-dive"

ATTACKS = {
    HAUGHTY: AttackDef(
        HAUGHTY,
        "Haughty Order",
        copy_selector=CopySelector("opponent_revealed"),
        pre_event="reveal_top_10",
        post_event="shuffle_revealed",
    ),
    PHANTOM: AttackDef(
        PHANTOM,
        "Phantom Dive",
        effect_label=PHANTOM_EVENT,
    ),
}


def phantom_resolution():
    return resolve_attack(
        actor_player="P1",
        actor_card_id="p1-persian",
        declared_attack_id=HAUGHTY,
        attacks=ATTACKS,
        state=State(
            pokemon=(
                PokemonRef(
                    "p2-dragapult-revealed",
                    "Dragapult ex",
                    "P2",
                    "revealed",
                    attacks=(PHANTOM,),
                ),
            )
        ),
        choose=choose_exact((PHANTOM,)),
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


def physical_target_state() -> tuple[IdentityLedger, StackBoardMaterialState]:
    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("active-card", "hand"): 1,
                ("bench-card", "hand"): 1,
                ("survivor-card", "hand"): 1,
                ("active-tool", "hand"): 1,
                ("bench-energy", "hand"): 1,
            }
        )
    )
    ledger = put_pokemon(
        initial,
        card_class="active-card",
        card_name="200 HP Active",
        instance_id="active-copy",
        pokemon_id="active",
    )
    ledger = put_pokemon(
        ledger,
        card_class="bench-card",
        card_name="60 HP Bench",
        instance_id="bench-copy",
        pokemon_id="bench60",
    )
    ledger = put_pokemon(
        ledger,
        card_class="survivor-card",
        card_name="Survivor",
        instance_id="survivor-copy",
        pokemon_id="survivor",
    )

    board = make_state(
        (
            BoardPokemon(
                "active",
                (PokemonCard("active-copy", "200 HP Active"),),
                retreat_cost=1,
            ),
            BoardPokemon(
                "bench60",
                (PokemonCard("bench-copy", "60 HP Bench"),),
                retreat_cost=1,
            ),
            BoardPokemon(
                "survivor",
                (PokemonCard("survivor-copy", "Survivor"),),
                retreat_cost=1,
            ),
        ),
        active_id="active",
    )
    state = StackBoardMaterialState(ledger, board)
    state = attach_from_hand(
        state,
        pokemon_id="active",
        card_class="active-tool",
        instance_id="tool-copy",
        card_name="Muscle Band",
        kind=AttachmentKind.TOOL,
    )
    assert state is not None
    state = attach_from_hand(
        state,
        pokemon_id="bench60",
        card_class="bench-energy",
        instance_id="energy-copy",
        card_name="Basic Psychic Energy",
        kind=AttachmentKind.ENERGY,
        retreat_units=1,
    )
    assert state is not None
    assert_conserved(initial, state.ledger)
    return initial, state


def main() -> None:
    initial, state = physical_target_state()
    resolution = phantom_resolution()

    replay = replay_copy_attack_physical_board(
        resolution,
        state,
        event_programs={
            PHANTOM_EVENT: PhysicalBoardEventProgram(
                "active",
                DamageContext(attack=AttackDamage(200)),
                (EffectCounterPlacement("bench60", 6),),
            )
        },
        hp_by_pokemon_id={
            "active": 200,
            "bench60": 60,
            "survivor": 100,
        },
    )

    assert tuple(step.event for step in replay.event_trace) == (
        "reveal_top_10",
        PHANTOM_EVENT,
        "shuffle_revealed",
    )
    assert replay.event_trace[1].damage_counters == (
        ("active", 20),
        ("bench60", 6),
        ("survivor", 0),
    )
    assert replay.event_trace[2].damage_counters == (
        ("active", 20),
        ("bench60", 6),
        ("survivor", 0),
    )
    assert replay.knocked_out_ids == ("active", "bench60")
    assert_conserved(initial, replay.state.ledger)

    pending = prepare_physical_knockouts(replay)
    assert pending is not None
    assert pending.knocked_out_ids == ("active", "bench60")
    assert pending.state.board is not None
    assert {pokemon.pokemon_id for pokemon in pending.state.board.pokemon} == {
        "active",
        "bench60",
        "survivor",
    }
    assert {
        attachment.card_id
        for attachment in pending.state.board.get("active").attachments
    } == {"tool-copy"}
    assert {
        attachment.card_id
        for attachment in pending.state.board.get("bench60").attachments
    } == {"energy-copy"}

    resolved = discard_pending_knock_out_batch(
        pending,
        promote_id="survivor",
    )
    assert resolved is not None
    assert resolved.board is not None
    assert resolved.board.active_id == "survivor"
    assert tuple(pokemon.pokemon_id for pokemon in resolved.board.pokemon) == (
        "survivor",
    )

    assert resolved.ledger.exchangeable.count("active-card", "discard") == 1
    assert resolved.ledger.exchangeable.count("bench-card", "discard") == 1
    assert resolved.ledger.exchangeable.count("active-tool", "discard") == 1
    assert resolved.ledger.exchangeable.count("bench-energy", "discard") == 1
    assert resolved.ledger.exchangeable.count("survivor-card", "discard") == 0
    assert_conserved(initial, resolved.ledger)

    print("attack-copy physical KO bridge regression: PASS")


if __name__ == "__main__":
    main()
