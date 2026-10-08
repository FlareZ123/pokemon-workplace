"""Reproduce exact copied-attack self-healing on physical boards."""
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
    replay_copy_attack_physical_board,
)
from board_position_state import (
    AttachmentKind,
    BoardPokemon,
    PokemonCard,
    make_state,
)
from damage_calculation_kernel import AttackDamage, DamageContext
from healing_profile_compiler import (
    HealingTarget,
    compile_healing_profiles,
)
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from physical_attack_healing_source_bridge import (
    apply_physical_attack_self_healing,
)
from physical_copy_damage_reaction_bridge import (
    resolve_physical_copy_damage_reactions,
)
from physical_damage_reaction_sources import eligible_spiky_energy_reactions
from simple_attack_board_semantics import compile_legal_index
from stack_knockout_conservation import StackBoardMaterialState, attach_from_hand


def actor_state(damage_counters: int) -> tuple[IdentityLedger, StackBoardMaterialState]:
    initial = IdentityLedger(ZoneCountState.from_mapping({
        ("actor-class", "hand"): 1,
    }))
    ledger = materialize(
        initial,
        card_class="actor-class",
        card_name="Team Rocket's Persian ex",
        source_zone="hand",
        instance_id="actor-instance",
    )
    ledger = put_in_play_instance(ledger, "actor-instance", "actor-active")
    board = make_state(
        (
            BoardPokemon(
                "actor-active",
                (PokemonCard("actor-instance", "Team Rocket's Persian ex"),),
                retreat_cost=1,
                damage_counters=damage_counters,
            ),
        ),
        active_id="actor-active",
    )
    state = StackBoardMaterialState(ledger, board)
    assert_conserved(initial, state.ledger)
    return initial, state


def defender_with_spiky() -> tuple[IdentityLedger, StackBoardMaterialState]:
    initial = IdentityLedger(ZoneCountState.from_mapping({
        ("defender-class", "hand"): 1,
        ("spiky-class", "hand"): 1,
    }))
    ledger = materialize(
        initial,
        card_class="defender-class",
        card_name="Dratini",
        source_zone="hand",
        instance_id="defender-instance",
    )
    ledger = put_in_play_instance(
        ledger, "defender-instance", "defender-active"
    )
    board = make_state(
        (
            BoardPokemon(
                "defender-active",
                (PokemonCard("defender-instance", "Dratini"),),
                retreat_cost=1,
            ),
        ),
        active_id="defender-active",
    )
    state = StackBoardMaterialState(ledger, board)
    attached = attach_from_hand(
        state,
        pokemon_id="defender-active",
        card_class="spiky-class",
        instance_id="spiky-instance",
        card_name="Spiky Energy",
        kind=AttachmentKind.ENERGY,
        retreat_units=1,
    )
    assert attached is not None
    assert_conserved(initial, attached.ledger)
    return initial, attached


def one_profile(card_id: str, attack_name: str):
    rows = compile_healing_profiles(ROOT / "resources")
    matches = tuple(
        row for row in rows
        if row.card_id == card_id
        and row.source_kind == "attack"
        and row.source_name == attack_name
    )
    assert len(matches) == 1
    profile = matches[0]
    assert profile.target == HealingTarget.SOURCE_POKEMON
    assert profile.attack_index is not None
    return profile


def copied_replay(profile, target_state: StackBoardMaterialState):
    index = compile_legal_index(ROOT / "resources")
    source = index[profile.card_id][profile.attack_index]
    leaf = source.to_leaf_attack_def()
    outer = AttackDef(
        "persian:haughty-order",
        "Haughty Order",
        copy_selector=CopySelector("opponent_revealed"),
        pre_event="reveal_top_10",
        post_event="shuffle_revealed",
    )
    resolution = resolve_attack(
        actor_player="P1",
        actor_card_id="actor-active",
        declared_attack_id=outer.attack_id,
        attacks={outer.attack_id: outer, leaf.attack_id: leaf},
        state=State(
            pokemon=(
                PokemonRef(
                    "revealed-source",
                    profile.name,
                    "P2",
                    "revealed",
                    attacks=(leaf.attack_id,),
                ),
            )
        ),
        choose=choose_exact((leaf.attack_id,)),
    )
    programs = {}
    if source.fixed_damage:
        programs[source.event_label] = PhysicalBoardEventProgram(
            damage_target_id="defender-active",
            damage_context=DamageContext(
                attack=AttackDamage(source.fixed_damage),
            ),
        )
    replay = replay_copy_attack_physical_board(
        resolution,
        target_state,
        event_programs=programs,
        hp_by_pokemon_id={"defender-active": 100},
    )
    assert source.event_label in replay.resolution.state.events
    return source, replay


def main() -> None:
    mega_drain = one_profile("bw1-11", "Mega Drain")
    assert mega_drain.heal_damage == 20
    actor_initial, actor = actor_state(4)
    defender_initial, defender = defender_with_spiky()
    source, replay = copied_replay(mega_drain, defender)

    assert source.fixed_damage == 20
    assert replay.state.board.get("defender-active").damage_counters == 2
    assert replay.state.board.get("defender-active").attachments[0].name == (
        "Spiky Energy"
    )

    healed = apply_physical_attack_self_healing(
        replay,
        actor,
        mega_drain,
        attacking_pokemon_id="actor-active",
    )
    assert healed.counters_removed == 2
    assert healed.actor_state.board.get("actor-active").damage_counters == 2
    assert_conserved(actor_initial, healed.actor_state.ledger)

    reactions = eligible_spiky_energy_reactions(
        replay,
        body_event=healed.body_event,
        damaged_pokemon_id="defender-active",
        from_opponents_pokemon=True,
    )
    assert len(reactions) == 1
    reacted = resolve_physical_copy_damage_reactions(
        replay,
        healed.actor_state,
        body_event=healed.body_event,
        damaged_pokemon_id="defender-active",
        attacking_pokemon_id="actor-active",
        reactions=reactions,
        attacker_hp_by_pokemon_id={"actor-active": 100},
        defender_hp_by_pokemon_id={"defender-active": 100},
    )
    assert reacted.counters_placed_on_attacker == 2
    assert reacted.attacker_state.board.get("actor-active").damage_counters == 4
    assert_conserved(actor_initial, reacted.attacker_state.ledger)
    assert_conserved(defender_initial, reacted.defender_state.ledger)

    # Effect-only copied attacks still heal the physical copying Pokemon even
    # when there is no damage event or post-damage reaction window.
    calm_mind = one_profile("bw3-54", "Calm Mind")
    assert calm_mind.heal_damage == 30
    clean_initial, damaged_actor = actor_state(3)
    _source, calm_replay = copied_replay(calm_mind, defender)
    assert calm_replay.damage_records == ()
    calm = apply_physical_attack_self_healing(
        calm_replay,
        damaged_actor,
        calm_mind,
        attacking_pokemon_id="actor-active",
    )
    assert calm.counters_removed == 3
    assert calm.actor_state.board.get("actor-active").damage_counters == 0
    assert_conserved(clean_initial, calm.actor_state.ledger)

    rejected = 0
    try:
        apply_physical_attack_self_healing(
            replay,
            actor,
            calm_mind,
            attacking_pokemon_id="actor-active",
        )
    except ValueError:
        rejected += 1
    try:
        apply_physical_attack_self_healing(
            replay,
            actor,
            mega_drain,
            attacking_pokemon_id="missing-attacker",
        )
    except ValueError:
        rejected += 1
    assert rejected == 2

    print({
        "copied_healing_sources": (
            (mega_drain.card_id, mega_drain.source_name, mega_drain.heal_damage),
            (calm_mind.card_id, calm_mind.source_name, calm_mind.heal_damage),
        ),
        "mega_drain_timing_counters": {
            "before_attack": 4,
            "after_step5_heal": 2,
            "after_step6_spiky": 4,
        },
        "effect_only_heal_to_zero": calm.counters_removed,
        "physical_ledgers_conserved": True,
        "invalid_source_gates": rejected,
    })


if __name__ == "__main__":
    main()
