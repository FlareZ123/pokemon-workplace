"""Reproduce attack-inflicted statuses in copied-body physical attack timing."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (
    AttackDef, CopySelector, PokemonRef, State, choose_exact, resolve_attack,
)
from attack_copy_physical_ko_bridge import (
    PhysicalBoardEventProgram, replay_copy_attack_physical_board,
)
from attack_status_text_contracts import compile_attack_status_source
from board_position_state import BoardPokemon, PokemonCard, make_state
from damage_calculation_kernel import AttackDamage, DamageContext
from identity_materialization import IdentityLedger, materialize, put_in_play_instance
from multicopy_zone_state import ZoneCountState
from physical_attack_status_source_bridge import apply_physical_attack_source_status
from physical_copy_damage_reaction_bridge import resolve_physical_copy_damage_reactions
from physical_damage_condition_reactions import (
    eligible_printed_condition_reactions, apply_physical_condition_reactions,
)
from simple_attack_board_semantics import compile_attack
from special_condition_state import ConditionKind
from stack_knockout_conservation import StackBoardMaterialState


def physical_defender(*, name: str = "Defender") -> StackBoardMaterialState:
    initial = IdentityLedger(ZoneCountState.from_mapping({
        ("a-class", "hand"): 1,
        ("b-class", "hand"): 1,
    }))
    ledger = initial
    pokemon = []
    for pokemon_id, card_class in (("active", "a-class"), ("bench", "b-class")):
        instance = pokemon_id + "-instance"
        ledger = materialize(
            ledger, card_class=card_class, card_name=name,
            source_zone="hand", instance_id=instance,
        )
        ledger = put_in_play_instance(ledger, instance, pokemon_id)
        pokemon.append(BoardPokemon(
            pokemon_id, (PokemonCard(instance, name),), retreat_cost=1,
        ))
    return StackBoardMaterialState(ledger, make_state(pokemon, active_id="active"))


def copied_status_source(card_id: str, attack_name: str, physical: StackBoardMaterialState):
    set_id = card_id.split("-")[0]
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    card = next(c for c in cards if c["id"] == card_id)
    index = next(
        i for i, a in enumerate(card.get("attacks") or ())
        if a["name"] == attack_name
    )
    contract = compile_attack_status_source(card, index)
    assert contract is not None
    source = compile_attack(card, index)
    leaf = source.to_leaf_attack_def()
    outer = AttackDef(
        "persian:haughty-order", "Haughty Order",
        copy_selector=CopySelector("opponent_revealed"),
        pre_event="reveal_top_10",
        post_event="shuffle_revealed",
    )
    resolution = resolve_attack(
        actor_player="P1", actor_card_id="p1-persian",
        declared_attack_id=outer.attack_id,
        attacks={outer.attack_id: outer, leaf.attack_id: leaf},
        state=State(pokemon=(
            PokemonRef(
                "revealed-source", card["name"], "P2",
                "revealed", attacks=(leaf.attack_id,),
            ),
        )),
        choose=choose_exact((leaf.attack_id,)),
    )
    damage = int(source.raw_damage) if source.raw_damage else 0
    program = (
        {source.event_label: PhysicalBoardEventProgram(
            damage_target_id="active",
            damage_context=DamageContext(attack=AttackDamage(damage)),
        )}
        if damage else {}
    )
    replay = replay_copy_attack_physical_board(
        resolution, physical,
        event_programs=program,
        hp_by_pokemon_id={"active": 200, "bench": 100},
    )
    assert f"body:{contract.attack_id}" in replay.resolution.state.events
    assert replay.event_trace[-1].event == "shuffle_revealed"
    return contract, replay


def main() -> None:
    initial = physical_defender()
    poison, poison_replay = copied_status_source(
        "bw1-53", "Poison Sting", initial
    )
    poisoned = apply_physical_attack_source_status(poison_replay, poison)
    assert poisoned.applied
    assert poisoned.condition == ConditionKind.POISONED
    assert poisoned.state.board.get("active").special_conditions == {"Poisoned"}
    assert poisoned.state.board.get("active").damage_counters == 2

    burned_contract, burned_replay = copied_status_source(
        "bw1-24", "Singe", poisoned.state
    )
    assert burned_replay.damage_records == ()
    burned = apply_physical_attack_source_status(
        burned_replay, burned_contract,
        typed_current=poisoned.typed_active_conditions,
    )
    assert burned.applied
    assert burned.state.board.get("active").special_conditions == {
        "Poisoned", "Burned",
    }

    confused_contract, confused_replay = copied_status_source(
        "bw1-79", "Confuse Ray", burned.state
    )
    confused = apply_physical_attack_source_status(
        confused_replay, confused_contract,
        typed_current=burned.typed_active_conditions,
    )
    assert confused.state.board.get("active").special_conditions == {
        "Poisoned", "Burned", "Confused",
    }

    sleep_contract, sleep_replay = copied_status_source(
        "bw1-39", "Water Pulse", confused.state
    )
    asleep = apply_physical_attack_source_status(
        sleep_replay, sleep_contract,
        typed_current=confused.typed_active_conditions,
    )
    assert asleep.state.board.get("active").special_conditions == {
        "Poisoned", "Burned", "Asleep",
    }
    assert asleep.state.board.get("active").damage_counters == 4

    wrap_contract, wrap_replay = copied_status_source(
        "bw1-3", "Wrap", asleep.state
    )
    tails = apply_physical_attack_source_status(
        wrap_replay, wrap_contract, coin_heads=False,
        typed_current=asleep.typed_active_conditions,
    )
    assert not tails.applied
    assert tails.state == wrap_replay.state

    heads = apply_physical_attack_source_status(
        wrap_replay, wrap_contract, coin_heads=True,
        typed_current=asleep.typed_active_conditions,
    )
    assert heads.applied
    assert heads.state.board.get("active").special_conditions == {
        "Poisoned", "Burned", "Paralyzed",
    }
    assert heads.state.board.get("active").damage_counters == 6
    assert heads.state.ledger == initial.ledger

    suppressed = apply_physical_attack_source_status(
        poison_replay, poison, prevent_effects_of_attacks=True,
    )
    assert not suppressed.applied
    assert suppressed.state == poison_replay.state

    # The attacking source's step-5 status and a damaged-by-attack
    # Ability on that defender are separate timing windows. Neither
    # overwrites the other's physical board or card instances.
    persian_state = physical_defender(name="Persian")
    roselia_state = physical_defender(name="Roselia")
    source, roselia_replay = copied_status_source(
        "bw1-53", "Poison Sting", roselia_state,
    )
    source_effect = apply_physical_attack_source_status(roselia_replay, source)
    assert source_effect.updated_copy_resolution.state == source_effect.state
    condition_sources = eligible_printed_condition_reactions(
        source_effect.updated_copy_resolution,
        resources=ROOT / "resources",
        body_event=source_effect.body_event,
        damaged_pokemon_id="active",
        defending_print_id="sv5-8",
        ability_is_enabled=True,
        from_opponents_pokemon=True,
    )
    assert condition_sources == (ConditionKind.POISONED,)
    reflected = resolve_physical_copy_damage_reactions(
        source_effect.updated_copy_resolution,
        persian_state,
        body_event=source_effect.body_event,
        damaged_pokemon_id="active",
        attacking_pokemon_id="active",
        reactions=(),
        attacker_hp_by_pokemon_id={"active": 200, "bench": 100},
        defender_hp_by_pokemon_id={"active": 60, "bench": 100},
    )
    both_status, triggered = apply_physical_condition_reactions(
        reflected, condition_sources,
    )
    assert triggered == (ConditionKind.POISONED,)
    assert both_status.attacker_state.board.get("active").special_conditions == {
        "Poisoned",
    }
    assert both_status.defender_state.board.get("active").special_conditions == {
        "Poisoned",
    }
    assert both_status.attacker_state.ledger == persian_state.ledger
    assert both_status.defender_state.ledger == roselia_state.ledger

    rejected = 0
    for operation in (
        lambda: apply_physical_attack_source_status(
            wrap_replay, wrap_contract,
            typed_current=asleep.typed_active_conditions,
        ),
        lambda: apply_physical_attack_source_status(
            burned_replay, burned_contract,
        ),
        lambda: apply_physical_attack_source_status(
            poison_replay, wrap_contract, coin_heads=True,
        ),
    ):
        try:
            operation()
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("invalid status source was accepted")
    assert rejected == 3

    print({
        "copied_status_sources_executed": 5,
        "condition_stacks": (
            tuple(sorted(poisoned.state.board.get("active").special_conditions)),
            tuple(sorted(heads.state.board.get("active").special_conditions)),
        ),
        "coin_heads_vs_tails": (heads.applied, tails.applied),
        "effect_immunity_suppresses_status": not suppressed.applied,
        "failed_state_gates": rejected,
        "physical_instance_ledger_preserved": heads.state.ledger == initial.ledger,
        "attack_status_before_passive_poison_reflection": tuple(
            (side, state.board.get("active").special_conditions)
            for side, state in (
                ("actor", both_status.attacker_state),
                ("defender", both_status.defender_state),
            )
        ),
    })


if __name__ == "__main__":
    main()
