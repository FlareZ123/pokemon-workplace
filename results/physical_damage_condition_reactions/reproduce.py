"""Reproduce physical post-damage condition Abilities and their suppression."""

from __future__ import annotations

from dataclasses import replace
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
from board_position_state import (
    BoardPokemon, PokemonCard, clear_for_bench, make_state,
)
from damage_calculation_kernel import AttackDamage, DamageContext
from identity_materialization import (
    IdentityLedger, assert_conserved, materialize, put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from physical_copy_damage_reaction_bridge import (
    prepare_reacted_physical_knockouts,
    resolve_physical_copy_damage_reactions,
)
from physical_damage_condition_reactions import (
    apply_physical_condition_reactions, eligible_printed_condition_reactions,
)
from special_condition_state import ConditionKind
from stack_knockout_conservation import StackBoardMaterialState

HAUGHTY = "persian:haughty-order"
TIMELESS = "dialga:timeless-gx"
BODY = "body:timeless-gx"


def copied_timeless():
    attacks = {
        HAUGHTY: AttackDef(
            HAUGHTY, "Haughty Order",
            copy_selector=CopySelector("opponent_revealed"),
            pre_event="reveal_top_10", post_event="shuffle_revealed",
        ),
        TIMELESS: AttackDef(
            TIMELESS, "Timeless-GX", is_gx=True,
            effect_label=BODY,
        ),
    }
    return resolve_attack(
        actor_player="P1", actor_card_id="a-active-card",
        declared_attack_id=HAUGHTY, attacks=attacks,
        state=State(
            pokemon=(
                PokemonRef(
                    "dialga-revealed", "Dialga-GX", "P2", "revealed",
                    attacks=(TIMELESS,),
                ),
            ),
        ),
        choose=choose_exact((TIMELESS,)),
    )


def make_player(
    prefix: str,
    stack_names: tuple[str, ...],
    *,
    attacker_conditions: tuple[str, ...] = (),
) -> tuple[IdentityLedger, StackBoardMaterialState]:
    card_classes = {
        (f"{prefix}-stack-{index}", "hand"): 1
        for index in range(len(stack_names))
    }
    card_classes[(f"{prefix}-bench-class", "hand")] = 1
    initial = IdentityLedger(ZoneCountState.from_mapping(card_classes))
    ledger = initial
    stack = []
    for index, name in enumerate(stack_names):
        instance = f"{prefix}-stack-card-{index}"
        ledger = materialize(
            ledger, card_class=f"{prefix}-stack-{index}",
            card_name=name, source_zone="hand",
            instance_id=instance,
        )
        ledger = put_in_play_instance(ledger, instance, f"{prefix}-active")
        stack.append(
            PokemonCard(
                instance, name,
                evolves_from=stack_names[index - 1] if index else None,
            )
        )
    ledger = materialize(
        ledger, card_class=f"{prefix}-bench-class",
        card_name=f"{prefix} backup", source_zone="hand",
        instance_id=f"{prefix}-bench-card",
    )
    ledger = put_in_play_instance(
        ledger, f"{prefix}-bench-card", f"{prefix}-bench",
    )
    board = make_state(
        (
            BoardPokemon(
                f"{prefix}-active", tuple(stack), retreat_cost=1,
                special_conditions=frozenset(attacker_conditions),
            ),
            BoardPokemon(
                f"{prefix}-bench",
                (PokemonCard(f"{prefix}-bench-card", f"{prefix} backup"),),
                retreat_cost=1,
            ),
        ),
        active_id=f"{prefix}-active",
    )
    state = StackBoardMaterialState(ledger, board)
    assert_conserved(initial, state.ledger)
    return initial, state


def attack_reaction(
    source_print_id: str,
    source_stack: tuple[str, ...],
    *,
    attacker_conditions: tuple[str, ...] = (),
):
    initial_a, a = make_player(
        "a", ("Persian",), attacker_conditions=attacker_conditions,
    )
    initial_b, b = make_player("b", source_stack)
    set_id = source_print_id.split("-")[0]
    set_cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    source_hp = int(next(
        card["hp"] for card in set_cards if card["id"] == source_print_id
    ))
    replay = replay_copy_attack_physical_board(
        copied_timeless(), b,
        event_programs={
            BODY: PhysicalBoardEventProgram(
                "b-active",
                DamageContext(attack=AttackDamage(150)),
            ),
        },
        hp_by_pokemon_id={"b-active": source_hp, "b-bench": 100},
    )
    conditions = eligible_printed_condition_reactions(
        replay, resources=ROOT / "resources",
        body_event=BODY, damaged_pokemon_id="b-active",
        defending_print_id=source_print_id,
        ability_is_enabled=True,
        from_opponents_pokemon=True,
    )
    base = resolve_physical_copy_damage_reactions(
        replay, a, body_event=BODY, damaged_pokemon_id="b-active",
        attacking_pokemon_id="a-active", reactions=(),
        attacker_hp_by_pokemon_id={"a-active": 120, "a-bench": 100},
        defender_hp_by_pokemon_id={"b-active": source_hp, "b-bench": 100},
    )
    enhanced, applied = apply_physical_condition_reactions(base, conditions)
    assert_conserved(initial_a, enhanced.attacker_state.ledger)
    assert_conserved(initial_b, enhanced.defender_state.ledger)
    return replay, base, enhanced, applied


def test_poison_point_even_when_knocked_out():
    initial_a, a = make_player("a", ("Persian",))
    initial_b, b = make_player("b", ("Roselia",))
    replay = replay_copy_attack_physical_board(
        copied_timeless(), b,
        event_programs={
            BODY: PhysicalBoardEventProgram(
                "b-active", DamageContext(attack=AttackDamage(150)),
            ),
        },
        hp_by_pokemon_id={"b-active": 60, "b-bench": 100},
    )
    assert replay.knocked_out_ids == ("b-active",)

    conditions = eligible_printed_condition_reactions(
        replay, resources=ROOT / "resources", body_event=BODY,
        damaged_pokemon_id="b-active", defending_print_id="sv5-8",
        ability_is_enabled=True, from_opponents_pokemon=True,
    )
    assert conditions == (ConditionKind.POISONED,)
    base = resolve_physical_copy_damage_reactions(
        replay, a, body_event=BODY, damaged_pokemon_id="b-active",
        attacking_pokemon_id="a-active", reactions=(),
        attacker_hp_by_pokemon_id={"a-active": 120, "a-bench": 100},
        defender_hp_by_pokemon_id={"b-active": 60, "b-bench": 100},
    )
    enhanced, applied = apply_physical_condition_reactions(base, conditions)
    assert applied == (ConditionKind.POISONED,)
    assert enhanced.attacker_state.board.get("a-active").special_conditions == frozenset({"Poisoned"})
    assert enhanced.defender_knocked_out_ids == ("b-active",)
    pa, pb = prepare_reacted_physical_knockouts(enhanced)
    assert pa is None and pb is not None
    assert pb.state.board.get("b-active").name == "Roselia"
    assert_conserved(initial_a, enhanced.attacker_state.ledger)
    assert_conserved(initial_b, enhanced.defender_state.ledger)

    for ability_enabled, opposing, expected in (
        (False, True, ()),
        (True, False, ()),
        (True, True, (ConditionKind.POISONED,)),
    ):
        actual = eligible_printed_condition_reactions(
            replay, resources=ROOT / "resources", body_event=BODY,
            damaged_pokemon_id="b-active", defending_print_id="sv5-8",
            ability_is_enabled=ability_enabled,
            from_opponents_pokemon=opposing,
        )
        assert actual == expected

    try:
        eligible_printed_condition_reactions(
            replay, resources=ROOT / "resources", body_event=BODY,
            damaged_pokemon_id="b-active", defending_print_id="sv6-123",
            ability_is_enabled=True, from_opponents_pokemon=True,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("mismatched bound print accepted")


def test_burn_poison_coexist_and_confusion():
    _, _, enhanced, applied = attack_reaction(
        "sv6-123", ("Heatran",),
        attacker_conditions=("Poisoned",),
    )
    assert applied == (ConditionKind.BURNED,)
    assert enhanced.attacker_state.board.get("a-active").special_conditions == frozenset({
        "Poisoned", "Burned",
    })

    _, _, confused, applied = attack_reaction(
        "swsh35-20", ("Hatenna", "Hattrem", "Hatterene"),
        attacker_conditions=("Poisoned", "Burned"),
    )
    assert applied == (ConditionKind.CONFUSED,)
    assert confused.attacker_state.board.get("a-active").special_conditions == frozenset({
        "Poisoned", "Burned", "Confused",
    })

    # Existing regular condition state is normalized through the shared
    # typed condition kernel: rotating conditions replace each other.
    adjusted, applied = apply_physical_condition_reactions(
        confused, (ConditionKind.ASLEEP, ConditionKind.CONFUSED),
    )
    assert applied == (ConditionKind.ASLEEP, ConditionKind.CONFUSED)
    assert adjusted.attacker_state.board.get("a-active").special_conditions == frozenset({
        "Poisoned", "Burned", "Confused",
    })


def test_prevented_damage_and_benched_actor():
    _, a = make_player("a", ("Persian",))
    _, b = make_player("b", ("Roselia",))
    replay = replay_copy_attack_physical_board(
        copied_timeless(), b,
        event_programs={
            BODY: PhysicalBoardEventProgram(
                "b-active",
                DamageContext(
                    attack=AttackDamage(150), prevent_all_damage=True,
                ),
            ),
        },
        hp_by_pokemon_id={"b-active": 60, "b-bench": 100},
    )
    assert eligible_printed_condition_reactions(
        replay, resources=ROOT / "resources", body_event=BODY,
        damaged_pokemon_id="b-active", defending_print_id="sv5-8",
        ability_is_enabled=True, from_opponents_pokemon=True,
    ) == ()

    unprevented = replay_copy_attack_physical_board(
        copied_timeless(), b,
        event_programs={
            BODY: PhysicalBoardEventProgram(
                "b-active", DamageContext(attack=AttackDamage(150)),
            ),
        },
        hp_by_pokemon_id={"b-active": 60, "b-bench": 100},
    )
    conditions = eligible_printed_condition_reactions(
        unprevented, resources=ROOT / "resources", body_event=BODY,
        damaged_pokemon_id="b-active", defending_print_id="sv5-8",
        ability_is_enabled=True, from_opponents_pokemon=True,
    )
    assert a.board is not None
    moved_board = replace(
        a.board, active_id="a-bench",
        pokemon=(
            clear_for_bench(a.board.get("a-active")),
            a.board.get("a-bench"),
        ),
    )
    moved = StackBoardMaterialState(a.ledger, moved_board)
    base = resolve_physical_copy_damage_reactions(
        unprevented, moved, body_event=BODY, damaged_pokemon_id="b-active",
        attacking_pokemon_id="a-active", reactions=(),
        attacker_hp_by_pokemon_id={"a-active": 120, "a-bench": 100},
        defender_hp_by_pokemon_id={"b-active": 60, "b-bench": 100},
    )
    result, applied = apply_physical_condition_reactions(base, conditions)
    assert applied == ()
    assert result.attacker_state.board.active_id == "a-bench"
    assert result.attacker_state.board.get("a-active").special_conditions == frozenset()
    assert result.attacker_state.board.get("a-bench").special_conditions == frozenset()


def main():
    test_poison_point_even_when_knocked_out()
    test_burn_poison_coexist_and_confusion()
    test_prevented_damage_and_benched_actor()
    print("physical damage-triggered Special Conditions: PASS")


if __name__ == "__main__":
    main()
