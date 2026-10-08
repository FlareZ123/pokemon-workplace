"""Reproduce physical Energy discard, return, and reattachment backlash."""

from __future__ import annotations

from dataclasses import replace
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
    AttachmentKind, BoardPokemon, PokemonCard, make_state, replace_pokemon,
)
from damage_calculation_kernel import AttackDamage, DamageContext
from identity_materialization import (
    IdentityLedger, assert_conserved, materialize, put_in_play_instance,
)
from lock_state_kernel import suppress_tool_effect
from multicopy_zone_state import ZoneCountState
from physical_copy_damage_reaction_bridge import (
    prepare_reacted_physical_knockouts,
    resolve_physical_copy_damage_reactions,
)
from physical_energy_backlash_reactions import (
    EnergyReactionKind, apply_physical_energy_backlash,
    eligible_printed_energy_backlash,
)
from stack_knockout_conservation import StackBoardMaterialState, attach_from_hand

HAUGHTY = "persian:haughty-order"
TIMELESS = "dialga:timeless-gx"
BODY = "body:timeless-gx"


def copy_timeless():
    attacks = {
        HAUGHTY: AttackDef(
            HAUGHTY, "Haughty Order",
            copy_selector=CopySelector("opponent_revealed"),
            pre_event="reveal_top_10", post_event="shuffle_revealed",
        ),
        TIMELESS: AttackDef(
            TIMELESS, "Timeless-GX", is_gx=True, effect_label=BODY,
        ),
    }
    return resolve_attack(
        actor_player="P1", actor_card_id="a-active-card",
        declared_attack_id=HAUGHTY, attacks=attacks,
        state=State(
            pokemon=(
                PokemonRef(
                    "revealed-dialga", "Dialga-GX", "P2", "revealed",
                    attacks=(TIMELESS,),
                ),
            ),
        ),
        choose=choose_exact((TIMELESS,)),
    )


def physical_player(
    prefix: str,
    active_name: str,
    *,
    energies: tuple[tuple[str, str], ...] = (),
    tool: str | None = None,
    bench: bool = True,
):
    names = (("active", active_name),) + (
        (("bench", f"{prefix} backup"),) if bench else ()
    )
    counts = {
        (f"{prefix}-{role}-class", "hand"): 1
        for role, _ in names
    }
    for instance_id, _ in energies:
        counts[(f"{prefix}-{instance_id}-class", "hand")] = 1
    if tool is not None:
        counts[(f"{prefix}-tool-class", "hand")] = 1

    initial = IdentityLedger(ZoneCountState.from_mapping(counts))
    ledger = initial
    board_rows = []
    for role, name in names:
        iid = f"{prefix}-{role}-card"
        ledger = materialize(
            ledger, card_class=f"{prefix}-{role}-class",
            card_name=name, source_zone="hand", instance_id=iid,
        )
        ledger = put_in_play_instance(ledger, iid, f"{prefix}-{role}")
        board_rows.append(
            BoardPokemon(
                f"{prefix}-{role}", (PokemonCard(iid, name),),
                retreat_cost=1,
            )
        )

    state = StackBoardMaterialState(
        ledger,
        make_state(board_rows, active_id=f"{prefix}-active"),
    )
    for iid, name in energies:
        result = attach_from_hand(
            state, pokemon_id=f"{prefix}-active",
            card_class=f"{prefix}-{iid}-class", instance_id=iid,
            card_name=name, kind=AttachmentKind.ENERGY,
            retreat_units=1,
        )
        assert result is not None
        state = result
    if tool is not None:
        result = attach_from_hand(
            state, pokemon_id=f"{prefix}-active",
            card_class=f"{prefix}-tool-class", instance_id=f"{prefix}-tool",
            card_name=tool, kind=AttachmentKind.TOOL,
        )
        assert result is not None
        state = result

    assert_conserved(initial, state.ledger)
    return initial, state


def ready_reaction(
    defender_name: str,
    *,
    tool: str | None = None,
    defender_hp: int = 180,
    attacker_bench: bool = True,
):
    original_a, a = physical_player(
        "a", "Persian", bench=attacker_bench,
        energies=(
            ("a-fire-energy", "Fire Energy"),
            ("a-water-energy", "Water Energy"),
        ),
    )
    original_b, b = physical_player(
        "b", defender_name, tool=tool,
    )
    replay = replay_copy_attack_physical_board(
        copy_timeless(), b,
        event_programs={
            BODY: PhysicalBoardEventProgram(
                "b-active", DamageContext(attack=AttackDamage(150)),
            ),
        },
        hp_by_pokemon_id={"b-active": defender_hp, "b-bench": 100},
    )
    base = resolve_physical_copy_damage_reactions(
        replay, a, body_event=BODY, damaged_pokemon_id="b-active",
        attacking_pokemon_id="a-active", reactions=(),
        attacker_hp_by_pokemon_id={"a-active": 250, "a-bench": 100} if attacker_bench else {"a-active": 250},
        defender_hp_by_pokemon_id={"b-active": defender_hp, "b-bench": 100},
    )
    return original_a, original_b, replay, base


def compiled(replay, *, card: str, tool_instance: str | None = None, enabled: bool = True):
    result = eligible_printed_energy_backlash(
        replay, resources=ROOT / "resources",
        body_event=BODY, damaged_pokemon_id="b-active",
        source_print_id=card, source_instance_id=tool_instance,
        ability_is_enabled=enabled,
        from_opponents_pokemon=True,
    )
    assert len(result) == 1
    return result[0]


def test_discard_ability_before_ko():
    original_a, original_b, replay, base = ready_reaction(
        "Turtonator", defender_hp=120,
    )
    assert replay.knocked_out_ids == ("b-active",)
    reaction = compiled(replay, card="me3-17")
    assert reaction.kind is EnergyReactionKind.DISCARD
    resolved, outcome = apply_physical_energy_backlash(
        base, reaction, energy_instance_id="a-fire-energy",
    )
    assert outcome.applied
    assert resolved.attacker_state.ledger.exchangeable.count(
        "a-a-fire-energy-class", "discard",
    ) == 1
    assert tuple(
        item.card_id
        for item in resolved.attacker_state.board.get("a-active").attachments
    ) == ("a-water-energy",)
    assert_conserved(original_a, resolved.attacker_state.ledger)
    assert_conserved(original_b, resolved.defender_state.ledger)
    pa, pb = prepare_reacted_physical_knockouts(resolved)
    assert pa is None and pb is not None
    assert pb.state.board.get("b-active").name == "Turtonator"

    assert eligible_printed_energy_backlash(
        replay, resources=ROOT / "resources",
        body_event=BODY, damaged_pokemon_id="b-active",
        source_print_id="me3-17", source_instance_id=None,
        ability_is_enabled=False, from_opponents_pokemon=True,
    ) == ()
    _, _, klawf_replay, _ = ready_reaction(
        "Klawf ex", defender_hp=220,
    )
    assert compiled(
        klawf_replay, card="sv3-120",
    ).kind is EnergyReactionKind.DISCARD


def test_return_to_owners_hand_and_source_tool_binding():
    original_a, original_b, replay, base = ready_reaction(
        "Turtonator", tool="Rugged Helmet", defender_hp=120,
    )
    reaction = compiled(
        replay, card="swsh6-152", tool_instance="b-tool",
    )
    assert reaction.kind is EnergyReactionKind.RETURN_TO_HAND
    returned, outcome = apply_physical_energy_backlash(
        base, reaction, energy_instance_id="a-fire-energy",
    )
    assert outcome.applied
    assert returned.attacker_state.ledger.exchangeable.count(
        "a-a-fire-energy-class", "hand",
    ) == 1
    assert tuple(
        item.card_id
        for item in returned.attacker_state.board.get("a-active").attachments
    ) == ("a-water-energy",)
    assert returned.defender_state.board.get("b-active").attachments[0].card_id == "b-tool"
    _, pending_b = prepare_reacted_physical_knockouts(returned)
    assert pending_b is not None
    assert pending_b.state.board.get("b-active").attachments[0].card_id == "b-tool"
    assert_conserved(original_a, returned.attacker_state.ledger)
    assert_conserved(original_b, returned.defender_state.ledger)

    # Both the normal and the alternate-art print use the same source text.
    assert compiled(
        replay, card="swsh6-228", tool_instance="b-tool",
    ).kind is EnergyReactionKind.RETURN_TO_HAND

    # Jamming Tower-style suppression leaves the physical Tool attached
    # while its effect becomes unavailable.
    holder = replay.state.board.get("b-active")
    disabled_holder = replace(
        holder, combat=suppress_tool_effect(holder.combat),
    )
    suppressed = replace(
        replay,
        state=StackBoardMaterialState(
            replay.state.ledger,
            replace_pokemon(replay.state.board, disabled_holder),
        ),
    )
    assert eligible_printed_energy_backlash(
        suppressed, resources=ROOT / "resources",
        body_event=BODY, damaged_pokemon_id="b-active",
        source_print_id="swsh6-152", source_instance_id="b-tool",
        ability_is_enabled=True, from_opponents_pokemon=True,
    ) == ()


def test_move_energy_to_bench_and_missing_destination():
    original_a, _, replay, base = ready_reaction(
        "Turtonator", tool="Handheld Fan",
    )
    reaction = compiled(
        replay, card="sv6-150", tool_instance="b-tool",
    )
    assert reaction.kind is EnergyReactionKind.MOVE_TO_BENCH
    updated, outcome = apply_physical_energy_backlash(
        base, reaction,
        energy_instance_id="a-fire-energy",
        destination_pokemon_id="a-bench",
    )
    assert outcome.applied
    assert updated.attacker_state.ledger.instance("a-fire-energy").attached_to == "a-bench"
    assert tuple(
        item.card_id
        for item in updated.attacker_state.board.get("a-active").attachments
    ) == ("a-water-energy",)
    assert tuple(
        item.card_id
        for item in updated.attacker_state.board.get("a-bench").attachments
    ) == ("a-fire-energy",)
    assert_conserved(original_a, updated.attacker_state.ledger)

    _, _, replay_without, no_bench = ready_reaction(
        "Turtonator", tool="Handheld Fan",
        attacker_bench=False,
    )
    no_bench_reaction = compiled(
        replay_without, card="sv6-150", tool_instance="b-tool",
    )
    no_change, outcome = apply_physical_energy_backlash(
        no_bench, no_bench_reaction,
        energy_instance_id="a-fire-energy",
    )
    assert not outcome.applied
    assert outcome.reason == "no_destination_bench"
    assert no_change is no_bench

    try:
        apply_physical_energy_backlash(
            base, reaction,
            energy_instance_id="a-fire-energy",
            destination_pokemon_id="b-bench",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("opponent Bench accepted as an Energy destination")


def test_missing_energy_and_ability_eligible_attacker_movement():
    _, _, replay, base = ready_reaction("Turtonator")
    reaction = compiled(replay, card="me3-17")
    first, _ = apply_physical_energy_backlash(
        base, reaction, energy_instance_id="a-fire-energy",
    )
    second, _ = apply_physical_energy_backlash(
        first, reaction, energy_instance_id="a-water-energy",
    )
    unchanged, outcome = apply_physical_energy_backlash(
        second, reaction, energy_instance_id=None,
    )
    assert not outcome.applied
    assert unchanged is second
    assert outcome.reason == "no_eligible_damage_or_energy"

    # The original Attacking Pokémon may move to the Bench after damage.
    # The source chooses Energy from that Pokémon's identity, regardless of
    # who is currently in the Active Spot.
    board = base.attacker_state.board
    assert board is not None
    moved = StackBoardMaterialState(
        base.attacker_state.ledger,
        replace(board, active_id="a-bench"),
    )
    switched = replace(base, attacker_state=moved)
    result, outcome = apply_physical_energy_backlash(
        switched, reaction, energy_instance_id="a-fire-energy",
    )
    assert outcome.applied
    assert result.attacker_state.board.active_id == "a-bench"
    assert result.attacker_state.ledger.exchangeable.count(
        "a-a-fire-energy-class", "discard",
    ) == 1


def main():
    test_discard_ability_before_ko()
    test_return_to_owners_hand_and_source_tool_binding()
    test_move_energy_to_bench_and_missing_destination()
    test_missing_energy_and_ability_eligible_attacker_movement()
    print("physical Energy backlash source/identity conservation: PASS")


if __name__ == "__main__":
    main()
