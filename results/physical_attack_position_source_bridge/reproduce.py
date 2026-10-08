"""Reproduce copied attack-source position effects on physical boards."""
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
from damage_calculation_kernel import AttackDamage, DamageContext
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from physical_attack_position_source_bridge import (
    apply_physical_attack_position_effect,
)
from physical_copy_damage_reaction_bridge import (
    resolve_physical_copy_damage_reactions,
)
from physical_damage_condition_reactions import (
    apply_physical_condition_reactions,
    eligible_printed_condition_reactions,
)
from position_effect_profile_compiler import (
    PositionEffectKind,
    compile_position_effect_profiles,
)
from simple_attack_board_semantics import compile_legal_index
from simultaneous_knockout_conservation import discard_pending_knock_out_batch
from special_condition_state import ConditionKind
from stack_knockout_conservation import StackBoardMaterialState, attach_from_hand


def physical_side(
    prefix: str,
    *,
    active_name: str,
    bench_names: tuple[str, ...],
    active_conditions: frozenset[str] = frozenset(),
    attach_active_energy: bool = False,
) -> tuple[IdentityLedger, StackBoardMaterialState]:
    ids = (f"{prefix}-active",) + tuple(
        f"{prefix}-bench-{index}" for index in range(len(bench_names))
    )
    names = (active_name,) + bench_names
    counts = {
        (f"{pokemon_id}-class", "hand"): 1
        for pokemon_id in ids
    }
    if attach_active_energy:
        counts[(f"{prefix}-energy-class", "hand")] = 1

    initial = IdentityLedger(ZoneCountState.from_mapping(counts))
    ledger = initial
    pokemon = []
    for index, (pokemon_id, name) in enumerate(zip(ids, names)):
        instance_id = f"{pokemon_id}-instance"
        ledger = materialize(
            ledger,
            card_class=f"{pokemon_id}-class",
            card_name=name,
            source_zone="hand",
            instance_id=instance_id,
        )
        ledger = put_in_play_instance(ledger, instance_id, pokemon_id)
        pokemon.append(
            BoardPokemon(
                pokemon_id,
                (PokemonCard(instance_id, name),),
                retreat_cost=1,
                special_conditions=active_conditions if index == 0 else frozenset(),
            )
        )
    state = StackBoardMaterialState(
        ledger,
        make_state(pokemon, active_id=ids[0]),
    )
    if attach_active_energy:
        attached = attach_from_hand(
            state,
            pokemon_id=ids[0],
            card_class=f"{prefix}-energy-class",
            instance_id=f"{prefix}-energy-instance",
            card_name="Basic Colorless Test Energy",
            kind=AttachmentKind.ENERGY,
            retreat_units=1,
        )
        assert attached is not None
        state = attached
    assert_conserved(initial, state.ledger)
    return initial, state


def profile(rows, card_id: str, attack_name: str):
    matches = tuple(
        row for row in rows
        if row.card_id == card_id
        and row.source_kind == "attack"
        and row.source_name == attack_name
    )
    assert len(matches) == 1
    assert matches[0].attack_index is not None
    return matches[0]


def copied_replay(
    source_profile,
    target_state: StackBoardMaterialState,
    *,
    hp_by_pokemon_id: dict[str, int],
):
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
        actor_card_id="p1-persian",
        declared_attack_id=outer.attack_id,
        attacks={outer.attack_id: outer, leaf.attack_id: leaf},
        state=State(
            pokemon=(
                PokemonRef(
                    "p2-revealed-source",
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
            damage_target_id=target_state.board.active_id,
            damage_context=DamageContext(
                attack=AttackDamage(source.fixed_damage),
            ),
        )
    replay = replay_copy_attack_physical_board(
        resolution,
        target_state,
        event_programs=programs,
        hp_by_pokemon_id=hp_by_pokemon_id,
    )
    assert f"body:{source_profile.card_id}:attack:{source_profile.attack_index}" in (
        replay.resolution.state.events
    )
    return source, replay


def main() -> None:
    rows = compile_position_effect_profiles(ROOT / "resources")
    aqua = profile(rows, "sm3-39", "Aqua Ring")
    push_down = profile(rows, "me1-9", "Push Down")
    follow_me = profile(rows, "me3-30", "Follow Me")
    assert aqua.kind == PositionEffectKind.SELF_SWITCH
    assert push_down.kind == PositionEffectKind.OPPONENT_FORCED_SWITCH
    assert follow_me.kind == PositionEffectKind.TARGETED_GUST

    # Aqua Ring deals damage, then optionally moves the copying Pokemon.
    # A later damaged-by-attack Poison Point reaction therefore sees the
    # original attacker on the Bench when the pivot is taken.
    actor_initial, actor = physical_side(
        "actor",
        active_name="Persian",
        bench_names=("Pivot",),
        active_conditions=frozenset({"Burned"}),
        attach_active_energy=True,
    )
    _defender_initial, roselia = physical_side(
        "def",
        active_name="Roselia",
        bench_names=("Roselia Bench",),
    )
    aqua_source, aqua_replay = copied_replay(
        aqua,
        roselia,
        hp_by_pokemon_id={"def-active": 60, "def-bench-0": 100},
    )
    assert aqua_source.fixed_damage == 20
    assert aqua_replay.state.board.get("def-active").damage_counters == 2

    stayed = apply_physical_attack_position_effect(
        aqua_replay,
        actor,
        aqua,
        attacking_pokemon_id="actor-active",
        take_optional=False,
    )
    conditions = eligible_printed_condition_reactions(
        stayed.updated_copy_resolution,
        resources=ROOT / "resources",
        body_event=stayed.body_event,
        damaged_pokemon_id="def-active",
        defending_print_id="sv5-8",
        ability_is_enabled=True,
        from_opponents_pokemon=True,
    )
    assert conditions == (ConditionKind.POISONED,)
    stayed_reaction = resolve_physical_copy_damage_reactions(
        stayed.updated_copy_resolution,
        stayed.actor_state,
        body_event=stayed.body_event,
        damaged_pokemon_id="def-active",
        attacking_pokemon_id="actor-active",
        reactions=(),
        attacker_hp_by_pokemon_id={"actor-active": 200, "actor-bench-0": 100},
        defender_hp_by_pokemon_id={"def-active": 60, "def-bench-0": 100},
    )
    stayed_status, stayed_applied = apply_physical_condition_reactions(
        stayed_reaction,
        conditions,
    )
    assert stayed_applied == (ConditionKind.POISONED,)
    assert stayed_status.attacker_state.board.active_id == "actor-active"
    assert stayed_status.attacker_state.board.get("actor-active").special_conditions == {
        "Burned", "Poisoned",
    }

    pivoted = apply_physical_attack_position_effect(
        aqua_replay,
        actor,
        aqua,
        attacking_pokemon_id="actor-active",
        chosen_pokemon_id="actor-bench-0",
        take_optional=True,
    )
    assert pivoted.moved
    assert pivoted.actor_state.board.active_id == "actor-bench-0"
    moved_attacker = pivoted.actor_state.board.get("actor-active")
    assert moved_attacker.special_conditions == frozenset()
    assert {card.card_id for card in moved_attacker.attachments} == {
        "actor-energy-instance"
    }
    pivot_reaction = resolve_physical_copy_damage_reactions(
        pivoted.updated_copy_resolution,
        pivoted.actor_state,
        body_event=pivoted.body_event,
        damaged_pokemon_id="def-active",
        attacking_pokemon_id="actor-active",
        reactions=(),
        attacker_hp_by_pokemon_id={"actor-active": 200, "actor-bench-0": 100},
        defender_hp_by_pokemon_id={"def-active": 60, "def-bench-0": 100},
    )
    pivot_status, pivot_applied = apply_physical_condition_reactions(
        pivot_reaction,
        conditions,
    )
    assert pivot_applied == ()
    assert pivot_status.attacker_state.board.get("actor-active").special_conditions == set()
    assert_conserved(actor_initial, pivot_status.attacker_state.ledger)

    # Push Down damage is resolved before its forced switch. A 50-HP Active
    # can therefore move to the Bench at 0 HP and be discarded from there in
    # the later KO phase, with no replacement promotion needed at KO disposal.
    _actor2_initial, actor2 = physical_side(
        "actor2", active_name="Persian", bench_names=("Pivot",),
    )
    defender_initial, fragile = physical_side(
        "fragile",
        active_name="Fragile Target",
        bench_names=("Bench A", "Bench B"),
        active_conditions=frozenset({"Poisoned"}),
    )
    push_source, push_replay = copied_replay(
        push_down,
        fragile,
        hp_by_pokemon_id={
            "fragile-active": 50,
            "fragile-bench-0": 100,
            "fragile-bench-1": 100,
        },
    )
    assert push_source.fixed_damage == 50
    assert push_replay.knocked_out_ids == ("fragile-active",)

    pushed = apply_physical_attack_position_effect(
        push_replay,
        actor2,
        push_down,
        attacking_pokemon_id="actor2-active",
        chosen_pokemon_id="fragile-bench-0",
    )
    assert pushed.moved
    pushed_board = pushed.updated_copy_resolution.state.board
    assert pushed_board.active_id == "fragile-bench-0"
    assert pushed_board.get("fragile-active").damage_counters == 5
    assert pushed_board.get("fragile-active").special_conditions == frozenset()

    pending = prepare_physical_knockouts(pushed.updated_copy_resolution)
    assert pending is not None
    removed_from_bench = discard_pending_knock_out_batch(pending)
    assert removed_from_bench is not None
    assert removed_from_bench.board.active_id == "fragile-bench-0"
    assert "fragile-active" not in {
        pokemon.pokemon_id for pokemon in removed_from_bench.board.pokemon
    }
    assert_conserved(defender_initial, removed_from_bench.ledger)

    blocked_push = apply_physical_attack_position_effect(
        push_replay,
        actor2,
        push_down,
        attacking_pokemon_id="actor2-active",
        chosen_pokemon_id="fragile-bench-0",
        blocked_defender_effect_target_ids=frozenset({"fragile-active"}),
    )
    assert not blocked_push.moved
    blocked_pending = prepare_physical_knockouts(
        blocked_push.updated_copy_resolution
    )
    assert blocked_pending is not None
    assert discard_pending_knock_out_batch(blocked_pending) is None
    promoted_after_ko = discard_pending_knock_out_batch(
        blocked_pending,
        promote_id="fragile-bench-0",
    )
    assert promoted_after_ko is not None
    assert promoted_after_ko.board.active_id == "fragile-bench-0"

    # Follow Me is a targeted-gust effect on the selected Benched Pokemon,
    # not on the old Active. Physical immunity therefore blocks opposite
    # objects from Push Down despite the same final switch topology.
    _actor3_initial, actor3 = physical_side(
        "actor3", active_name="Persian", bench_names=("Pivot",),
    )
    _target3_initial, target3 = physical_side(
        "gust",
        active_name="Wall",
        bench_names=("Target A", "Target B"),
    )
    _follow_source, follow_replay = copied_replay(
        follow_me,
        target3,
        hp_by_pokemon_id={
            "gust-active": 100,
            "gust-bench-0": 100,
            "gust-bench-1": 100,
        },
    )
    blocked_gust = apply_physical_attack_position_effect(
        follow_replay,
        actor3,
        follow_me,
        attacking_pokemon_id="actor3-active",
        chosen_pokemon_id="gust-bench-1",
        blocked_defender_effect_target_ids=frozenset({"gust-bench-1"}),
    )
    assert not blocked_gust.moved
    old_active_block_only = apply_physical_attack_position_effect(
        follow_replay,
        actor3,
        follow_me,
        attacking_pokemon_id="actor3-active",
        chosen_pokemon_id="gust-bench-1",
        blocked_defender_effect_target_ids=frozenset({"gust-active"}),
    )
    assert old_active_block_only.moved
    assert (
        old_active_block_only.updated_copy_resolution.state.board.active_id
        == "gust-bench-1"
    )

    print({
        "exact_position_attack_indices": {
            "Aqua Ring": aqua.attack_index,
            "Push Down": push_down.attack_index,
            "Follow Me": follow_me.attack_index,
        },
        "optional_self_switch_changes_reaction_targetability": {
            "stay_conditions": tuple(sorted(
                stayed_status.attacker_state.board.get("actor-active").special_conditions
            )),
            "pivot_conditions": tuple(sorted(
                pivot_status.attacker_state.board.get("actor-active").special_conditions
            )),
        },
        "zero_hp_active_switched_before_ko": (
            pushed_board.active_id,
            removed_from_bench.board.active_id,
        ),
        "forced_vs_targeted_immunity_geometry": (
            blocked_push.moved,
            blocked_gust.moved,
            old_active_block_only.moved,
        ),
        "physical_ledgers_conserved": True,
    })


if __name__ == "__main__":
    main()
