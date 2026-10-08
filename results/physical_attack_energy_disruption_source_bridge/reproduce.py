"""Reproduce copied Energy disruption before damaged-by-attack reactions."""
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
from board_position_state import AttachmentKind, BoardPokemon, PokemonCard, make_state
from damage_calculation_kernel import AttackDamage, DamageContext
from energy_disruption_profile_compiler import compile_energy_disruption_profiles
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from physical_attack_energy_disruption_source_bridge import (
    apply_physical_attack_energy_disruption,
)
from physical_copy_damage_reaction_bridge import resolve_physical_copy_damage_reactions
from physical_damage_reaction_sources import eligible_spiky_energy_reactions
from simple_attack_board_semantics import compile_legal_index
from stack_knockout_conservation import StackBoardMaterialState, attach_from_hand


def actor_state() -> tuple[IdentityLedger, StackBoardMaterialState]:
    initial = IdentityLedger(ZoneCountState.from_mapping({("actor-class", "hand"): 1}))
    ledger = materialize(
        initial,
        card_class="actor-class",
        card_name="Team Rocket's Persian ex",
        source_zone="hand",
        instance_id="actor-card",
    )
    ledger = put_in_play_instance(ledger, "actor-card", "actor-active")
    state = StackBoardMaterialState(
        ledger,
        make_state(
            (
                BoardPokemon(
                    "actor-active",
                    (PokemonCard("actor-card", "Team Rocket's Persian ex"),),
                    retreat_cost=1,
                ),
            ),
            active_id="actor-active",
        ),
    )
    return initial, state


def defender_state() -> tuple[IdentityLedger, StackBoardMaterialState]:
    initial = IdentityLedger(
        ZoneCountState.from_mapping({
            ("defender-class", "hand"): 1,
            ("spiky-class", "hand"): 1,
            ("basic-class", "hand"): 1,
        })
    )
    ledger = materialize(
        initial,
        card_class="defender-class",
        card_name="Defender",
        source_zone="hand",
        instance_id="defender-card",
    )
    ledger = put_in_play_instance(ledger, "defender-card", "defender-active")
    state = StackBoardMaterialState(
        ledger,
        make_state(
            (
                BoardPokemon(
                    "defender-active",
                    (PokemonCard("defender-card", "Defender"),),
                    retreat_cost=1,
                ),
            ),
            active_id="defender-active",
        ),
    )
    for card_class, instance_id, name in (
        ("spiky-class", "spiky-energy", "Spiky Energy"),
        ("basic-class", "basic-energy", "Basic Metal Energy"),
    ):
        attached = attach_from_hand(
            state,
            pokemon_id="defender-active",
            card_class=card_class,
            instance_id=instance_id,
            card_name=name,
            kind=AttachmentKind.ENERGY,
            retreat_units=1,
        )
        assert attached is not None
        state = attached
    return initial, state


def profile(card_id: str, attack_name: str):
    matches = tuple(
        row
        for row in compile_energy_disruption_profiles(ROOT / "resources")
        if row.card_id == card_id
        and row.source_kind == "attack"
        and row.source_name == attack_name
    )
    assert len(matches) == 1
    assert matches[0].attack_index is not None
    return matches[0]


def copied_replay(source_profile, target_state):
    index = compile_legal_index(ROOT / "resources")
    source = index[source_profile.card_id][source_profile.attack_index]
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
                    source_profile.name,
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
            damage_context=DamageContext(attack=AttackDamage(source.fixed_damage)),
        )
    replay = replay_copy_attack_physical_board(
        resolution,
        target_state,
        event_programs=programs,
        hp_by_pokemon_id={"defender-active": 200},
    )
    return source, replay


def main() -> None:
    hyper_beam = profile("me2-74", "Hyper Beam")
    deleting_glare = profile("bw2-46", "Deleting Glare")

    actor_initial, actor = actor_state()
    defender_initial, defender = defender_state()
    source, replay = copied_replay(hyper_beam, defender)
    assert source.fixed_damage == 70
    body_event = f"body:{hyper_beam.card_id}:attack:{hyper_beam.attack_index}"

    before_step5 = eligible_spiky_energy_reactions(
        replay,
        body_event=body_event,
        damaged_pokemon_id="defender-active",
        from_opponents_pokemon=True,
    )
    assert len(before_step5) == 1

    remove_spiky = apply_physical_attack_energy_disruption(
        replay,
        hyper_beam,
        energy_instance_id="spiky-energy",
    )
    assert remove_spiky.discarded_energy_instance_id == "spiky-energy"
    assert (
        remove_spiky.updated_copy_resolution.state.ledger.exchangeable.count(
            "spiky-class", "discard"
        )
        == 1
    )
    after_spiky_removed = eligible_spiky_energy_reactions(
        remove_spiky.updated_copy_resolution,
        body_event=body_event,
        damaged_pokemon_id="defender-active",
        from_opponents_pokemon=True,
    )
    assert after_spiky_removed == ()
    assert_conserved(defender_initial, remove_spiky.updated_copy_resolution.state.ledger)

    remove_basic = apply_physical_attack_energy_disruption(
        replay,
        hyper_beam,
        energy_instance_id="basic-energy",
    )
    spiky_survives = eligible_spiky_energy_reactions(
        remove_basic.updated_copy_resolution,
        body_event=body_event,
        damaged_pokemon_id="defender-active",
        from_opponents_pokemon=True,
    )
    assert len(spiky_survives) == 1
    reacted = resolve_physical_copy_damage_reactions(
        remove_basic.updated_copy_resolution,
        actor,
        body_event=body_event,
        damaged_pokemon_id="defender-active",
        attacking_pokemon_id="actor-active",
        reactions=spiky_survives,
        attacker_hp_by_pokemon_id={"actor-active": 200},
        defender_hp_by_pokemon_id={"defender-active": 200},
    )
    assert reacted.counters_placed_on_attacker == 2
    assert reacted.attacker_state.board.get("actor-active").damage_counters == 2
    assert_conserved(actor_initial, reacted.attacker_state.ledger)

    blocked = apply_physical_attack_energy_disruption(
        replay,
        hyper_beam,
        energy_instance_id="spiky-energy",
        blocked_effect_target_ids=frozenset({"defender-active"}),
    )
    assert blocked.blocked_by_effect_immunity
    assert blocked.discarded_energy_instance_id is None
    assert len(eligible_spiky_energy_reactions(
        blocked.updated_copy_resolution,
        body_event=body_event,
        damaged_pokemon_id="defender-active",
        from_opponents_pokemon=True,
    )) == 1

    _, glare_replay = copied_replay(deleting_glare, defender)
    assert glare_replay.damage_records == ()
    tails = apply_physical_attack_energy_disruption(
        glare_replay,
        deleting_glare,
        coin_heads=False,
    )
    assert tails.discarded_energy_instance_id is None
    heads = apply_physical_attack_energy_disruption(
        glare_replay,
        deleting_glare,
        target_pokemon_id="defender-active",
        energy_instance_id="basic-energy",
        coin_heads=True,
    )
    assert heads.discarded_energy_instance_id == "basic-energy"

    print({
        "hyper_beam_damage": source.fixed_damage,
        "spiky_reaction_before_step5": len(before_step5),
        "spiky_reaction_after_discarding_spiky": len(after_spiky_removed),
        "spiky_reaction_after_discarding_other_energy": len(spiky_survives),
        "backlash_counters_when_spiky_survives": reacted.counters_placed_on_attacker,
        "effect_immunity_preserves_spiky": blocked.blocked_by_effect_immunity,
        "coin_gated_deleting_glare": {
            "tails_discard": tails.discarded_energy_instance_id,
            "heads_discard": heads.discarded_energy_instance_id,
        },
        "physical_ledgers_conserved": True,
    })


if __name__ == "__main__":
    main()
